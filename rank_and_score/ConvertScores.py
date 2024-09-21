# This script will read in 
# 1. School rankings for a competition 
#    - first event should appear in column index 3 which is column number 4
#    - the first column should contain the team number and team name
# 2. Student schedule
#    - schedule should have the team number in the first column
#    - schedule should have the multiplier as < : mult> following an event
#    - event names in schedule must match event names in the results 
#
# The output 
# 1. A csv file containing the students ranking
# 2. A csv file containing the students points
#
# Input parameters:
#    competition_results: path and filename of the competition results
#    team_schedules:
#    is_team_num_a_col: Does the results file have a column for the team number
#    starting_col: the column in the schedule csv that has the first event
#    num_cols: number of columns in the schedule csv that contain event

import os
import csv
import sys

# this is the first column in the schedule file that contains events
SCHDLE_FILE_TB_STRT_COL_IDX = 3

# There are really 6 time blocks but lunch is usually included
SCHDLE_FILE_NUM_TBS = 7

_event_name_in_schedule = ["AIR","ANAT","CAPOW","CODE","CRIME",
                    "DD","DP","ECO","EXPD","FACTS",
                    "FLITE","FOREST","FOS","MET","MM",
                    "OPT","REACH","ROAD","ROLL","TOW",
                    "WHEEL","WIND","WIDI"]

_event_name_in_results = ["Air","Anat","Powder","Code","Crime Buster",
                     "DD","Dynamic Planet","Ecology","EXPD","Fast Facts",
                     "Flight","Forestry","Foss","Meteorology","Microbe",
                     "Optics","Stars","Road Scholar","Roller Coaster","Tower",
                     "Wheel Vehicle","Wind","WIDI"]

class StudentEvents(object):
    def __init__(self):
        self.team_number = 0
        self.team_name = ""
        self.num_events = 0
        self.event_names = []
        self.event_multipliers = []
        self.student_name = ""

