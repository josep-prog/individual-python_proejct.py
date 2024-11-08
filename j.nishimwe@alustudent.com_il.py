#!/usr/bin/env python3


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate  # Make sure you have the tabulate module installed

class Module:
    def __init__(self, name, score, weight):
        self.name = name
        self.score = score
        self.weight = weight

    def get_weighted_score(self):
        return self.score * self.weight / 100

class Course:
    def __init__(self, name):
        self.name = name
        self.modules = []

    def add_module(self, module):
        self.modules.append(module)

    def get_total_weighted_score(self):
        total_score = sum(module.get_weighted_score() for module in self.modules)
        return total_score

    def get_course_average(self):
        total_score = sum(module.score for module in self.modules)
        return total_score / len(self.modules)

    def check_retakes(self):
        retakes = [module.name for module in self.modules if module.score < 50]
        return retakes

class Student:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.courses = []

    def add_course(self, course):
        self.courses.append(course)

    def calculate_gpa(self):
        total_weighted_score = sum(course.get_total_weighted_score() for course in self.courses)
        total_weight = sum(module.weight for course in self.courses for module in course.modules)
        return (total_weighted_score / total_weight) * 100

    def generate_report(self):
        report = f"Report for {self.name} ({self.email})\n"
        report += "------------------------------------\n"
        
        table_data = []
        for course in self.courses:
            course_avg = course.get_course_average()
            retakes = course.check_retakes()
            
            # Collecting each course's modules and their details
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
        table_report = tabulate(table_data, headers=["Course", "Module", "Score", "Weight", "Weighted Score"], tablefmt="grid")
        report += "\nDetailed Report:\n" + table_report
        
        return report

    def send_report_to_parent(self, parent_email, sender_email, app_password):
        report = self.generate_report()

        # Email setup
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

# Creating student
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

# Generate report and send email
parent_email = "josephnishimwe398@gmail.com"
sender_email = "j.nishimwe@alustudent.com" 
app_password = "obxlxknjhpuejqwb"  # Your app password
student.send_report_to_parent(parent_email, sender_email, app_password)
