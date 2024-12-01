
import csv

def read_csv(filename, exclude_header):
    num_rows = 0
    csv_data = []
    with open(filename, 'r') as infile:
        csv_file = csv.reader(infile, delimiter=',')

        if(exclude_header):
            header = next(csv_file)

        for row in csv_file:
            csv_data.append(row)
            num_rows += 1
    
    return num_rows, csv_data
    