class RankAndScore(object):

    def __init__(self):
        # this is the first column in the competition results file that contains a competition result
        self.RESULT_FILE_RESULT_STRT_COL_IDX = 3

        self.num_teams = 6
        self.OUTPUT_PATH = "outputs/"
        self.DIVISION = "B"

    def read_competition_results(self, filename, log_file):
        event_names = []
        number_of_events = 0
        team_results = []
        number_of_teams = 0

        print("\n\rReading from competition results from file" + filename)
        log_file.write("\n\rReading from competition results from file" + filename)
        with open(filename, 'r') as csvfile:
            csv_file = csv.reader(csvfile, delimiter=',')

            #read first row
            header = next(csv_file)

            # Event names start in column index 3 and continue to end
            for event_name in range(self.RESULT_FILE_RESULT_STRT_COL_IDX, len(header)):
                event_names.append(header[event_name].strip())
                number_of_events += 1

            #read remaining rows
            for row in csv_file:
                team_results.append(row)
                number_of_teams+=1

        print("Read {0} events and {1} teams".format(number_of_events, number_of_teams))
        log_file.write("Read {0} events and {1} teams".format(number_of_events, number_of_teams))
        return(number_of_events, event_names, number_of_teams, team_results)

    # reads the student events from a schedule file
    def read_student_events(self, filename, log_file, starting_col = SCHDLE_FILE_TB_STRT_COL_IDX, num_cols = SCHDLE_FILE_NUM_TBS):
        student_events_db = []
        number_of_students = 0
        number_of_teams = 0
        prev_team_number = 0
        team_numbers = []

        print("\n\rReading from students schedules from file" + filename)
        log_file.write("\n\rReading from students schedules from file" + filename)
        with open(filename, 'r') as csvfile:
            csv_file = csv.reader(csvfile, delimiter=',')

            team_name = ""
            #read rows
            for row in csv_file:
                team_number = 0
                is_student_data_row = True
                student_events = StudentEvents()

                # if first column is a team number then this row contains a student
                try:
                    team_number = int(row[0])
                except ValueError:
                    is_student_data_row = False

                if(is_student_data_row):
                    student_events.team_number = team_number
                    student_events.team_name = team_name
                    student_events.student_name = row[1]
                    number_of_students+=1
                    if(prev_team_number != team_number):
                        number_of_teams += 1
                        team_numbers.append(row[0])
                        prev_team_number = team_number

                    num_events = 0
                    # go through the columns that may contain events and store it
                    for column_idx in range(starting_col,starting_col + num_cols):
                        event_name = row[column_idx].strip()
                        event_multiplier = 1

                        # event found if cell is not null
                        if(event_name != ""):
                            # check for multipliers
                            delim_idx = event_name.find(":")
                            if(delim_idx > 0):
                                mult_str = event_name[delim_idx + 1:]
                                event_name = event_name[0:delim_idx-1].strip()
                                event_multiplier = float(mult_str)
                            num_events+=1
                            student_events.event_names.append(event_name)
                            student_events.event_multipliers.append(event_multiplier)

                    student_events.num_events = num_events
                    student_events_db.append(student_events)
                    log_file.write("\n\rstudent {0} in {1} team number {2} has {3} events".format(student_events.student_name, 
                                    team_name, team_number, num_events))
                else:
                    team_name = row[1]

        print("Found {0} events in {1} teams".format(number_of_students, number_of_teams))
        log_file.write("\n\rFound {0} events in {1} teams".format(number_of_students, number_of_teams))
        return(number_of_students, student_events_db, number_of_teams, team_numbers)

    def gen_output_file_name(self, input_file_name):
        base_name = os.path.basename(input_file_name)
        base_name = os.path.splitext(base_name)[0]
        output_log_filename = self.OUTPUT_PATH + base_name + ".log"
        output_scores_filename = self.OUTPUT_PATH + base_name + "_Scores.csv"
        output_ranks_filename = self.OUTPUT_PATH + base_name + "_Ranks.csv"
        
        # Check whether the specified path exists or not
        isExist = os.path.exists(self.OUTPUT_PATH)
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(self.OUTPUT_PATH)
            print(f"Output directory {self.OUTPUT_PATH} is created!")

        return output_log_filename, output_scores_filename, output_ranks_filename

    def write_results_file_header(self, results_file, event_names):
        results_file.write("Team Number, Team Name, Student Name")
        for event_name in event_names:
            results_file.write(f",{event_name}")
        results_file.write(",Average")
        results_file.write("\n")

    def extract_team_number_str_from_result(self, team_result, team_number_str_len):
        team_name_and_number = team_result[0]
        team_number_str = team_name_and_number[0:team_number_str_len]
        return(team_number_str)

    def get_team_result(self, target_team_number_str, team_results, log_file, is_team_num_a_col=False):
        is_found = False
        
        # The team number may be included in the same field as the team name.  If there is no column for team
        #   number, then the code needs to extract it from the first column
        if (is_team_num_a_col == False):
            target_team_number_str = self.DIVISION + target_team_number_str.strip()
        team_number_str_len = len(target_team_number_str)  # +1 for the Division, ex "B" for Division B
        for team_result in team_results:
            team_number_str = team_result[0]
            if (is_team_num_a_col == False):
                team_number_str = self.extract_team_number_str_from_result(team_result, team_number_str_len)
            if(target_team_number_str == team_number_str):
                is_found = True
                log_file.write(f"\n\rFound team {target_team_number_str}")
                print(f"\n\rFound team {target_team_number_str}")
                break

        if(not is_found):
            log_file.write(f"\n\rTeam {target_team_number_str} not found")
            print(f"\n\rError! Team {target_team_number_str} not found")

        return(is_found, team_result)

    def write_student_result(self, team_result, student_event, results_file, rank_file, log_file, team_number, event_names, num_teams, translate_event_names):
        #if the student belongs to this team
        total_score = 0
        if(student_event.team_number == team_number):
            # write student info
            rank_file.write(f"{team_number},{student_event.team_name},{student_event.student_name}")
            results_file.write(f"{team_number},{student_event.team_name},{student_event.student_name}")

            # for each event in the list of event
            col_idx = self.RESULT_FILE_RESULT_STRT_COL_IDX
            event_idx = 0
            for event in event_names:
                # check if student has that event
                student_has_event = False
                if translate_event_names:
                    schedule_event_name = _event_name_in_schedule[event_idx].upper()
                else:
                    schedule_event_name = event.upper()
                for student_event_idx in range(0, student_event.num_events):
                    if(student_event.event_names[student_event_idx].upper() == schedule_event_name):
                        #write the score for that rank
                        rank = int(team_result[col_idx])
                        points = ((num_teams - rank + 1)/num_teams) * student_event.event_multipliers[student_event_idx] * 100
                        # cap points to 100
                        if points > 100:
                            points = 100
                        elif points < 0:
                            points = 0
                        rank_file.write(f",{rank}")
                        results_file.write(",{:.2f}".format(points))
                        total_score += points
                        student_has_event = True
                        break
                if(not student_has_event):
                    rank_file.write(f",")
                    results_file.write(f",")
                col_idx+=1
                event_idx+=1

            # calc and write average
            avg_score = 0
            if(student_event.num_events > 0):
                avg_score = total_score/student_event.num_events
            results_file.write(",{:.2f}".format(avg_score))

            # write end of line
            rank_file.write("\n")
            results_file.write("\n")

    def write_team_results(self, results_file, 
                                 out_rank_file, 
                                 log_file, 
                                 team_number_str, 
                                 team_results, 
                                 student_events, 
                                 event_names, 
                                 num_teams,
                                 is_team_num_a_col=False,
                                 translate_event_names=False):
        # for each student in the team, look up event result and write result
        team_number = int(team_number_str)
        
        #find the team result
        is_found, team_result = self.get_team_result(team_number_str, team_results, log_file, is_team_num_a_col)

        # write result for each student in the team
        if is_found:
            for student_event in student_events:
                self.write_student_result(team_result, student_event, results_file, out_rank_file, log_file, team_number, event_names, num_teams, translate_event_names)
        else:
            log_file.writ(f"\n\r!!!ERROR, team number {team_number} not found")
            print(f"ERROR, team number {team_number} not found")

    def calculate_scores_from_ranks(self, competition_results, 
                                          team_schedules, 
                                          is_team_num_a_col=False,
                                          starting_col = SCHDLE_FILE_TB_STRT_COL_IDX, 
                                          num_cols = SCHDLE_FILE_NUM_TBS,
                                          translate_event_names = False):
        output_log_filename, output_scores_filename, output_ranks_filename = self.gen_output_file_name(competition_results)
        with open(output_log_filename, 'w') as outlogfile:
            outlogfile.write("Starting Event Score calculation\n\r")

            number_of_events, event_names, num_teams_in_results, team_results = self.read_competition_results(competition_results, outlogfile)
            number_of_students, student_events, num_teams_in_schdl, team_numbers_str = self.read_student_events(team_schedules, outlogfile, starting_col, num_cols)

            # now for each school team, go through the results and calculate scores
            with open(output_scores_filename, 'w') as out_result_file:
                out_rank_file = open(output_ranks_filename, 'w')
                self.write_results_file_header(out_result_file, event_names)
                self.write_results_file_header(out_rank_file, event_names)
                for team_number_str in team_numbers_str:
                    self.write_team_results(out_result_file, out_rank_file, outlogfile, team_number_str, team_results, 
                                            student_events, event_names, num_teams_in_results, is_team_num_a_col,translate_event_names)

        out_rank_file.close()
        out_result_file.close()

