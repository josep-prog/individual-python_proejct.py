#!/usr/bin/env python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate  # Ensure tabulate module is installed

class Assignment:
    """
    Represents an assignment, either formative or summative, with its score, weight, and type.
    """
    def __init__(self, name, score, weight, type):
        self.name = name
        self.score = score
        self.weight = weight
        self.type = type  # 'Formative' or 'Summative'

    def get_weighted_score(self):
        """
        Calculate and return the weighted score of this assignment.
        Formula: weighted score = (score * weight) / 100
        """
        return self.score * self.weight / 100


class Course:
    """
    Represents a course that contains assignments and tracks attendance.
    Calculates overall scores and checks course progression.
    """
    def __init__(self, name, total_sessions):
        self.name = name
        self.assignments = []  # List to hold assignments for the course
        self.attendance = []  # Track attendance as a list of tuples (date, status)
        self.total_sessions = total_sessions  # Total mandatory sessions in the course

    def add_assignment(self, assignment):
        """
        Adds an assignment to the course.
        """
        self.assignments.append(assignment)

    def mark_attendance(self, date, status):
        """
        Marks the attendance for a specific session.
        """
        self.attendance.append((date, status))

    def calculate_attendance(self):
        """
        Calculate and return the percentage of attendance.
        """
        total_present = sum(1 for _, status in self.attendance if status == 'Present')
        return (total_present / self.total_sessions) * 100

    def calculate_group_score(self, group_type):
        """
        Calculate the total weighted score and weight for a specific group (Formative or Summative).
        """
        total_weight = 0
        total_weighted_score = 0
        for assignment in self.assignments:
            if assignment.type == group_type:
                total_weight += assignment.weight
                total_weighted_score += assignment.get_weighted_score()
        return total_weight, total_weighted_score

    def check_progression(self):
        """
        Check if the student passes the course based on the Formative and Summative group scores.
        Returns True if passed, otherwise False.
        """
        formative_weight, formative_score = self.calculate_group_score('Formative')
        summative_weight, summative_score = self.calculate_group_score('Summative')

        formative_total = formative_score / formative_weight * 100 if formative_weight else 0
        summative_total = summative_score / summative_weight * 100 if summative_weight else 0

        # Check if the student passed the Formative and Summative groups
        pass_formative = formative_total >= 30
        pass_summative = summative_total >= 20

        passed = pass_formative and pass_summative
        return passed, formative_total, summative_total

    def get_resubmission_candidates(self):
        """
        Get a list of assignments eligible for resubmission (Formative assignments with score < 50%).
        """
        return [assignment.name for assignment in self.assignments if assignment.score < 50 and assignment.type == 'Formative']

    def generate_transcript(self, sort_order="ascending"):
        """
        Generate and return a sorted list of assignments for the course.
        Sort the assignments based on score in ascending or descending order.
        """
        # Sort the assignments by score in the desired order
        sorted_assignments = sorted(self.assignments, key=lambda x: x.score, reverse=(sort_order == "descending"))
        return sorted_assignments


class Student:
    """
    Represents a student enrolled in multiple courses. Can calculate GPA, generate reports, and send them to parents.
    """
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.courses = []  # List of courses the student is enrolled in

    def add_course(self, course):
        """
        Adds a course to the student's list of courses.
        """
        self.courses.append(course)

    def calculate_gpa(self):
        """
        Calculate and return the student's GPA based on the weighted scores from all courses.
        """
        total_weighted_score = 0
        total_weight = 0

        # Loop through each course and assignment to calculate total weighted score and weight
        for course in self.courses:
            for assignment in course.assignments:
                total_weighted_score += assignment.get_weighted_score()
                total_weight += assignment.weight

        return (total_weighted_score / total_weight) * 100 if total_weight else 0

    def generate_report(self, sort_order="ascending"):
        """
        Generate and return a report for the student, including course progress, attendance, resubmission candidates, and transcript.
        """
        report = f"Report for {self.name} ({self.email})\n"
        report += "=" * 40 + "\n"

        overall_score = 0
        total_weight = 0
        table_data = []

        total_courses = len(self.courses)
        total_weighted_score_all_courses = 0
        total_weight_all_courses = 0

        for course in self.courses:
            passed, formative_total, summative_total = course.check_progression()
            resubmissions = course.get_resubmission_candidates()
            attendance_percentage = course.calculate_attendance()

            # Adding course summary to the report
            report += f"\nCourse: {course.name}\n"
            report += f"Formative Group Total: {formative_total:.2f}%\n"
            report += f"Summative Group Total: {summative_total:.2f}%\n"
            report += "Passed: " + ("Yes" if passed else "No") + "\n"

            if resubmissions:
                report += f"Eligible for Resubmission: {', '.join(resubmissions)}\n"
            else:
                report += "No Resubmissions Needed.\n"

            report += f"Attendance: {attendance_percentage:.2f}%\n"
            if attendance_percentage == 100:
                report += "Attendance is in good standing (100%).\n"
            else:
                report += "Warning: Attendance is below 100%. The student should attend more classes.\n"

            # Generate and display transcript breakdown for the course
            report += "\nTranscript Breakdown:\n"
            report += tabulate([[assignment.name, assignment.type, f"{assignment.score}%", f"{assignment.weight}%"] for assignment in course.generate_transcript(sort_order)], 
                               headers=["Assignment", "Type", "Score (%)", "Weight (%)"], tablefmt="grid")
            report += "\n" + "-" * 60 + "\n"

            for assignment in course.assignments:
                table_data.append([course.name, assignment.name, f"{assignment.score}%", f"{assignment.weight}%", f"{assignment.get_weighted_score():.2f}%"])
                total_weighted_score_all_courses += assignment.get_weighted_score()
                total_weight_all_courses += assignment.weight

        gpa = self.calculate_gpa()
        overall_avg_score = (total_weighted_score_all_courses / total_weight_all_courses) * 100 if total_weight_all_courses else 0
        report += f"\nOverall GPA: {gpa:.2f}%\n"
        report += f"Overall Average Score: {overall_avg_score:.2f}%\n"
        report += "=" * 40 + "\n"

        # Detailed report for all assignments
        report += "\nDetailed Report:\n"
        report += tabulate(table_data, headers=["Course", "Assignment", "Score", "Weight", "Weighted Score"], tablefmt="grid")
        
        return report

    def send_report_to_parent(self, parent_email, sender_email, app_password, sort_order="ascending"):
        """
        Sends the student's report to the parent's email using SMTP.
        """
        report = self.generate_report(sort_order)

        # Send email logic
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


# Example usage (Ensure to replace email with correct details)
student = Student("Joseph Nishimwe", "j.nishimwe@alustudent.com")

# Sample courses, assignments, and data
course1 = Course("Data Science 101", 30)
course1.add_assignment(Assignment("Assignment 1", 85, 15, "Formative"))
course1.add_assignment(Assignment("Midterm", 72, 20, "Summative"))
course1.add_assignment(Assignment("Final Exam", 90, 20, "Summative"))

student.add_course(course1)

# Generate report for a student, and sort transcript in ascending order
report = student.generate_report("ascending")
print(report)

# Example of sending report via email
# student.send_report_to_parent("parent_email@example.com", "your_email@example.com", "your_app_password", "ascending")
