import csv

def sort_by_ts(fname):
  reader = csv.reader(open(fname, 'r'))
  lines = [line for line in reader]
  header = lines[0]
  lines = lines[1:]
  lines = sorted(lines, key=lambda x:x[2])

  with open(fname, 'w') as fout:
    fout.write(header)
  
if __name__ == "__main__":
  sort_by_ts('new_train.csv')
  sort_by_ts('new_val.csv')
