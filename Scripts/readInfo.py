import csv

def getInfo (csv_file):
    with open(csv_file) as file:
        reader = csv.reader(file, delimiter=';')
        for line in reader:
            if line[0].startswith("%"):
                print('\n')
            if len(line) > 1 and len(line[1]) > 1:
                print(line[0], line[1])

        



def getExperimentInfo():
    return False