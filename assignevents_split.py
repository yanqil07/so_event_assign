
import os
import csv
import sys

#column index for Student Info File
STUDENT_ID_COL_INDEX = 0
FIRST_NAME_COL_INDEX = 1
LAST_NAME_COL_INDEX = 2
STUDENT_GRADE_COL_INDEX = 3
MAX_EVENTS_COL_INDEX = 4
MAX_BUILD_EVENTS_COL_INDEX = 5
COACH_KID_COL_INDEX = 7
EVENT_PREF_START_COL = 13
EVENT_PREF_END_COL = 36
SCHED_PREF_START_COL = 37
SCHED_PREF_END_COL = 57
EVENT_RETAIN_START_COL = 58
EVENT_RETAIN_END_COL = 61

#column index for Course Data File
EVENT_ID_ROW_INDEX = 0
EVENT_NAME_ROW_INDEX = 1
EVENT_TYPE_ROW_INDEX = 2
EVENT_CAPACITY_ROW_INDEX = 3
EVENT_TEAM_SIZE_ROW_INDEX = 5
EVENT_TIME_SLOT_ROW_INDEX = 6
EVENT_CONFLICT_START_COL = 9

BUILD_EVENT_TYPE = 3
NUM_SCIENCE_OLY_EVENTS = 23

SPECIFY_CAPACITY = True
CAPACITY_MULTIPLIER = 2     # This is really the number of teams