if __name__ == '__main__':
    print("\n\r**************************************")
    print("**** Starting rank and score calculations *****")
    print("**************************************\n\r")

    score_calc = RankAndScore()
#    score_calc.calculate_scores_from_ranks("inputs/SD Regional Results.csv", "inputs/SD Regional SO Schedule.csv")
#    score_calc.calculate_scores_from_ranks("inputs/BIRD SO Results.csv", "inputs/BIRD SO Schedule.csv")
#    score_calc.calculate_scores_from_ranks("inputs/OA Satellite Results.csv", "inputs/OA Satellite Schedule.csv")
#    score_calc.calculate_scores_from_ranks("inputs/BIRD SO Results 2024.csv", "inputs/BIRD SO Schedule 2024.csv", is_team_num_a_col=True)
#    score_calc.calculate_scores_from_ranks("inputs/SanDiegoRegional_B_final.csv", "inputs/SDRegionalSchedule.csv", is_team_num_a_col=True, starting_col=3, num_cols=7)
#    assigner.readCourseData(sys.argv[2])
    score_calc.calculate_scores_from_ranks("inputs/SDRegional_B_final.csv", "inputs/PTMS_RegionalSchedule.csv", is_team_num_a_col=True, starting_col=3, num_cols=7, translate_event_names=True)
#    score_calc.calculate_scores_from_ranks("inputs/SanDiegoRegional_B_final.csv", "inputs/SDRegionalSchedSycamoreRidge.csv", is_team_num_a_col=True, starting_col=3, num_cols=7)
#
#    # check if event assignment is correct
#    assigner.readAndCheckAssignedEvents(sys.argv[3])
