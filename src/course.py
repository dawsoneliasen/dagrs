
class Course:
    """ Representation of a course. 

    Attributes:
        dept (str): course department, e.g. ECON
        number (int): course number, e.g. 492
        code (str): course code, e.g. CS 163
        credits (int): credit hours for this course
        prereqs (list): list of Course objects; courses required
        to take this course
        equiv (list): list of Course objects; courses that are 
        equivalent to this course
    """

    def __init__(self, dept=None, number=None, credits=3.0, prereqs=[], equiv=[], completed=None):
        """ Initialize a class object. """
        self.dept = dept
        self.number = number
        self.code = dept + ' ' + number
        self.credits = credits
        self.prereqs = prereqs
        self.equivs = equiv

    def __str__(self):
        return self.code

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.code == other.code
        return False

    def __lt__(self, other):
        if isinstance(other, Course):
            if other in self.prereqs:
                return False
            return int(self.number) < int(other.number)
        return False
