#!/usr/bin/env python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import time

# Global dictionary to store email confirmation data
confirmation_store = {}

# ============================
# Server Code for Tracking
# ============================

class RequestHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests to track email opens and button clicks."""

    def do_GET(self):
        """Handle GET requests for tracking and confirmation."""
        # Track email open (when an invisible image is loaded)
        if self.path.startswith("/track_open/"):
            email_id = self.path.split("/")[-1]
            logging.info(f"Email opened by {email_id}")

            # Send a 1x1 transparent image as an invisible tracking pixel
            self.send_response(204)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(b'')  # Empty body for tracking pixel
            return

        # Handle the confirmation when the parent clicks the confirmation button
        elif self.path.startswith("/confirm_view/"):
            email_id = self.path.split("/")[-1]
            confirmation_store[email_id] = time.time()  # Store confirmation time
            logging.info(f"Parent confirmed viewing for {email_id}")

            # Send a confirmation response to the parent
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Thank you for confirming that you've seen the report!")

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Page not found.")

# Run the HTTP server for tracking and confirmation
def run_server(host="0.0.0.0", port=8000):
    """Start the HTTP server to handle open and confirmation requests."""
    logging.basicConfig(level=logging.INFO)
    server_address = (host, port)
    httpd = HTTPServer(server_address, RequestHandler)
    logging.info(f"Server running on {host}:{port}")
    httpd.serve_forever()

# ============================
# Email Report Generation and Sending
# ============================

class Module:
    """Represents a module in a course with a name, score, and weight."""

    def __init__(self, name, score, weight):
        self.name = name
        self.score = score
        self.weight = weight

    def get_weighted_score(self):
        """Calculate the weighted score for the module."""
        return self.score * self.weight / 100

class Course:
    """Represents a course with a list of modules."""

    def __init__(self, name):
        self.name = name
        self.modules = []

    def add_module(self, module):
        """Add a module to the course."""
        self.modules.append(module)

    def get_total_weighted_score(self):
        """Calculate the total weighted score for the course."""
        return sum(module.get_weighted_score() for module in self.modules)

    def get_course_average(self):
        """Calculate the average score for the course."""
        total_score = sum(module.score for module in self.modules)
        return total_score / len(self.modules)

    def check_retakes(self):
        """Check if any modules require a retake based on the score."""
        return [module.name for module in self.modules if module.score < 50]

class Student:
    """Represents a student with a name, email, and a list of courses."""

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.courses = []

    def add_course(self, course):
        """Add a course to the student's list of courses."""
        self.courses.append(course)

    def calculate_gpa(self):
        """Calculate the student's GPA based on all courses."""
        total_weighted_score = sum(course.get_total_weighted_score() for course in self.courses)
        total_weight = sum(module.weight for course in self.courses for module in course.modules)
        return (total_weighted_score / total_weight) * 100

    def generate_report(self):
        """Generate the student's report including courses, modules, and GPA."""
        report = f"Report for {self.name} ({self.email})\n"
        report += "------------------------------------\n"

        table_data = []
        for course in self.courses:
            course_avg = course.get_course_average()
            retakes = course.check_retakes()

            # Collecting course modules and their details
            for module in course.modules:
                table_data.append([course.name, module.name, f"{module.score}%", f"{module.weight}%", f"{module.get_weighted_score():.2f}%"])

            # Adding course average and retakes status
            table_data.append([course.name, "Course Average", f"{course_avg:.2f}%", "N/A", "N/A"])
            if retakes:
                table_data.append([course.name, "Retakes Required", ", ".join(retakes), "N/A", "N/A"])
            else:
                table_data.append([course.name, "Retakes Required", "None", "N/A", "N/A"])

            report += f"\nCourse: {course.name}\n"
            report += f"Course Average: {course_avg:.2f}%\n"
            if retakes:
                report += f"Retakes Required: {', '.join(retakes)}\n"
            else:
                report += "No Retakes Required\n"
            report += "------------------------------------\n"

        # Adding overall GPA
        gpa = self.calculate_gpa()
        report += f"Overall GPA: {gpa:.2f}%\n"

        # Adding the table formatted data into the report
        report += "\nDetailed Report:\n"
        table_report = self.create_table(table_data)
        report += table_report

        return report

    def create_table(self, table_data):
        """Generate a formatted table from the report data."""
        table = "\n"
        headers = ["Course", "Module", "Score", "Weight", "Weighted Score"]
        table += f"{' | '.join(headers)}\n"
        table += "-" * 80 + "\n"
        for row in table_data:
            table += f"{' | '.join(row)}\n"
        return table

    def send_report_to_parent(self, parent_email, sender_email, app_password, confirmation_url):
        """Send the student's report to the parent with tracking and confirmation links."""
        report = self.generate_report()

        # Embed an invisible image to track the email open
        tracking_image_url = f"{confirmation_url}/track_open/{parent_email}"

        # Add a confirmation button URL
        confirmation_button_url = f"{confirmation_url}/confirm_view/{parent_email}"

        # Create the email content with HTML to support the tracking image and button
        email_body = f"""
        <html>
        <body>
            <h2>Student Report for {self.name}</h2>
            <p>{report}</p>
            <br>
            <p>Click the button below to confirm you've seen the report:</p>
            <a href="{confirmation_button_url}" style="padding: 10px; background-color: green; color: white; text-decoration: none; border-radius: 5px;">Confirm Viewing</a>
            <br><br>
            <img src="{tracking_image_url}" width="1" height="1" style="display:none;" />
        </body>
        </html>
        """

        # Email setup
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = parent_email
        msg['Subject'] = f"Student Report for {self.name}"

        msg.attach(MIMEText(email_body, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, parent_email, msg.as_string())
            server.quit()
            print(f"Report sent to {parent_email}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")


# ============================
# Example Usage
# ============================

def main():
    # Create a student and courses
    student = Student("Joseph Nishimwe", "j.nishimwe@alustudent.com")

    # Creating courses and modules
    course_1 = Course("Introduction to Programming and Databases")
    course_1.add_module(Module("Python - Hello, World", 100, 10))
    course_1.add_module(Module("Python - Inheritance", 40.59, 20))
    course_1.add_module(Module("Python - Data Structures", 100, 30))

    course_2 = Course("Self-Leadership and Team Dynamics")
    course_2.add_module(Module("Enneagram Test", 80, 10))
    course_2.add_module(Module("Empathy Discussion Board", 65, 20))
    course_2.add_module(Module("Community Building Quiz", 90, 20))

    # Adding courses to student
    student.add_course(course_1)
    student.add_course(course_2)

    # Start the HTTP server for tracking and confirmation
    import threading
    server_thread = threading.Thread(target=run_server, args=("0.0.0.0",
