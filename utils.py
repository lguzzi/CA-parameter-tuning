import csv
import numpy as np
    
def get_metrics(uproot_file, id):
    tree = uproot_file['simpleValidation' + str(id)]['output']
    total_rec = tree['rt'].array()[0]
    total_ass = tree['at'].array()[0]
    total_sim = tree['st'].array()[0]
    
    return [total_sim / total_ass, (total_rec - total_ass) / total_rec]

def read_csv(filename):
    with open(filename, 'r') as f:
        return np.asarray(list(csv.reader(f)), dtype="float32")
    
def write_csv(filename, matrix):
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for i in range(len(matrix)):
            writer.writerow(matrix[i]) 