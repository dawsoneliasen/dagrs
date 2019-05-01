""" dagrs client. 

Call from the command line with: python3 dagrs.py filename
Where filename is the path to an html download of an audit. 
"""

import os
import requests
import sys
import time

from bs4 import BeautifulSoup
from program import Program
from program import Requirement
from course import Course
from graph import Graph

ignore_reqs = [
    'UNACCEPTABLE COURSES',
    'ACADEMIC HISTORY',
    'TRANSFER CREDIT REPORT',
    'ELECTIVE CREDITS',
    'IN-PROGRESS COURSEWORK',
    ''
]

def course_url(dept, num):
    return 'http://catalog.colostate.edu/search/?P={d}%20{n}'.format(
        d=dept,
        n=num
    )

def get_course_info(dept, num):
    path = './courses/' + dept + num + '.html'
    ref = course_url(dept, num)
    if not os.path.exists(path):
        time.sleep(1)
        course_info = BeautifulSoup(requests.get(ref).content, 'html.parser').find(attrs={'class': 'searchresult'})
        course_info_raw = course_info.prettify()
        f = open(path, 'w+')
        f.write(course_info_raw)
        f.close()
    else:
        course_info = BeautifulSoup(open(path), 'html.parser')
    return course_info

def parse_course_info(course_info, dept, num):
    """ Return a course object from 
    a BeautifulSoup object of the course page.
    Recursively creates prerequisite relationships.
    # TODO: recursively split prerequisites on 'and' / 'or'
    """
    course_info_raw = course_info.prettify()
    if 'Registration Information' in course_info_raw:
        preqs = course_info_raw[course_info_raw.find('Prerequisite'): course_info_raw.find('Registration Information')]
    else: 
        course_info_raw = course_info_raw.replace('Terms Offered', 'Term Offered')
        preqs = course_info_raw[course_info_raw.find('Prerequisite'): course_info_raw.find('Term Offered')]
    preqs_soup = BeautifulSoup(preqs, 'html.parser')
    preqs_list = []
    for p in preqs_soup.find_all(attrs={'class': 'code'}):
        code = p['title'].replace(u'\xa0', ' ').split(' ')
        pdept, pnum = code[0], code[1]
        if pdept == 'ECE':
            continue
        if pdept == 'MATH':
            continue
        psoup = get_course_info(pdept, pnum)
        preq = parse_course_info(psoup, pdept, pnum)
        preqs_list.append(preq)
        # preqs don't have to be perfectly represented...
        # just include those that are specified by the program
    return Course(dept=dept, number=num, prereqs=preqs_list)

def main(file):
    """ Entry point, will print parse of audit and create dagrs. """
    soup = BeautifulSoup(file, 'html.parser')    
    reqs = soup.find_all(attrs={'class': 'requirement'})
    req_list = []    
    completed = []
    for r in reqs:
        subreqs = r.find_all(attrs={'class': 'auditSubrequirements'})
        try:
            title = r.find(attrs={'reqTitle'}).text.upper()
        except AttributeError:
            title = ''
        try:
            title = title.split(' - ', 1)[1]
        except IndexError:
            pass
        title = title.lstrip().rstrip()
        if title in ignore_reqs:
            if title == 'ACADEMIC HISTORY':
                for c in r.find_all(attrs={'class': 'course'}):
                    c = c.text.strip().replace(u'\xa0', ' ').replace(' ', '')
                    dept = c[:-3]
                    num = c[-3:]
                    course = Course(dept=dept, number=num)
                    completed.append(course)
            continue
        print('REQ:', title)
        print('-----' + ('-' * len(title)))

        if len(subreqs) != 1:
            raise Exception('Multiple subrequirements.')
        s = subreqs[0]

        desc = s.find(attrs={'class': 'subreqTitle'})
        if desc is None:
            desc = ''
        else:
            desc = desc.text
        if desc != '':
            print(desc)

        needs = s.find(attrs={'class': 'subreqNeeds'})
        done = s.find(attrs={'class': 'subrequirementTotals'})
        count = None
        done_count = None
        if needs is not None:
            count = needs.find(attrs={'class': 'count number'})
        if count is not None:
            count = int(count.text.strip())
            print(count, 'courses remaining')
        else:
            print('* Complete!')
            print()
            continue
        if done is not None:
            done_count = done.find(attrs={'class': 'count number'})
        if done_count is not None:
            try:
                done_count = int(done_count.text.strip())
                print(done_count, 'completed')
            except ValueError:
                done_count = 0
        else:
            done_count = 0

        courses = s.find_all(attrs={'class': 'course draggable'})
        courses_list = []
        for c in courses:
            dept = c['department'].strip()
            num = c['number'].strip()
            course_info = get_course_info(dept, num)
            course = parse_course_info(course_info, dept, num)
            courses_list.append(course)
            course_info = course_info.text.replace('\n', '').replace('\t', ' ')
            if 'Registration Information' in course_info:
                preqs = course_info[course_info.find('Prerequisite'): course_info.find('Registration Information')]
            else: 
                preqs = course_info[course_info.find('Prerequisite'): course_info.find('Term Offered')]
            preqs = preqs.replace('           ', ' ').replace('          ', ' ')
            print(course)
            print('\t' + preqs)
        print()
        if len(courses_list) == count:
            req_type = 'rigid'
        else:
            req_type = 'choose'
        if not desc:
            desc = title
        req = Requirement(
            options=courses_list,
            desc=desc,
            count=count,
            req_type=req_type
        )
        req_list.append(req)
    try:
        time_left = int(sys.argv[2])
    except IndexError:
        time_left = 8
    prog = Program(reqs=req_list, completed=completed, time_left=time_left)
    print(str(prog))
    Graph(prog)

if __name__ == '__main__':
    file = open('audits/' + sys.argv[1])
    main(file)
    file.close()
