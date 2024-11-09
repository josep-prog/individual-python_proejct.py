#!/usr/bin/env python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate  # Ensure tabulate module is installed

class Assignment:
    def __init__(self, name, score, weight, type):
        self.name = name
        self.score = score
        self.weight = weight
        self.type = type  # 'Formative' or 'Summative'

    def get_weighted_score(self):
        return self.score * self.weight / 100


class Course:
    def __init__(self, name, total_sessions):
        self.name = name
        self.assignments = []  # A list of assignments
        self.attendance = []  # Track attendance as a list of tuples (date, status)
        self.total_sessions = total_sessions  # Total mandatory sessions in the course

    def add_assignment(self, assignment):
        self.assignments.append(assignment)

    def mark_attendance(self, date, status):
        """Mark attendance for a specific session."""
        self.attendance.append((date, status))

    def calculate_attendance(self):
        """Calculate attendance percentage."""
        total_present = sum(1 for _, status in self.attendance if status == 'Present')
        return (total_present / self.total_sessions) * 100

    def calculate_group_score(self, group_type):
        total_weight = 0
        total_weighted_score = 0
        for assignment in self.assignments:
            if assignment.type == group_type:
                total_weight += assignment.weight
                total_weighted_score += assignment.get_weighted_score()
        return total_weight, total_weighted_score

    def check_progression(self):
        formative_weight, formative_score = self.calculate_group_score('Formative')
        summative_weight, summative_score = self.calculate_group_score('Summative')

        formative_total = formative_score / formative_weight * 100 if formative_weight else 0
        summative_total = summative_score / summative_weight * 100 if summative_weight else 0

        pass_formative = formative_total >= 30
        pass_summative = summative_total >= 20

        passed = pass_formative and pass_summative
        return passed, formative_total, summative_total

    def get_resubmission_candidates(self):
        return [assignment.name for assignment in self.assignments if assignment.score < 50 and assignment.type == 'Formative']

    def generate_transcript(self, sort_order="ascending"):
        # Sort the assignments by score in the desired order
        sorted_assignments = sorted(self.assignments, key=lambda x: x.score, reverse=(sort_order == "descending"))
        return sorted_assignments


class Student:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.courses = []

    def add_course(self, course):
        self.courses.append(course)

    def calculate_gpa(self):
        total_weighted_score = 0
        total_weight = 0

        for course in self.courses:
            for assignment in course.assignments:
                total_weighted_score += assignment.get_weighted_score()
                total_weight += assignment.weight

        return (total_weighted_score / total_weight) * 100 if total_weight else 0

    def generate_report(self, sort_order="ascending"):
        report = f"Report for {self.name} ({self.email})\n"
        report += "=" * 40 + "\n"

        # Track overall data for GPA
        overall_score = 0
        total_weight = 0

        table_data = []

        for course in self.courses:
            # Check course progression (pass/fail)
            passed, formative_total, summative_total = course.check_progression()
            resubmissions = course.get_resubmission_candidates()
            attendance_percentage = course.calculate_attendance()

            # Collecting course summary
            report += f"\nCourse: {course.name}\n"
            report += f"Formative Group Total: {formative_total:.2f}%\n"
            report += f"Summative Group Total: {summative_total:.2f}%\n"
            report += "Passed: " + ("Yes" if passed else "No") + "\n"

            # Handle resubmission eligibility
            if resubmissions:
                report += f"Eligible for Resubmission: {', '.join(resubmissions)}\n"
            else:
                report += "No Resubmissions Needed.\n"

            # Attendance report
            report += f"Attendance: {attendance_percentage:.2f}%\n"
            if attendance_percentage < 75:
                report += "Warning: Attendance is below 75%. The student should attend more classes.\n"
            else:
                report += "Attendance is satisfactory.\n"

            # Generate transcript for the course
            report += "\nTranscript Breakdown:\n"
            report += tabulate([[assignment.name, assignment.type, f"{assignment.score}%", f"{assignment.weight}%"] for assignment in course.generate_transcript(sort_order)], 
                               headers=["Assignment", "Type", "Score (%)", "Weight (%)"], tablefmt="grid")
            report += "\n" + "-" * 60 + "\n"

            # Collecting data for overall GPA calculation
            for assignment in course.assignments:
                table_data.append([course.name, assignment.name, f"{assignment.score}%", f"{assignment.weight}%", f"{assignment.get_weighted_score():.2f}%"])

        # Overall GPA
        gpa = self.calculate_gpa()
        report += f"\nOverall GPA: {gpa:.2f}%\n"
        report += "=" * 40 + "\n"

        # Generate final report table
        report += "\nDetailed Report:\n"
        report += tabulate(table_data, headers=["Course", "Assignment", "Score", "Weight", "Weighted Score"], tablefmt="grid")
        
        return report

    def send_report_to_parent(self, parent_email, sender_email, app_password, sort_order="ascending"):
        report = self.generate_report(sort_order)

        # Send email logic (same as your current code, using SMTP)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = parent_email
        msg['Subject'] = f"Student Report for {self.name}"

        msg.attach(MIMEText(report, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, parent_email, msg.as_string())
            server.quit()
            print(f"Report sent to {parent_email}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")


# Example usage
student = Student("Joseph Nishimwe", "j.nishimwe@alustudent.com")

# Creating courses with Formative and Summative assignments
course_1 = Course("Introduction to Programming and Databases", total_sessions=7)
course_1.add_assignment(Assignment("Python - Hello, World", 100, 10, 'Formative'))
course_1.add_assignment(Assignment("Python - Inheritance", 40.59, 20, 'Formative'))
course_1.add_assignment(Assignment("Python - Data Structures", 100, 30, 'Summative'))
course_1.mark_attendance("Sep 16", "Present")
course_1.mark_attendance("Sep 17", "Present")
course_1.mark_attendance("Sep 18", "Present")
course_1.mark_attendance("Sep 19", "Present")
course_1.mark_attendance("Sep 20", "Present")
course_1.mark_attendance("Sep 21", "Present")
course_1.mark_attendance("Sep 22", "Present")  # Corrected attendance to 100% for all sessions

course_2 = Course("Self-Leadership and Team Dynamics", total_sessions=7)
course_2.add_assignment(Assignment("Enneagram Test", 80, 10, 'Formative'))
course_2.add_assignment(Assignment("Empathy Discussion Board", 65, 20, 'Formative'))
course_2.add_assignment(Assignment("Community Building Quiz", 90, 20, 'Summative'))

course_3 = Course("Introduction to IT Tools and Linux", total_sessions=10)  # Added new course
course_3.add_assignment(Assignment("Pre-reading Sunday 1", 90, 10, 'Formative'))
course_3.add_assignment(Assignment("Discussion Board", 100, 20, 'Formative'))
course_3.add_assignment(Assignment("In Call Check-in Quiz 1", 65, 15, 'Formative'))
course_3.add_assignment(Assignment("Pre-reading Sunday 2", 83.33, 15, 'Formative'))
course_3.add_assignment(Assignment("General Quiz", 75.51, 15, 'Formative'))
course_3.add_assignment(Assignment("Shell, processes and signals", 100, 25, 'Summative'))

# Adding courses to student
student.add_course(course_1)
student.add_course(course_2)
student.add_course(course_3)

# Print report to terminal
print(student.generate_report(sort_order="ascending"))

# Optional: Send report to parent's email
parent_email = "josephnishimwe398@gmail.com"
sender_email = "j.nishimwe@alustudent.com"
app_password = "vhdu lbbe cixj islr"
student.send_report_to_parent(parent_email, sender_email, app_password)
