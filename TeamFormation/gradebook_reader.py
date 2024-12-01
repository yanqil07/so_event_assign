# Reads in gradebook team assignment data
# Outputs the average score per student

from os import sys, path
root_folder = path.join(path.dirname(path.abspath(__file__)), "..")
sys.path.append(root_folder)

from common import utils

FIRST_NAME_MSK = 1
LAST_NAME_MSK = 2
GRADE_LEVEL_MSK = 4
EVENT_NAME_MSK = 8
COMPOSITE_MSK = 16

class GradebookReader():
    _first_name_col = None
    _last_name_col = None
    _grade_level_col = None
    _event_name_col = None
    _composite_col = None

    # db in a array of dicts:
    #   - 'first', 'last', 'grade', 'num_events', 'event1', 'event1_score','event1_rank',...,'event4', 'event4_score','event4_rank'
    _student_info_db = []
    _event_names_db = []

    def find_pertinent_cols(self, header):
        are_all_cols_found = False
        col_found_status = 0
        col_idx = 0
        for col_label in header:
            if(col_label.strip().upper() == "FIRST"):
                self._first_name_col = col_idx
                col_found_status = col_found_status | FIRST_NAME_MSK
            elif(col_label.strip().upper() == "LAST"):
                self._last_name_col = col_idx
                col_found_status = col_found_status | LAST_NAME_MSK
            elif(col_label.strip().upper() == "GRADE LEVEL"):
                self._grade_level_col = col_idx
                col_found_status = col_found_status | GRADE_LEVEL_MSK
            elif(col_label.strip().upper() == "EVENT NAME"):
                self._event_name_col = col_idx
                col_found_status = col_found_status | EVENT_NAME_MSK
            elif(col_label.strip().upper() == "COMPOSITE"):
                self._composite_col = col_idx
                col_found_status = col_found_status | COMPOSITE_MSK
            col_idx += 1
        
        if(col_found_status == 31):
            are_all_cols_found = True
            print("All column names are found")
        else:
            print(f"Error! Not all column names are found.  Status = {col_found_status}")

        return are_all_cols_found


    def find_student_in_db(self, last_name, first_name):
        db_size = len(self._student_info_db)
        lower_idx = 0
        upper_idx = db_size - 1
        curr_idx = 0
        found = False
        while ((upper_idx >= lower_idx) and (not found)):
            curr_idx = int((lower_idx + upper_idx)/2)
            if (last_name == self._student_info_db[curr_idx]['last']):
                if(first_name == self._student_info_db[curr_idx]['first']):
                    found = True
                elif(first_name > self._student_info_db[curr_idx]['first']):
                    lower_idx = curr_idx + 1
                else:
                    upper_idx = curr_idx - 1
            elif (last_name > self._student_info_db[curr_idx]['last']):
                lower_idx = curr_idx + 1
            else:
                upper_idx = curr_idx - 1

        return found, curr_idx


    def merge_entries(self, db_idx, entry):
        num_events = self._student_info_db[db_idx]['num_events']
        match num_events:
            case 1: 
                self._student_info_db[db_idx]['event2'] = entry['event1']
                self._student_info_db[db_idx]['event2_score'] = entry['event1_score']
            case 2:
                self._student_info_db[db_idx]['event3'] = entry['event1']
                self._student_info_db[db_idx]['event3_score'] = entry['event1_score']
            case 3:
                self._student_info_db[db_idx]['event4'] = entry['event1']
                self._student_info_db[db_idx]['event4_score'] = entry['event1_score']
            case 4:
                self._student_info_db[db_idx]['event5'] = entry['event1']
                self._student_info_db[db_idx]['event5_score'] = entry['event1_score']
            case _:
                print("Error. unable to handle {num_events} event nums")
                return False

        num_events += 1
        self._student_info_db[db_idx]['num_events'] = num_events
        return True


    def swap_entries(self, indx1, indx2):
        temp_entry = self._student_info_db[indx1]
        self._student_info_db[indx1] = self._student_info_db[indx2]
        self._student_info_db[indx2] = temp_entry


    def sort_db(self):
        db_len = len(self._student_info_db)
        for entry_idx in range(0, db_len-1):
            for inner_idx in range(1, db_len):
                if(self._student_info_db[inner_idx]['last'] < self._student_info_db[inner_idx - 1]['last']):
                    self.swap_entries(inner_idx, inner_idx - 1)
                elif(self._student_info_db[inner_idx]['last'] == self._student_info_db[inner_idx - 1]['last']):
                    if(self._student_info_db[inner_idx]['first'] < self._student_info_db[inner_idx - 1]['first']):
                        self.swap_entries(inner_idx, inner_idx - 1)


    def sort_event_db(self):
        event_db_len = len(self._event_names_db)
        for outer_loop_idx in range(0,event_db_len-1):
            for inner_loop_idx in range(1,event_db_len): 
                if(self._event_names_db[inner_loop_idx] < self._event_names_db[inner_loop_idx - 1]):
                    temp = self._event_names_db[inner_loop_idx]
                    self._event_names_db[inner_loop_idx] = self._event_names_db[inner_loop_idx - 1]
                    self._event_names_db[inner_loop_idx - 1] = temp


    def add_event_to_event_db(self, event_to_add):
        found = False
        for event_name in self._event_names_db:
            if(event_to_add == event_name):
                found = True

        if(not found):
            self._event_names_db.append(event_to_add)
            self.sort_event_db()

    def add_entry_to_db(self, entry_raw_data):
        entry = {'last': entry_raw_data[self._last_name_col],
                'first': entry_raw_data[self._first_name_col],
                'grade': entry_raw_data[self._grade_level_col],
                'num_events' : 1,
                'event1': entry_raw_data[self._event_name_col],
                'event1_score': float(entry_raw_data[self._composite_col])}

        self.add_event_to_event_db(entry_raw_data[self._event_name_col])
        is_student_in_db, db_indx = self.find_student_in_db(entry['last'],entry['first'])
        if(is_student_in_db == True):
            is_success = self.merge_entries(db_indx, entry)
            if not is_success:
                return False
        else:
            self._student_info_db.append(entry)
            self.sort_db()

        return True


    def calc_avg(self, num_students):
        for db_idx in range(num_students):
            num_events = self._student_info_db[db_idx]['num_events']
            sum = 0
            if(num_events >= 5):
                sum += self._student_info_db[db_idx]['event5_score']
            if(num_events >= 4):
                sum += self._student_info_db[db_idx]['event4_score']
            if(num_events >= 3):
                sum += self._student_info_db[db_idx]['event3_score']
            if(num_events >= 2):
                sum += self._student_info_db[db_idx]['event2_score']
            sum += self._student_info_db[db_idx]['event1_score']

            if(num_events > 0):
                self._student_info_db[db_idx]['average'] = sum/num_events
            else:
                first_name = self._student_info_db[db_idx]['first']
                last_name = self._student_info_db[db_idx]['last']
                print(f"student {first_name} {last_name} has no events")


    def get_all_students_with_event(self, event_name, num_students):
        students_with_event = []
        # find all students with that event
        for student_idx in range(num_students):
            if(event_name == self._student_info_db[student_idx]['event1']):
                entry = {'student_idx':student_idx, 
                            'last':self._student_info_db[student_idx]['last'],
                            'first':self._student_info_db[student_idx]['first'],
                            'event_score':self._student_info_db[student_idx]['event1_score']}
                students_with_event.append(entry)

            if(self._student_info_db[student_idx]['num_events'] >= 2):
                if(event_name == self._student_info_db[student_idx]['event2']):
                    entry = {'student_idx':student_idx, 
                            'last':self._student_info_db[student_idx]['last'],
                            'first':self._student_info_db[student_idx]['first'],
                            'event_score':self._student_info_db[student_idx]['event2_score']}
                    students_with_event.append(entry)

            if(self._student_info_db[student_idx]['num_events'] >= 3):
                if(event_name == self._student_info_db[student_idx]['event3']):
                    entry = {'student_idx':student_idx, 
                            'last':self._student_info_db[student_idx]['last'],
                            'first':self._student_info_db[student_idx]['first'],
                            'event_score':self._student_info_db[student_idx]['event3_score']}
                    students_with_event.append(entry)

            if(self._student_info_db[student_idx]['num_events'] >= 4):
                if(event_name == self._student_info_db[student_idx]['event4']):
                    entry = {'student_idx':student_idx, 
                            'last':self._student_info_db[student_idx]['last'],
                            'first':self._student_info_db[student_idx]['first'],
                            'event_score':self._student_info_db[student_idx]['event4_score']}
                    students_with_event.append(entry)

            if(self._student_info_db[student_idx]['num_events'] >= 5):
                if(event_name == self._student_info_db[student_idx]['event5']):
                    entry = {'student_idx':student_idx, 
                            'last':self._student_info_db[student_idx]['last'],
                            'first':self._student_info_db[student_idx]['first'],
                            'event_score':self._student_info_db[student_idx]['event5_score']}
                    students_with_event.append(entry)
        return students_with_event
    

    def sort_students_by_event(self, students_with_event):
        num_students_in_event = len(students_with_event)
        for outer_loop_idx in range(0,num_students_in_event-1):
            for inner_loop_idx in range(1,num_students_in_event): 
                if(students_with_event[inner_loop_idx - 1]['event_score'] < students_with_event[inner_loop_idx]['event_score']):
                    temp = students_with_event[inner_loop_idx - 1]
                    students_with_event[inner_loop_idx - 1] = students_with_event[inner_loop_idx]
                    students_with_event[inner_loop_idx] = temp
        return students_with_event
    

    def calculate_ranks(self):
        num_students = len(self._student_info_db)
        for event in self._event_names_db:
            students_with_event = self.get_all_students_with_event(event, num_students)
            students_with_event = self.sort_students_by_event(students_with_event)
            rank = 1
            prev_score = 0
            student_num = 0

            # For each student with the rank, write their ranks into the db
            for entry in students_with_event:
                student_idx = entry['student_idx']
                student_num += 1
                num_student_events = self._student_info_db[student_idx]['num_events']
                
                # in case of tie, do not change the rank
                if(entry['event_score'] != prev_score):
                    rank = student_num

                for event_num in range (num_student_events):
                    event_label = f"event{event_num + 1}"
                    rank_label = f"event{event_num + 1}_rank"
                    if(self._student_info_db[student_idx][event_label] == event):
                        self._student_info_db[student_idx][rank_label] = rank


    def write_results_to_file(self, filename, type):
        with open(filename, 'w') as ofile:
            # write header
            ofile.write("last name},first name,grade,num events,average")

            for event in self._event_names_db:
                ofile.write(f",{event}")
            ofile.write("\n")

            # write student data
            for entry in self._student_info_db:
                last_name = entry['last']
                first_name = entry['first']
                grade = entry['grade']
                num_events = entry['num_events']
                average = entry['average']
                ofile.write(f"{last_name},{first_name},{grade},{num_events},{average}")
                for event in self._event_names_db:
                    ofile.write(",")
                    for event_idx in range(num_events):
                        if(event == entry[f'event{event_idx + 1}']):
                            event_value = entry[f'event{event_idx + 1}_{type}']
                            ofile.write(f"{event_value}")

                    # if(event == entry['event1']):
                    #     event_score = entry['event1_score']
                    #     ofile.write(f"{event_score}")
                    # if(num_events >= 2):
                    #     if(event == entry['event2']):
                    #         event_score = entry['event2_score']
                    #         ofile.write(f"{event_score}")
                    # if(num_events >= 3):
                    #     if(event == entry['event3']):
                    #         event_score = entry['event3_score']
                    #         ofile.write(f"{event_score}")
                    # if(num_events >= 4):
                    #     if(event == entry['event4']):
                    #         event_score = entry['event4_score']
                    #         ofile.write(f"{event_score}")
                    # if(num_events >= 5):
                    #     if(event == entry['event5']):
                    #         event_score = entry['event5_score']
                    #         ofile.write(f"{event_score}")
                                        
                ofile.write("\n")


    def read_team_selection_data(self, in_file, score_out_file, rank_out_file):
        num_rows, input_data = utils.read_csv(in_file, False)
        print(f"{num_rows} rows read")

        are_all_cols_found = self.find_pertinent_cols(input_data[0])
        if not are_all_cols_found:
            return

        for row_idx in range(1, num_rows):
            is_success = self.add_entry_to_db(input_data[row_idx])
            if not is_success:
                return
            if(row_idx % 10 == 0):
                print(f"{row_idx} out of {num_rows - 1} entries processed")

        #calculate average
        num_students = len(self._student_info_db)
        self.calc_avg(num_students)

        # calculate ranks
        self.calculate_ranks()

        # write the results to file
        self.write_results_to_file(score_out_file, 'score')
        self.write_results_to_file(rank_out_file, 'rank')


if __name__ == '__main__':
    input_path = "C:/code/so_event_assign/input/"
    output_path = "C:/code/so_event_assign/outputs/"
    input_file = input_path + "TeamSelectionStudentData_2024_11_29.csv"
    score_output_file = output_path + "StudentScores_2024_11_29.csv"
    rank_output_file = output_path + "StudentRanks_2024_11_29.csv"

    gr_reader = GradebookReader()
    gr_reader.read_team_selection_data(input_file, score_output_file, rank_output_file)