class eventAssigner(object):

    def __init__(self):
        self.studentInfo = None
        self.num_teams = 6

        # Student Info Arrays 
        self.student_id_db = []
        self.first_name_db = []
        self.last_name_db = []
        self.student_grade_db = []
        self.coach_kid_db = []
        self.num_assigned_events_db = []    # number of assigned events per student.  Must not exceed max_events of student
        self.event_pref_index_db = []
        self.num_assigned_build_events_db = []
        self.max_events_db = []
        self.max_build_events_db = []
        self.avg_assigned_event_ranking_db = []

        # Student Info Matrices
        self.event_preference_dict = {}
        self.schedule_pref_dict = {}
        self.events_retained_from_prev_years_dict = {}
        self.student_assignment_dict = {}
        self.student_ranking_of_assigned_event_dict = {}

        # Event Info Arrays
        self.event_id_db = []
        self.event_name_db = []
        self.event_type_db = []
        self.event_capacity_db = []
        self.event_team_size_db = []
        self.event_time_slot_db = []
        self.num_students_in_event = []

        # Event Info Matrices
        self.event_conflict_dict = {}
        self.event_assignment_dict = {}

        self.student_event_csv_dict = {}

        self.num_students = 0
        self.num_events = 0
        self.print_sch_conflicts = True
        self.num_assigned_events = 0
        self.num_coach_kids = 0
        self.num_repeat_event_assignment_requests = 0
        self.print_debug = False

    def readstudentinfo(self, filename):
        #with open(filename, mode = 'rb') as file:
        #filecontent = file.read()
        with open(filename, 'r') as csvfile:
            csv_file = csv.reader(csvfile, delimiter=',')

            #read first row
            header = next(csv_file)

            #read remaining rows
            for row in csv_file:
                self.student_id_db.append(row[STUDENT_ID_COL_INDEX])
                self.first_name_db.append(row[FIRST_NAME_COL_INDEX])
                self.last_name_db.append(row[LAST_NAME_COL_INDEX])
                self.student_grade_db.append(row[STUDENT_GRADE_COL_INDEX])
                self.coach_kid_db.append(row[COACH_KID_COL_INDEX])
                self.max_events_db.append(int(row[MAX_EVENTS_COL_INDEX]))
                self.event_pref_index_db.append(0)
                self.num_assigned_events_db.append(0)
                self.num_assigned_build_events_db.append(0)
                self.avg_assigned_event_ranking_db.append(0)
                self.max_build_events_db.append(int(row[MAX_BUILD_EVENTS_COL_INDEX]))
                self.event_preference_dict[self.num_students] = []
                self.schedule_pref_dict[self.num_students] = []
                self.events_retained_from_prev_years_dict[self.num_students] = []
                self.student_assignment_dict[self.num_students] = []
                self.student_ranking_of_assigned_event_dict[self.num_students] = []
                for col in range (EVENT_PREF_START_COL, EVENT_PREF_END_COL + 1):
                    self.event_preference_dict[self.num_students].append(row[col])
                for col in range (SCHED_PREF_START_COL, SCHED_PREF_END_COL):
                    self.schedule_pref_dict[self.num_students].append(row[col])
                for col in range (EVENT_RETAIN_START_COL, EVENT_RETAIN_END_COL + 1):
                    self.events_retained_from_prev_years_dict[self.num_students].append(row[col])
                self.num_students+=1

            print("Number of students = ", self.num_students)
            print("Student first names: ")
            print(self.first_name_db)
            print("Student Last names: ")
            print(self.last_name_db)
            print("Max number of events: ")
            print(self.max_events_db)
            print("Max Build events: ")
            print(self.max_build_events_db)
            print("Coach Kid: ")
            print(self.coach_kid_db)
            print("Student 0 event prefs: ")
            print(self.event_preference_dict[0])
            print("Student 0 sched prefs: ")
            print(self.schedule_pref_dict[0])
            print("Student 0 repeat events: ")
            print(self.events_retained_from_prev_years_dict[0])

    def readCourseData(self, filename):
        with open(filename, 'r') as csvfile:
            csv_file = csv.reader(csvfile, delimiter=',')

            #read first row
            header = next(csv_file)
            num_cols = len(header)
            print("Num cols =", num_cols)

            #read remaining rows
            for row in csv_file:
                self.event_id_db.append(row[EVENT_ID_ROW_INDEX])
                self.event_name_db.append(row[EVENT_NAME_ROW_INDEX])
                self.event_type_db.append(int(row[EVENT_TYPE_ROW_INDEX]))
                self.num_students_in_event.append(0)
                if(SPECIFY_CAPACITY):
                    if(self.num_events==0):
                        self.event_capacity_db.append(int(row[EVENT_TEAM_SIZE_ROW_INDEX]) * CAPACITY_MULTIPLIER + 2)
                    elif(self.num_events==2):
                        self.event_capacity_db.append(int(row[EVENT_TEAM_SIZE_ROW_INDEX]) * CAPACITY_MULTIPLIER + 1)
                    elif(self.num_events==17):
                        self.event_capacity_db.append(int(row[EVENT_TEAM_SIZE_ROW_INDEX]) * CAPACITY_MULTIPLIER + 1)
                    else:
                        self.event_capacity_db.append(int(row[EVENT_TEAM_SIZE_ROW_INDEX]) * CAPACITY_MULTIPLIER)
                else:
                    self.event_capacity_db.append(int(row[EVENT_CAPACITY_ROW_INDEX]))
                self.event_team_size_db.append(int(row[EVENT_TEAM_SIZE_ROW_INDEX]))
                self.event_time_slot_db.append(int(row[EVENT_TIME_SLOT_ROW_INDEX]))
                self.event_conflict_dict[self.num_events] = []
                self.event_assignment_dict[self.num_events] = []
                for col in range (EVENT_CONFLICT_START_COL, num_cols):
                    self.event_conflict_dict[self.num_events].append(row[col])
                self.num_events+=1

            # print so as to verify that data is read correctly
            print("Event IDs: ")
            print(self.event_id_db)
            print("Event names: ")
            print(self.event_name_db)
            print("Event type: ")
            print(self.event_type_db)
            print("Event team size: ")
            print(self.event_team_size_db)
            print("Event timeslot: ")
            print(self.event_time_slot_db)
            print("Event Conflicts: ")
            print(self.event_conflict_dict)
            print("Num Events: ", self.num_events)

    # Determines if the candidate event does not conflict with other events student has already been assigned
    def event_does_not_conflict(self, student_index, event_index):
        does_not_conflict = True
        # Go through all events student has been assigned - if any
        for student_event_index in range(0, self.num_assigned_events_db[student_index]):
            num_event_conflicts = len(self.event_conflict_dict[event_index])
            student_event_id = self.student_assignment_dict[student_index][student_event_index]
            # Check all conflicts with this candidate event
            for conflict_dict_index in range(0, num_event_conflicts):
                event_conflict_id = self.event_conflict_dict[event_index][conflict_dict_index]
                # if one of the student's event pooped up, then it's a conflict
                if(event_conflict_id == student_event_id):
                    does_not_conflict = False
                    if(self.print_sch_conflicts):
                        conflicting_event_index = self.get_index_from_event_id(event_conflict_id)
                        print("Student {0} {1} has event conflict. candidate event {2} - conflict event {3}".format(
                            self.first_name_db[student_index], self.last_name_db[student_index], 
                            self.event_name_db[event_index], self.event_name_db[conflicting_event_index]) )
                        print("Num assigned events = ", self.num_assigned_events_db[student_index])
                        print("Assigned events = ", self.student_assignment_dict[student_index]) 
        return(does_not_conflict)

    def is_event_already_assigned_to_student(self, student_index, event_id):
        is_event_already_assigned = False
        for student_event_index in range(0, self.num_assigned_events_db[student_index]):
            if(self.student_assignment_dict[student_index][student_event_index] == event_id):
                is_event_already_assigned = True
        return is_event_already_assigned

    def get_index_from_event_id(self, event_id):
        is_event_found = False
        event_index = 0
        while(not is_event_found and (event_index < self.num_events)):
            if(self.event_id_db[event_index] == event_id):
                is_event_found = True
            else:
                event_index+=1

        if(not is_event_found):
            event_index = -1
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!Bug Event ID Not Found!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return(event_index)

    def is_build_event(self, event_index):
        is_build_event = False

        if(event_index >= 0):
            if(self.event_type_db[event_index] == BUILD_EVENT_TYPE):
                is_build_event = True
        return(is_build_event)

    def max_build_event_not_exceeded(self, student_index, event_index):
        is_max_build_event_not_exceeded = True

        # If this is a build event and student does not want anymore build events then return False
        if(self.is_build_event(event_index)):
            if(self.num_assigned_build_events_db[student_index] >= self.max_build_events_db[student_index]):
                is_max_build_event_not_exceeded = False
        return(is_max_build_event_not_exceeded)

    def is_event_at_capacity(self, event_index):
        is_event_at_capacity = True
        if(event_index >= 0):
            event_capacity = self.event_capacity_db[event_index]
            if(self.num_students_in_event[event_index] < event_capacity):
                is_event_at_capacity = False
            else:
                print("Event {0} is at capacity. {1} students".format(self.event_name_db[event_index], self.num_students_in_event[event_index]))
        return(is_event_at_capacity)

    def event_fits_into_student_schedule(self, student_index, event_index):
        does_event_fit_into_student_schedule = False
        event_time_slot_index = self.event_time_slot_db[event_index]
        if(self.schedule_pref_dict[student_index][event_time_slot_index] ==  '1'):
            does_event_fit_into_student_schedule = True
        elif(self.print_sch_conflicts):
            print("Student {0} {1} has schedule conflict: timeslot index={2} event name:{3}".format(self.first_name_db[student_index], 
                                self.last_name_db[student_index], event_time_slot_index, self.event_name_db[event_index]))
        return(does_event_fit_into_student_schedule)

    def assign_repeat_event(self, student_index, event_id):
        is_assigned = False
        event_index = self.get_index_from_event_id(event_id)
        if( (not self.is_event_already_assigned_to_student(student_index, event_id)) and
            self.event_does_not_conflict(student_index, event_index) and 
            (self.num_assigned_events_db[student_index] < self.max_events_db[student_index]) and
            self.max_build_event_not_exceeded(student_index, event_index) and
            self.event_fits_into_student_schedule(student_index, event_index) and
            (not self.is_event_at_capacity(event_index)) ):

            # all checks passed, assign event
            self.student_assignment_dict[student_index].append(event_id)
            self.num_assigned_events_db[student_index] += 1
            self.event_assignment_dict[event_index].append(student_index)
            self.num_students_in_event[event_index] += 1
            self.student_ranking_of_assigned_event_dict[student_index].append(0)
            if(self.is_build_event(event_index)):
                self.num_assigned_build_events_db[student_index] += 1
            is_assigned = True
            self.num_assigned_events+=1
            print("{0} Student {1} {2} is assigned {3}".format(student_index+1, self.first_name_db[student_index], 
                    self.last_name_db[student_index], self.event_name_db[event_index]))

        if(not is_assigned):
            print("Unable to assign {0} {1} repeat event {2}".format(self.first_name_db[student_index], self.last_name_db[student_index],
                        self.event_name_db[event_index]))
            # max build events exceeded
            if(not self.max_build_event_not_exceeded(student_index, event_index)):
                print("Max build events exceeded. Student Max build events = {0}. Num build events already {1}".format(
                    self.max_build_events_db[student_index], self.num_assigned_build_events_db[student_index]))  
            if(self.num_assigned_events_db[student_index] >= self.max_events_db[student_index]):
                print("Student's max events reached ", self.max_events_db[student_index])
            if(self.is_event_already_assigned_to_student(student_index, event_id)):
                print("Event already assigned to student")
            print()

    def assign_event(self, student_index):
        is_assigned = False
        event_preference_index = self.event_pref_index_db[student_index]
        while((not is_assigned) and (event_preference_index < self.num_events) ):
            event_to_assign = self.event_preference_dict[student_index][event_preference_index]
            event_index = self.get_index_from_event_id(event_to_assign)
            event_id = self.event_id_db[event_index]
            if((not self.is_event_already_assigned_to_student(student_index, event_id)) and
               self.event_does_not_conflict(student_index, event_index) and 
               (self.num_assigned_events_db[student_index] < self.max_events_db[student_index]) and
               self.max_build_event_not_exceeded(student_index, event_index) and
               self.event_fits_into_student_schedule(student_index, event_index) and
               (not self.is_event_at_capacity(event_index)) ):

                # all checks passed, assign event
                self.student_assignment_dict[student_index].append(event_to_assign)
                self.num_assigned_events_db[student_index] += 1
                self.event_assignment_dict[event_index].append(student_index)
                self.num_students_in_event[event_index] += 1
                self.student_ranking_of_assigned_event_dict[student_index].append(event_preference_index + 1)
                if(self.is_build_event(event_index)):
                    self.num_assigned_build_events_db[student_index] += 1
                is_assigned = True
                self.num_assigned_events+=1
                print("{0} Student {1} {2} is assigned {3}".format(student_index+1, self.first_name_db[student_index], 
                        self.last_name_db[student_index], self.event_name_db[event_index]))

            # whether assigned or not, go to the next event in the student's list
            event_preference_index += 1

        if(event_preference_index >= self.num_events):
            print("Student {0} {1} is out of event preferences".format(self.first_name_db[student_index], self.last_name_db[student_index]))

        self.event_pref_index_db[student_index] = event_preference_index

    def print_student_assignments(self):
        print("\n\r**** Student assignments *****\n\r")
        for student_index in range (0, self.num_students):
            num_events_assigned = len(self.student_assignment_dict[student_index])
            total_assigned_event_rank = 0
            print("{0} Student {1} {2} requested {3} events and has {4} event(s) assigned".format(student_index + 1, 
                    self.first_name_db[student_index], 
                    self.last_name_db[student_index], self.max_events_db[student_index],
                    num_events_assigned))
            for indx in range (0, num_events_assigned):
                event_id = self.student_assignment_dict[student_index][indx]
                event_index = self.get_index_from_event_id(event_id)
                total_assigned_event_rank += self.student_ranking_of_assigned_event_dict[student_index][indx]
                
                if(event_index >= 0):
                    print("  {0}. {1} - {2}".format(indx + 1, self.event_name_db[event_index], 
                    self.student_ranking_of_assigned_event_dict[student_index][indx]))
            if(num_events_assigned > 0):
                self.avg_assigned_event_ranking_db[student_index] = total_assigned_event_rank / num_events_assigned
            else:
                self.avg_assigned_event_ranking_db[student_index] = 0

    def print_student_event_ranking(self):
        print("\n\r**** Student event ranking *****\n\r")
        for student_index in range (0, self.num_students):
            num_events_assigned = len(self.student_assignment_dict[student_index])
            print("{0} Student {1} {2} requested {3} events, is assigned {4} event(s), avg rank is {5}".format(student_index + 1, 
                    self.first_name_db[student_index], 
                    self.last_name_db[student_index], self.max_events_db[student_index],
                    num_events_assigned, self.avg_assigned_event_ranking_db[student_index]))

    def print_event_shortfall(self):
        print("\n\r**** Students not getting max requested events *****\n\r")
        for student_index in range (0, self.num_students):
            num_events_assigned = len(self.student_assignment_dict[student_index])
            num_events_wanted = self.max_events_db[student_index]
            if(num_events_wanted > num_events_assigned):
                print("{0} Student {1} {2} only received {3} out of {4} events".format(student_index + 1, 
                    self.first_name_db[student_index], self.last_name_db[student_index], 
                    num_events_assigned, num_events_wanted))

    def print_event_distribution(self):
        print("\n\r**** Event distribution *****\n\r")
        for event_index in range (0, self.num_events):
            event_capacity = self.event_capacity_db[event_index]
            print("{0} Event {1} has {2} out of {3} students".format(event_index + 1, 
                self.event_name_db[event_index], self.num_students_in_event[event_index], 
                event_capacity))

    def print_event_assignments(self):
        print("\n\r**** Event Assignments *****\n\r")
        for event_index in range (0, self.num_events):
            event_capacity = self.event_capacity_db[event_index]
            print("{0} Event {1} has {2} out of {3} students".format(event_index + 1, 
                self.event_name_db[event_index], self.num_students_in_event[event_index], 
                event_capacity))
            for student in range (0, self.num_students_in_event[event_index]):
                student_index = self.event_assignment_dict[event_index][student]
                print("   {0} {1} {2} - Grade {3}".format(student + 1, 
                    self.first_name_db[student_index], self.last_name_db[student_index], 
                    self.student_grade_db[student_index]) )

    def assign_coach_kid_first_event(self):
        num_assigned_events_in = self.num_assigned_events
        for student in range (0, self.num_students):
            if(self.coach_kid_db[student] == '1'):
                self.num_coach_kids+=1
                self.assign_event(student)
                
        print("\n\r**** Coach kids assigned *****\n\r")
        print("{0} coach kids. {1} events assigned".format(self.num_coach_kids, self.num_assigned_events - num_assigned_events_in))

        print("\n\rStudent assignment\n\r")
        print(self.student_assignment_dict)

    def assign_repeat_events(self):
        num_assigned_events_in = self.num_assigned_events
        for student_index in range (0, self.num_students):
            num_repeat_event_requests = len(self.events_retained_from_prev_years_dict[student_index])
            for event_request_index in range (0, num_repeat_event_requests):
                if(self.events_retained_from_prev_years_dict[student_index][event_request_index] != ''):
                    event_id = self.events_retained_from_prev_years_dict[student_index][event_request_index]
                    if(not self.is_event_already_assigned_to_student(student_index, event_id)):
                        self.num_repeat_event_assignment_requests+=1
                        self.assign_repeat_event(student_index, event_id)

        print("\n\r**** Repeat events assigned *****\n\r")
        print("{0} repeat events requested. {1} repeat events assigned".format(self.num_repeat_event_assignment_requests, 
                        self.num_assigned_events - num_assigned_events_in))
        print("\n\rEvent assignment\n\r")
        self.print_event_assignments()

    def assign_remaining_events(self, starting_position):
        num_assigned_events_in = self.num_assigned_events
        for student_index in range (starting_position, self.num_students):
            self.assign_event(student_index)
        for student_index in range (0, starting_position):
            self.assign_event(student_index)

        for student_index in range (starting_position, self.num_students):
            self.assign_event(self.num_students - 1 - student_index)
        for student_index in range (0, starting_position):
            self.assign_event(self.num_students - 1 - student_index)

        for student_index in range (starting_position, self.num_students):
            self.assign_event(student_index)
        for student_index in range (0, starting_position):
            self.assign_event(student_index)

        for student_index in range (starting_position, self.num_students):
            self.assign_event(self.num_students - 1 - student_index)
        for student_index in range (0, starting_position):
            self.assign_event(self.num_students - 1 - student_index)

        for student_index in range (starting_position, self.num_students):
            self.assign_event(student_index)
        for student_index in range (0, starting_position):
            self.assign_event(student_index)

        print("\n\r**** All events assigned *****\n\r")

    def write_results(self, filename):
        for student_index in range (0, self.num_students):
            self.student_event_csv_dict[student_index] = []

        for student_index in range (0, self.num_students):
            self.student_event_csv_dict[student_index].append(self.student_id_db[student_index])
            self.student_event_csv_dict[student_index].append(self.first_name_db[student_index])
            self.student_event_csv_dict[student_index].append(self.last_name_db[student_index])
            self.student_event_csv_dict[student_index].append(self.coach_kid_db[student_index])  
            self.student_event_csv_dict[student_index].append(self.student_grade_db[student_index])
            self.student_event_csv_dict[student_index].append(self.num_assigned_events_db[student_index])   # courses
            self.student_event_csv_dict[student_index].append(self.num_assigned_events_db[student_index])   # assigned
            self.student_event_csv_dict[student_index].append(0)   # delta
            self.student_event_csv_dict[student_index].append(0)   # available
            self.student_event_csv_dict[student_index].append(0)   # T-Misery
            self.student_event_csv_dict[student_index].append(0)   # W-Misery
            self.student_event_csv_dict[student_index].append(0)   # RPref0
            self.student_event_csv_dict[student_index].append(0)   # RPref1
            self.student_event_csv_dict[student_index].append(0)   # RPref2
            self.student_event_csv_dict[student_index].append(0)   # RPref3
            for assigned_event_index in range (0, self.num_assigned_events_db[student_index]):
                evend_id = self.student_assignment_dict[student_index][assigned_event_index]
                event_index_in_event_db = self.get_index_from_event_id(evend_id)
                self.student_event_csv_dict[student_index].append(evend_id)   
                self.student_event_csv_dict[student_index].append(self.event_name_db[event_index_in_event_db])
                self.student_event_csv_dict[student_index].append(self.event_time_slot_db[event_index_in_event_db])
                self.student_event_csv_dict[student_index].append(1)

        with open(filename, 'w') as f:
            header = ["#SID","First","Last","Coach","Grade",
                    "Courses","Assigned","Delta","Avail","T-Misery","W-Misery","RPref0","RPref1","RPref2","RPref3",
                    "CID1","Name1","Period1","Pref1","CID2","Name2","Period2","Pref2","CID3","Name3","Period3",
                    "Pref3","CID4","Name4","Period4","Pref4","CID5","Name5","Period5","Pref5"]
            #writer.writeheader()
            writer = csv.writer(f)
            writer.writerow(header)
            for student_index in range (0, self.num_students):
                #print(self.student_event_csv_dict[student_index])
                writer.writerow(self.student_event_csv_dict[student_index])

if __name__ == '__main__':
    assigner = eventAssigner()
    assigner.readstudentinfo(sys.argv[1])
    assigner.readCourseData(sys.argv[2])
    starting_position = int(sys.argv[3])

    print("\n\r**************************************")
    print("**** Starting event assignment *****")
    print("**************************************\n\r")

    assigner.assign_coach_kid_first_event()
    assigner.assign_repeat_events()
    assigner.assign_remaining_events(starting_position)
    assigner.print_student_assignments()
    assigner.print_event_shortfall()
    assigner.print_event_distribution()
    assigner.print_event_assignments()
    assigner.print_student_event_ranking()
    assigner.write_results("cvms_assigned_events_part1.csv")
