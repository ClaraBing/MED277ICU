import os

date_map = {}

with open('videos_2210.csv', 'r') as fin:
  data = [line for line in fin]

header = data[0]
data = data[1:]

for line in data:
  date = line.split('_')[0]
  if date not in date_map:
    date_map[date] = []

  date_map[date] += line,

for date in date_map:
  fname = '{}.csv'.format(date.replace('-', '_'))
  if os.path.exists(fname):
    print('File exists:', fname)
    continue
  with open(fname, 'w') as fout:
    fout.write(header)
    for line in date_map[date]:
      fout.write(line)


