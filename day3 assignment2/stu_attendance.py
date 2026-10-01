import streamlit as st
import pandas as pd
from datetime import date

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Student Attendance Tracker",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }

    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    }

    h1 {
        color: #1f4e79;
    }

    h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "students" not in st.session_state:
    st.session_state.students = []

if "attendance" not in st.session_state:
    st.session_state.attendance = []

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🎓 Student Attendance Tracker")
st.write("Manage students, record attendance, and calculate attendance percentages automatically.")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Dashboard",
        "👨‍🎓 Student Management",
        "📝 Mark Attendance",
        "📊 Attendance Reports"
    ]
)

# ==================================================
# DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    st.header("📊 Attendance Dashboard")

    total_students = len(st.session_state.students)
    total_classes = len(st.session_state.attendance)

    present_count = sum(
        1 for record in st.session_state.attendance
        if record["Status"] == "Present"
    )

    absent_count = sum(
        1 for record in st.session_state.attendance
        if record["Status"] == "Absent"
    )

    if total_classes > 0:
        overall_percentage = (present_count / total_classes) * 100
    else:
        overall_percentage = 0

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👨‍🎓 Total Students", total_students)
    col2.metric("📚 Total Classes", total_classes)
    col3.metric("✅ Present", present_count)
    col4.metric("📈 Overall Attendance", f"{overall_percentage:.2f}%")

    st.divider()

    # Attendance summary
    st.subheader("📋 Attendance Summary")

    if total_classes == 0:
        st.info("No attendance records available yet.")
    else:
        st.write(f"**Present:** {present_count}")
        st.write(f"**Absent:** {absent_count}")

        st.progress(int(overall_percentage))

        if overall_percentage >= 75:
            st.success("🟢 Overall attendance is good.")
        elif overall_percentage >= 65:
            st.warning("🟡 Overall attendance needs attention.")
        else:
            st.error("🔴 Overall attendance is low.")

# ==================================================
# STUDENT MANAGEMENT
# ==================================================

elif page == "👨‍🎓 Student Management":

    st.header("👨‍🎓 Student Management")

    # ------------------------------
    # ADD STUDENT
    # ------------------------------

    st.subheader("➕ Add Student")

    with st.form("student_form"):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Student Name")
            roll_no = st.text_input("Roll Number")

        with col2:
            branch = st.selectbox(
                "Branch",
                ["CSE", "ECE", "EEE", "MECH", "CIVIL", "IT"]
            )

            year = st.selectbox(
                "Year",
                ["1st Year", "2nd Year", "3rd Year", "4th Year"]
            )

        section = st.selectbox(
            "Section",
            ["A", "B", "C", "D"]
        )

        submit_student = st.form_submit_button("➕ Add Student")

    if submit_student:

        if name.strip() == "" or roll_no.strip() == "":
            st.error("❌ Please enter student name and roll number.")

        elif any(
            student["Roll No"] == roll_no
            for student in st.session_state.students
        ):
            st.warning("⚠️ Roll number already exists.")

        else:

            new_student = {
                "Roll No": roll_no,
                "Name": name,
                "Branch": branch,
                "Year": year,
                "Section": section
            }

            st.session_state.students.append(new_student)

            st.success("✅ Student added successfully!")

    # ------------------------------
    # DISPLAY STUDENTS
    # ------------------------------

    st.divider()

    st.subheader("📋 Student List")

    if len(st.session_state.students) == 0:

        st.info("No students added yet.")

    else:

        student_df = pd.DataFrame(st.session_state.students)

        st.dataframe(
            student_df,
            use_container_width=True,
            hide_index=True
        )

        # ------------------------------
        # DELETE STUDENT
        # ------------------------------

        st.subheader("🗑️ Delete Student")

        roll_numbers = [
            student["Roll No"]
            for student in st.session_state.students
        ]

        delete_roll = st.selectbox(
            "Select Roll Number",
            roll_numbers
        )

        if st.button("🗑️ Delete Student"):

            st.session_state.students = [
                student
                for student in st.session_state.students
                if student["Roll No"] != delete_roll
            ]

            # Also delete attendance records
            st.session_state.attendance = [
                record
                for record in st.session_state.attendance
                if record["Roll No"] != delete_roll
            ]

            st.success("✅ Student deleted successfully!")

# ==================================================
# MARK ATTENDANCE
# ==================================================

