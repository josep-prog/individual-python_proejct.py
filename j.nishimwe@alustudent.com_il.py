import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create a class for the assignment
class Assignment:
    def __init__(self, name, due_date, submitted_date, score, weight, assignment_type, status):
        self.name = name
        self.due_date = due_date
        self.submitted_date = submitted_date
        self.score = score
        self.weight = weight
        self.assignment_type = assignment_type
        self.status = status

    def calculate_weighted_score(self):
        return (self.score * self.weight) / 100

# Create a class for the student
class Student:
    def __init__(self, name, email, assignments):
        self.name = name
        self.email = email
        self.assignments = assignments

    def calculate_total_score(self):
        total_score = sum([assignment.calculate_weighted_score() for assignment in self.assignments])
        return total_score

    def calculate_gpa(self):
        total_score = self.calculate_total_score()
        gpa = (total_score / 100) * 4.0  # Assuming GPA is based on a 4.0 scale
        return round(gpa, 2)

    def check_progress(self):
        total_score = self.calculate_total_score()
        if total_score >= 50:
            return "Good standing"
        else:
            return "Needs improvement"

    def check_resubmission_eligibility(self):
        eligible_assignments = [assignment.name for assignment in self.assignments if assignment.score < 50]
        return eligible_assignments

    def generate_transcript(self):
        sorted_assignments = sorted(self.assignments, key=lambda x: x.score)
        transcript = "Assignment Breakdown (Sorted by Score):\n"
        for assignment in sorted_assignments:
            transcript += f"{assignment.name} | {assignment.assignment_type} | {assignment.score}% | Weight: {assignment.weight}%\n"
        return transcript

# Sending email function
def send_email_to_parent(student, parent_email, parent_name, subject, body):
    sender_email = "j.nishimwe@alustudent.com"
    sender_password = "obxl xknj hpue jqwb"
    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = parent_email
        message['Subject'] = subject

        body_content = f"Dear {parent_name},\n\n{body}\n\nRegards,\n{student.name}"
        message.attach(MIMEText(body_content, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, parent_email, message.as_string())

        print(f"Email sent to {parent_name} ({parent_email})")

    except Exception as e:
        print(f"Error sending email: {e}")

# Define student data
assignments = [
    Assignment("Python - Hello, World", "Sep 1", "Aug 30", 100, 10, "Formative", "Completed"),
    Assignment("Python - if/else, loops, functions", "Sep 5", "Sep 4", 100, 10, "Formative", "Completed"),
    Assignment("Python - Classes and Objects", "Sep 10", "Sep 8", 100, 15, "Formative", "Completed"),
    Assignment("Python - Inheritance", "Sep 15", "Sep 14", 40.59, 20, "Formative", "Completed"),
    Assignment("SQL - Introduction", "Sep 20", "Sep 19", 100, 10, "Summative", "Completed"),
    Assignment("Final Exam", "Nov 18", "", 0, 35, "Summative", "Incomplete")
]

student = Student("Joseph Nishimwe", "nishimwejoseph26@gmail.com", assignments)

# Generate report and email
progress = student.check_progress()
gpa = student.calculate_gpa()
resubmission_eligible = student.check_resubmission_eligibility()
transcript = student.generate_transcript()

# Preparing the email body
body = f"Student: {student.name}\nProgress: {progress}\nGPA: {gpa}\nResubmission Eligibility: {', '.join(resubmission_eligible) if resubmission_eligible else 'None'}\n\nTranscript:\n{transcript}"

# Send the report to the parent
send_email_to_parent(student, "nishimwejoseph26@gmail.com", "TUYIZERE JULES", "Student Progress Report", body)

# Displaying the report on the terminal
print("Student Progress Report")
print(f"Name: {student.name}")
print(f"Progress: {progress}")
print(f"GPA: {gpa}")
print(f"Resubmission Eligibility: {', '.join(resubmission_eligible) if resubmission_eligible else 'None'}")
print(f"\nTranscript:\n{transcript}")
