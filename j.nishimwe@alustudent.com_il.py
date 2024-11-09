# Class for representing an assignment in a course
class Assignment:
    def __init__(self, name, score, weight, type):
        """
        Initializes an Assignment object.
        
        :param name: The name of the assignment.
        :param score: The score received by the student for the assignment (out of 100).
        :param weight: The weight of the assignment (percentage of total course weight).
        :param type: The type of assignment ('Formative' or 'Summative').
        """
        self.name = name
        self.score = score
        self.weight = weight
        self.type = type  # 'Formative' or 'Summative'

    def get_weighted_score(self):
        """
        Calculates the weighted score of the assignment.

        :return: Weighted score (score * weight / 100).
        """
        return self.score * self.weight / 100


# Class for representing a course that has assignments
class Course:
    def __init__(self, name, total_sessions):
        """
        Initializes a Course object.
        
        :param name: The name of the course.
        :param total_sessions: The total number of mandatory sessions in the course.
        """
        self.name = name
        self.assignments = []  # A list of assignments
        self.attendance = []  # Track attendance as a list of tuples (date, status)
        self.total_sessions = total_sessions  # Total mandatory sessions in the course

    def add_assignment(self, assignment):
        """
        Adds an assignment to the course.
        
        :param assignment: An Assignment object to add to the course.
        """
        self.assignments.append(assignment)

    def mark_attendance(self, date, status):
        """
        Marks attendance for a specific session.
        
        :param date: The date of the class session.
        :param status: The attendance status ('Present' or 'Absent').
        """
        self.attendance.append((date, status))

    def calculate_attendance(self):
        """
        Calculates the attendance percentage.
        
        :return: The percentage of classes attended.
        """
        total_present = sum(1 for _, status in self.attendance if status == 'Present')
        return (total_present / self.total_sessions) * 100

    def calculate_group_score(self, group_type):
        """
        Calculates the total weight and weighted score for a specific group (Formative/Summative).
        
        :param group_type: The type of group ('Formative' or 'Summative').
        :return: A tuple of total weight and total weighted score.
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
        Checks if the student has passed the course based on the Formative and Summative group scores.
        
        :return: A tuple of (passed, formative_total, summative_total).
        """
        formative_weight, formative_score = self.calculate_group_score('Formative')
        summative_weight, summative_score = self.calculate_group_score('Summative')

        # Ensure no division by zero if no assignments in either group
        formative_total = formative_score / formative_weight * 100 if formative_weight else 0
        summative_total = summative_score / summative_weight * 100 if summative_weight else 0

        pass_formative = formative_total >= 30
        pass_summative = summative_total >= 20

        passed = pass_formative and pass_summative
        return passed, formative_total, summative_total

    def get_resubmission_candidates(self):
        """
        Identifies Formative assignments with scores below 50% for resubmission eligibility.
        
        :return: A list of assignment names that are eligible for resubmission.
        """
        return [assignment.name for assignment in self.assignments if assignment.score < 50 and assignment.type == 'Formative']

    def generate_transcript(self, sort_order="ascending"):
        """
        Generates a sorted list of assignments in the course for a transcript.
        
        :param sort_order: The order in which to sort the assignments ('ascending' or 'descending').
        :return: A sorted list of assignments.
        """
        sorted_assignments = sorted(self.assignments, key=lambda x: x.score, reverse=(sort_order == "descending"))
        return sorted_assignments


# Class for representing a student
class Student:
    def __init__(self, name, email):
        """
        Initializes a Student object.
        
        :param name: The name of the student.
        :param email: The email address of the student.
        """
        self.name = name
        self.email = email
        self.courses = []

    def add_course(self, course):
        """
        Adds a course to the student's record.
        
        :param course: A Course object to add to the student's record.
        """
        self.courses.append(course)

    def calculate_gpa(self):
        """
        Calculates the GPA for the student based on all their courses and assignments.
        
        :return: The GPA as a percentage.
        """
        total_weighted_score = 0
        total_weight = 0

        for course in self.courses:
            for assignment in course.assignments:
                total_weighted_score += assignment.get_weighted_score()
                total_weight += assignment.weight

        return (total_weighted_score / total_weight) * 100 if total_weight else 0