elif page == "📝 Mark Attendance":

    st.header("📝 Mark Attendance")

    if len(st.session_state.students) == 0:

        st.warning("⚠️ Please add students first.")

    else:

        student_options = [
            f"{student['Roll No']} - {student['Name']}"
            for student in st.session_state.students
        ]

        with st.form("attendance_form"):

            selected_student = st.selectbox(
                "Select Student",
                student_options
            )

            subject = st.selectbox(
                "Subject",
                [
                    "DBMS",
                    "Operating Systems",
                    "Data Structures",
                    "Python",
                    "Java",
                    "Computer Networks",
                    "Full Stack Development"
                ]
            )

            attendance_date = st.date_input(
                "Attendance Date",
                value=date.today()
            )

            status = st.radio(
                "Attendance Status",
                ["Present", "Absent"],
                horizontal=True
            )

            submit_attendance = st.form_submit_button(
                "📝 Submit Attendance"
            )

        if submit_attendance:

            roll_no = selected_student.split(" - ")[0]

            # Check duplicate attendance
            duplicate = any(
                record["Roll No"] == roll_no
                and record["Subject"] == subject
                and record["Date"] == str(attendance_date)
                for record in st.session_state.attendance
            )

            if duplicate:

                st.warning(
                    "⚠️ Attendance for this student, subject and date already exists."
                )

            else:

                new_record = {
                    "Roll No": roll_no,
                    "Student": selected_student.split(" - ")[1],
                    "Date": str(attendance_date),
                    "Subject": subject,
                    "Status": status
                }

                st.session_state.attendance.append(new_record)

                st.success("✅ Attendance recorded successfully!")

# ==================================================
# ATTENDANCE REPORTS
# ==================================================

elif page == "📊 Attendance Reports":

    st.header("📊 Attendance Reports")

    if len(st.session_state.students) == 0:

        st.info("No students available.")

    else:

        # ------------------------------
        # STUDENT ATTENDANCE PERCENTAGE
        # ------------------------------

        st.subheader("📈 Individual Attendance")

        selected_roll = st.selectbox(
            "Select Student",
            [
                student["Roll No"]
                for student in st.session_state.students
            ]
        )

        selected_student = next(
            student
            for student in st.session_state.students
            if student["Roll No"] == selected_roll
        )

        student_records = [
            record
            for record in st.session_state.attendance
            if record["Roll No"] == selected_roll
        ]

        total = len(student_records)

        present = sum(
            1
            for record in student_records
            if record["Status"] == "Present"
        )

        absent = sum(
            1
            for record in student_records
            if record["Status"] == "Absent"
        )

        if total > 0:
            percentage = (present / total) * 100
        else:
            percentage = 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Classes", total)
        col2.metric("Present", present)
        col3.metric("Absent", absent)

        st.metric(
            "Attendance Percentage",
            f"{percentage:.2f}%"
        )

        st.progress(int(percentage))

        if percentage >= 75:

            st.success(
                f"🟢 {selected_student['Name']} has good attendance."
            )

        elif percentage >= 65:

            st.warning(
                f"🟡 {selected_student['Name']} needs to improve attendance."
            )

        else:

            st.error(
                f"🔴 {selected_student['Name']} has low attendance."
            )

        # ------------------------------
        # ATTENDANCE RECORDS
        # ------------------------------

        st.divider()

        st.subheader("📋 Attendance Records")

        if len(student_records) == 0:

            st.info("No attendance records for this student.")

        else:

            records_df = pd.DataFrame(student_records)

            st.dataframe(
                records_df,
                use_container_width=True,
                hide_index=True
            )

    # ------------------------------
    # ALL ATTENDANCE
    # ------------------------------

    st.divider()

    st.subheader("📚 All Attendance Records")

    if len(st.session_state.attendance) == 0:

        st.info("No attendance records available.")

    else:

        attendance_df = pd.DataFrame(
            st.session_state.attendance
        )

        # Filter
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "Present", "Absent"]
        )

        if filter_status != "All":

            filtered_df = attendance_df[
                attendance_df["Status"] == filter_status
            ]

        else:

            filtered_df = attendance_df

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        # ------------------------------
        # DELETE ATTENDANCE
        # ------------------------------

        st.subheader("🗑️ Delete Attendance Record")

        record_numbers = list(
            range(len(st.session_state.attendance))
        )

        selected_record = st.selectbox(
            "Select Record Number",
            record_numbers
        )

        if st.button("🗑️ Delete Attendance"):

            st.session_state.attendance.pop(
                selected_record
            )

            st.success(
                "✅ Attendance record deleted successfully!"
            )