import csv
import numpy as np

# calculate the metrics from validation results
def get_metrics(uproot_file, id):
    tree = uproot_file['simpleValidation' + str(id)]['output']
    total_rec = tree['rt'].array()[0]
    total_ass = tree['at'].array()[0]
    total_ass_sim = tree['ast'].array()[0]
    total_sim = tree['st'].array()[0]
    
    if not total_ass or not total_rec or not total_sim or not total_ass_sim:
        return [1.0, 1.0]

    return [1 - total_ass_sim / total_sim, (total_rec - total_ass) / total_rec]

# read a csv file, return a matrix
def read_csv(filename):
    with open(filename, 'r') as f:
        return np.array(list(csv.reader(f)), dtype=float)
    
# write a matrix to a csv file
def write_csv(filename, matrix):
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for i in range(len(matrix)):
            writer.writerow(matrix[i]) 
