
class Program:
    """ Representation of a degree program (major, minor, certificate).

    Attributes:
        program_type ('major', 'minor', or 'cert'): description
        of the type of program.
        reqs (list): list of Requirement objects that must be
        completed for the program.

    # TODO: separate different types of requirements, e.g. major, AUCC
    """

    def __init__(self, program_type='major', reqs=[], completed=[], desc='', time_left=8):
        self.desc = desc
        self.program_type = program_type
        self.time_left = time_left
        # remove duplicate requirements
        # TODO: remove duplicate courses?
        self.completed = completed
        l = len(reqs) - 1
        for i in range(l):
            for j in range(l):
                if i == j:
                    continue
                if reqs[i] == reqs[j]:
                    reqs.pop(j)
        self.reqs = self.refactor_reqs(reqs)

    def __str__(self):
        # TODO: include prerequisites
        res = 'COMPLETED: '
        for c in self.completed:
            res += str(c) + ' '
        res += '\n\n'
        for r in self.reqs:
            res += str(r) + '\n'
        return res

    def refactor_reqs(self, reqs):
        " Return a list of reqs as appropriately sized groups of courses "
        courses = []
        new_reqs = []
        for r in reqs:
            if r.req_type == 'rigid':
                for c in r.options:
                    if c not in courses:
                        courses.append(c)
            # TODO: add other kinds of reqs
            else:
                new_reqs.append(r)
        # courses = self.topo_sort(courses)
        courses.sort()
        groups = []
        for i in range(self.time_left):
            groups.append([])
        g = 0
        for i in range(len(courses)):
            if len(groups[g]) >= (len(courses) / len(groups)):
                g += 1
            groups[g].append(courses[i])
        for r in groups:
            new_reqs.append(Requirement(options=r, count=len(r), req_type='rigid'))
        return new_reqs

    def topo_sort(self, courses):
        res = []
        for c in courses:
            res.extend(self.topo_sort(c.prereqs))
            if c not in self.completed:
                res.append(c)
        return res


class Requirement:
    """ Representation of a degree requirement.

    Attributes:
        credits (int): minimum number of credits to satisfy
        this requirement
        count (int): number of courses required to satisfy this credit
        options (list): list of Course and Requirement objects; courses
        that may be taken to satisfy the requirement / 
        sub requirements
        desc (str): description of this requirement
        req_type (str): 'rigid', 'choose', or 'open'; description 
        of requirement type. 
            - 'rigid': all courses in options must be completed (in
            this case, count = len(options))
            - 'choose': a certain number of courses/credits must be chosen
            from options
            - 'open': a certain number of courses/credits must be completed,
            chosen from a general set of courses instead of a list of options
    """
    def __init__(self, options=[], count=None, credits=None, desc=None, req_type=None):
        self.options = options
        self.count = count
        self.desc = desc
        self.req_type = req_type

    def __str__(self):
        res = ''
        if self.req_type == 'choose':
            res += (
                str(self.count) + ' ' + 
                self.desc + ';\n\tchoose from: '
            )
        for c in self.options:
            res += str(c) + '\n'
        # res = res[:-2]
        return res

    def __eq__(self, other):
        if isinstance(other, Requirement):
            return (
                (other.req_type == self.req_type) &
                (other.options == self.options)
            )
        return False
