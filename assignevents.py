
import os
import csv
import sys

#column index for Student Info File
FIRST_NAME_COL_INDEX = 1
LAST_NAME_COL_INDEX = 2
MAX_EVENTS_COL_INDEX = 4
MAX_BUILD_EVENTS_COL_INDEX = 5
COACH_KID_COL_INDEX = 7
EVENT_PREF_START_COL = 12
EVENT_PREF_END_COL = 35
SCHED_PREF_START_COL = 42   
SCHED_PREF_END_COL = 64
EVENT_RETAIN_START_COL = 65
EVENT_RETAIN_END_COL = 66

#column index for Course Data File
EVENT_ID_ROW_INDEX = 0
EVENT_NAME_ROW_INDEX = 1
EVENT_TYPE_ROW_INDEX = 2
EVENT_CAPACITY_ROW_INDEX = 3
EVENT_TEAM_SIZE_ROW_INDEX = 5
EVENT_TIME_SLOT_ROW_INDEX = 6
EVENT_TIME_CONFLICT_CNT_COL_INDEX = 8
EVENT_CONFLICT_START_COL = 9

BUILD_EVENT_TYPE = 3
NUM_SCIENCE_OLY_EVENTS = 23

class eventAssigner(object):

    PRIORITIZE_PREV_YEAR = False

    def __init__(self):
        self.studentInfo = None
        self.num_teams = 6

        # Student Info Arrays 
        self.first_name_db = []
        self.last_name_db = []
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

        self.num_students = 0
        self.num_events = 0
        self.print_sch_conflicts = True
        self.num_assigned_events = 0
        self.num_coach_kids = 0
        self.num_repeat_event_assignment_requests = 0
        self.print_debug = False
        self.course_info_read = False
        self.student_info_read = False

    def readstudentinfo(self, filename):
        #with open(filename, mode = 'rb') as file:
        #filecontent = file.read()
        with open(filename, 'r') as csvfile:
            csv_file = csv.reader(csvfile, delimiter=',')

            #read first row
            header = next(csv_file)

            for event_index in range(0, NUM_SCIENCE_OLY_EVENTS):
                self.num_students_in_event.append(0)

            #read remaining rows
            for row in csv_file:
                print(row)
                first_name = row[FIRST_NAME_COL_INDEX]
                self.first_name_db.append(first_name)
                self.last_name_db.append(row[LAST_NAME_COL_INDEX])
                self.coach_kid_db.append(row[COACH_KID_COL_INDEX])
                self.max_events_db.append(int(row[MAX_EVENTS_COL_INDEX]))
                self.event_pref_index_db.append(0)
                self.num_assigned_events_db.append(0)
                self.num_assigned_build_events_db.append(0)
                self.avg_assigned_event_ranking_db.append(0)
                self.max_build_events_db.append(row[MAX_BUILD_EVENTS_COL_INDEX])
                self.event_preference_dict[self.num_students] = []
                self.schedule_pref_dict[self.num_students] = []
                self.events_retained_from_prev_years_dict[self.num_students] = []
                self.student_assignment_dict[self.num_students] = []
                self.student_ranking_of_assigned_event_dict[self.num_students] = []
                for col in range (EVENT_PREF_START_COL, EVENT_PREF_END_COL + 1):
                    self.event_preference_dict[self.num_students].append(row[col])
                for col in range (SCHED_PREF_START_COL, SCHED_PREF_END_COL + 1):
                    self.schedule_pref_dict[self.num_students].append(row[col])
                if(self.PRIORITIZE_PREV_YEAR):                    
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
            print(self.event_preference_dict[1])
            print("Student 0 sched prefs: ")
            print(self.schedule_pref_dict)
            print("Student 0 repeat events: ")
            if(self.PRIORITIZE_PREV_YEAR):                    
                print(self.events_retained_from_prev_years_dict[0])
            self.student_info_read = True

    def readCourseData(self, filename):
        with open(filename, 'r') as csvfile:
            print("*************************************************")
            print("Reading course data")
            csv_file = csv.reader(csvfile, delimiter=',')

            #read first row
            header = next(csv_file)

            #read remaining rows
            for row in csv_file:
                self.event_id_db.append(row[EVENT_ID_ROW_INDEX])
                self.event_name_db.append(row[EVENT_NAME_ROW_INDEX])
                self.event_type_db.append(row[EVENT_TYPE_ROW_INDEX])
                self.event_capacity_db.append(int(row[EVENT_CAPACITY_ROW_INDEX]))
                self.event_team_size_db.append(int(row[EVENT_TEAM_SIZE_ROW_INDEX]))
                self.event_time_slot_db.append(int(row[EVENT_TIME_SLOT_ROW_INDEX]))
                self.event_conflict_dict[self.num_events] = []
                self.event_assignment_dict[self.num_events] = []
                num_cols = int(row[EVENT_TIME_CONFLICT_CNT_COL_INDEX])
                print("Num cols =", num_cols)
                for col in range (EVENT_CONFLICT_START_COL, num_cols + EVENT_CONFLICT_START_COL):
                    self.event_conflict_dict[self.num_events].append(row[col])
                print(self.event_conflict_dict[self.num_events])
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
            print("Event Capacity: ")
            print(self.event_capacity_db)
            print("Num Events: ", self.num_events)

            self.course_info_read = True

    def EventIDToName(self, target_event_id):
        index = 0
        for event_id in self.event_id_db:
            if(event_id == target_event_id):
                return(self.event_name_db[index])
            index+=1

    def writeEventPreferences(self, outfilename):
        if(self.course_info_read and self.student_info_read):

            print("********************************************")
            print("Write Event Prefs")
            print("********************************************")
            header = "Student, Event0, Event1, ..."

            with open(outfilename, 'w') as outfile:
                # Write header
                outfile.write("Student,")
                for event_num in range (1, NUM_SCIENCE_OLY_EVENTS + 1):
                    outfile.write("Event{0},".format(event_num))
                outfile.write("\n")

                #write events for each student
                for student_num in range(0, self.num_students):
                    outfile.write("{0} {1},".format(self.first_name_db[student_num], self.last_name_db[student_num]))
                    if(self.first_name_db[student_num] == "Euan"):
                        print(self.event_preference_dict[student_num])
                    for indx in range (0, NUM_SCIENCE_OLY_EVENTS):
                        found, event_array_indx = self.get_event_array_index_from_id(self.event_preference_dict[student_num][indx])
                        if(found):
                            does_event_fit = self.event_fits_into_student_schedule(student_num, event_array_indx)
                            if(does_event_fit):
                                event_name = self.EventIDToName(self.event_preference_dict[student_num][indx])
                                outfile.write("{0},".format(event_name))
                            else:
                                outfile.write(" ,")
                        else:
                            print(f"Error Event ID {self.event_preference_dict[student_num][indx]} not found")
                            outfile.write(f"Error Event ID {self.event_preference_dict[student_num][indx]} not found\n")      
                            return  
                    outfile.write("\n")
                    

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

    def get_event_array_index_from_id(self, desired_event_id):
        event_array_indx = 0
        found = False
        for event_id in self.event_id_db:
            if(event_id == desired_event_id):
                found = True
                return(found, event_array_indx)
            event_array_indx+=1
        return(found, event_array_indx)

    def get_event_id_from_name(self, target_event_name):
        index = 0
        for event_name in self.event_name_db:
            if(event_name == target_event_name):
                return(True, self.event_id_db[index])
            index+=1
        return(False, index)

    def translate_event_names_to_id(self, event_set):
        event_id_set = []
        print(event_set)
        for event_name in event_set:
            event_name = event_name.strip()
            if event_name:
                found, event_id = self.get_event_id_from_name(event_name)
                if(found):
                    event_id_set.append(event_id)
                else:
                    print("Event name {0} not found".format(event_name))
                    return(False, event_id_set)
        return(True, event_id_set)

    def is_event_on_conflict_list(self, target_event_id, events_that_conflict):
        conflict_found = False
        #print("Searching for conflict for event " + target_event_id)
        #print(events_that_conflict)
        for event_id in events_that_conflict:
            if(target_event_id == event_id):
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!conflict found")
                conflict_found = True
        return(conflict_found)

    def append_event_conflicts_to_conflict_list(self, event_id, events_that_conflict):
        found, event_array_indx = self.get_event_array_index_from_id(event_id)
        new_event_conflict_list = events_that_conflict
        if(found):
            for conflict_event_id in self.event_conflict_dict[event_array_indx]:
                new_event_conflict_list.append(conflict_event_id)
            return(True, new_event_conflict_list)
        else:
            print("Error event id {0} not found".format(event_id))
            return(False, new_event_conflict_list)

    def check_event_set_has_no_event_conflicts(self, student_name, event_set):
        does_not_conflict = True
        length = len(event_set)
        print("\n" + student_name)
        events_that_conflict = []
        for event_id in event_set:
            # update event conflict
            if(event_id):
                is_conflict_found = self.is_event_on_conflict_list(event_id, events_that_conflict)
                if(is_conflict_found):
                    print("Event {0} conflicts with existing assigned event".format(self.EventIDToName(event_id)))
                    return(False)
                else:
                    is_append_successful, events_that_conflict = self.append_event_conflicts_to_conflict_list(event_id, events_that_conflict)
                    if not is_append_successful:
                        return(False)
        return(does_not_conflict)

    def get_student_index_from_name(self, target_student_name):
        student_found = False
        student_index = 0
        #print("searching for " + target_student_name)
        for student_name in self.first_name_db:
            student_name = self.first_name_db[student_index] + " " + self.last_name_db[student_index] 
            if(student_name == target_student_name):
                return(True, student_index)
            student_index += 1
        return(False, student_index)

    # return true if all events fit
    def check_event_set_has_no_schd_conflicts(self, student_name, event_set):
        does_event_fit = True
        length = len(event_set)
        found, student_id = self.get_student_index_from_name(student_name)
        if(found):
            for event_id in event_set:
                # update event conflict
                if(event_id):
                    found, event_array_index = self.get_event_array_index_from_id(event_id)
                    if(found):
                        #print("Event index = {0}".format(event_index))
                        does_this_event_fit = self.event_fits_into_student_schedule(student_id, event_array_index)
                        if(not does_this_event_fit):
                            print("Event {0} conflicts with schedule".format(self.EventIDToName(event_id)))
                            does_event_fit = False
                    if(not found):
                        print("!!!!!!!!!!!!!!!!!! Event id not found")
                        return(False)
        else:
            print("Student name not found " + student_name)
        return(does_event_fit)

    # goes through db and determines if events have conflicts or not
    def check_event_assignment_has_no_conflict(self, assigned_events_db):
        does_not_conflict = True
        print("Checking for event conflicts")
        print(self.event_conflict_dict)
        # Go through all students
        for student_record in assigned_events_db:
            # check event conflicts 
            no_student_conflict_found = True
            is_translation_successful, event_id_db = self.translate_event_names_to_id(student_record[1:len(student_record)])
            if(is_translation_successful):
                no_student_conflict_found = no_student_conflict_found and self.check_event_set_has_no_event_conflicts(student_record[0], event_id_db)
                no_student_conflict_found = no_student_conflict_found and self.check_event_set_has_no_schd_conflicts(student_record[0], event_id_db)
            else:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!Translation Failed")
                print(student_record)
                print()
                does_not_conflict = False

            if(no_student_conflict_found == False):
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("Conflict found for student " + student_record[0])
            does_not_conflict = does_not_conflict and no_student_conflict_found
            # check scheduling conflicts 

        if(does_not_conflict == False):
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("At least one conflict found")
        else:
            print("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            print("$$$$$ No conflicts found")
        return(does_not_conflict)

        # Go through all events student has been assigned - if any

#        for already_assigned_event_index in range(0, assigned_events_db[student_index]):
#            # Check that the event conflicts for this event is not already in the student's assigned set of events
#            num_event_conflicts = len(self.event_conflict_dict[event_index_to_assign])
#            already_assigned_event_id = assigned_events_db[student_index][already_assigned_event_index]
#            # Check all conflicts with this candidate event
#            for event_conflict_id in range(self.event_conflict_dict[event_index_to_assign]):
#                # if one of the student's event pooped up, then it's a conflict
#                if(event_conflict_id == already_assigned_event_id):
#                    does_not_conflict = False
#                    if(self.print_sch_conflicts):
#                        conflicting_event_index = self.get_index_from_event_id(event_conflict_id)
#                        print("Student {0} {1} has event conflict. candidate event {2} - conflict event {3}".format(
#                            first_name_db[student_index], last_name_db[student_index], 
#                            self.event_name_db[event_index_to_assign], self.event_name_db[conflicting_event_index]) )
#                        #print("Num assigned events = ", self.num_assigned_events_db[student_index])
#                        #print("Assigned events = ", self.student_assignment_dict[student_index]) 
#        return(does_not_conflict)

    def readAndCheckAssignedEvents(self, assignmentFile):
        with open(assignmentFile, 'r') as csvfile:
            csv_file = csv.reader(csvfile, delimiter=',')

            #read first row
            header = next(csv_file)
            num_cols = len(header)
            print("Num cols =", num_cols)

            event_assignment_db = []

            #read remaining rows
            for row in csv_file:
                event_assignment_record = []
                event_assignment_record.append(row[0])
                event_assignment_record.append(row[1])
                event_assignment_record.append(row[2])
                event_assignment_record.append(row[3])
                event_assignment_record.append(row[4])
                event_assignment_db.append(event_assignment_record)

            self.check_event_assignment_has_no_conflict(event_assignment_db)

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
            print("event index = {0}".format(event_index))
            if(self.num_students_in_event[event_index] < event_capacity):
                is_event_at_capacity = False
            else:
                print("Event {0} is at capacity. {1} students".format(self.event_name_db[event_index], self.num_students_in_event[event_index]))
        return(is_event_at_capacity)

    def event_fits_into_student_schedule(self, student_index, event_index):
        does_event_fit_into_student_schedule = False
        event_time_slot_index = self.event_time_slot_db[event_index]
        #print("event time slot index = {0}".format(event_time_slot_index))
        #print(self.schedule_pref_dict[student_index])
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
                    self.student_ranking_of_assigned_event_dict[event_index]))
            self.avg_assigned_event_ranking_db[student_index] = total_assigned_event_rank / num_events_assigned

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
            event_capacity = self.num_teams * self.event_team_size_db[event_index]
            print("{0} Event {1} has {2} out of {3} students".format(event_index + 1, 
                self.event_name_db[event_index], self.num_students_in_event[event_index], 
                event_capacity))

    def print_event_assignments(self):
        print("\n\r**** Event Assignments *****\n\r")
        for event_index in range (0, self.num_events):
            event_capacity = self.num_teams * self.event_team_size_db[event_index]
            print("{0} Event {1} has {2} out of {3} students".format(event_index + 1, 
                self.event_name_db[event_index], self.num_students_in_event[event_index], 
                event_capacity))
            for student in range (0, self.num_students_in_event[event_index]):
                student_index = self.event_assignment_dict[event_index][student]
                print("   {0} {1} {2}".format(student + 1, 
                    self.first_name_db[student_index], self.last_name_db[student_index]) )

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

    def assign_remaining_events(self):
        num_assigned_events_in = self.num_assigned_events
        for student_index in range (0, self.num_students):
            self.assign_event(student_index)

        for student_index in range (0, self.num_students):
            self.assign_event(self.num_students - 1 - student_index)

        for student_index in range (0, self.num_students):
            self.assign_event(student_index)

        for student_index in range (0, self.num_students):
            self.assign_event(self.num_students - 1 - student_index)

        for student_index in range (0, self.num_students):
            self.assign_event(student_index)

        print("\n\r**** All events assigned *****\n\r")

if __name__ == '__main__':
    assigner = eventAssigner()
    assigner.readstudentinfo(sys.argv[1])
    assigner.readCourseData(sys.argv[2])
    #assigner.writeEventPreferences("eventPrefs.csv")

    # check if event assignment is correct
    assigner.readAndCheckAssignedEvents(sys.argv[3])

    print("\n\r**************************************")
    print("**** Starting event assignment *****")
    print("**************************************\n\r")


#    assigner.assign_coach_kid_first_event()
#    assigner.assign_repeat_events()
    #assigner.assign_remaining_events()
#    assigner.print_student_assignments()
#    assigner.print_event_shortfall()
#    assigner.print_event_distribution()
#    assigner.print_event_assignments()
#    assigner.print_student_event_ranking()
