import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import csv
from collections import Counter


bin_size = 10
reader = csv.reader(open('updated.csv', 'r'))
lines = [line for line in reader]
lines = lines[1:3000] # remove header
data = [line[0].split(' ') for line in lines]

timelines = {c:[] for c in range(12)}

for i in range(0, len(data), bin_size):
  counter = Counter([each[-1] for each in data[i:i+bin_size]])
  for c in range(12):
    if str(c) in counter:
      if counter[str(c)] == 0:
        print(c)
      val = np.log(counter[str(c)])
      timelines[c] += val,
    else:
      timelines[c] += 0,
    # timelines[c] += np.log(counter[c]) if str(c) in counter else 0,

for key in timelines:
  plt.plot(timelines[key], label=str(key))
plt.legend()
plt.savefig('timeline_{}.jpg'.format(bin_size))
plt.clf()

