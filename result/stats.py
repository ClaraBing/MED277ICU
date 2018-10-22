from collections import Counter

cls_map = {
  '0': 'background',
  '1': 'Get in bed',
  '2': 'Get out of bed',
  '3': 'Get in chair',
  '4': 'Get out of chair',
  '5': 'Moving in bed',
  '6': 'Walking',
  '7': 'Lying on bed',
  '8': 'Sitting on bed',
  '9': 'Sitting in chair',
  '10': 'Standing',
  '11': 'Delete'
  }

def count_file(fname):
  with open(fname, 'r') as fin:
    lines = [line for line in fin]
  header = lines[0]
  data = [line.strip().split(' ')[-1] for line in lines[1:]]

  counter = Counter(data)
  total = len(data)
  for cls in counter:
    print('[{}] {}: {}/{} [{:.3f}]'.format(cls, cls_map[cls], counter[cls], total, counter[cls]/total))

def train_val_wrapper():
  print('Train:')
  count_file('train.csv')
  print()
  print('Val:')
  count_file('val.csv')

def date_wrapper():
  dates = sorted(glob('17-*.csv'))
  for date in dates:
    print(date, ':')
    count_file(date)
    print()


if __name__ == "__main__":
  date_wrapper()
