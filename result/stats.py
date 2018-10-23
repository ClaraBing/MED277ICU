from collections import Counter
from glob import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import random

import pdb

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
  '11': 'Delete',
  # 'others': 'Others',
  }

ignored_keys = ['0', '7', '11', '12', '13']

def count_file(fname, silent=False):
  with open(fname, 'r') as fin:
    lines = [line for line in fin]
  header = lines[0]
  data = [line.strip().split(' ')[-1] for line in lines[1:]]
  data = [each for each in data if each not in ignored_keys]

  counter = Counter(data)
  total = len(data)
  print(sorted(counter, key=lambda x:int(x)))
  for cls in sorted(counter, key=lambda x:int(x)):
    if cls in cls_map and cls != 'others':
      if not silent:
        print('[{}] {}: {}/{} [{:.3f}]'.format(cls, cls_map[cls], counter[cls], total, counter[cls]/total))
    else:
      counter['others'] += counter[cls]
      del counter[cls]
  if not silent:
    print('[{}] {}: {}/{} [{:.3f}]'.format('others', cls_map['others'], counter['others'], total, counter['others']/total))

  del counter['others']

  return counter


def cls_by_day(remove_major=False, plot=True):
  dates = sorted(glob('17_*.csv'))
  mtrx = np.zeros([len(cls_map)-len(ignored_keys), len(dates)])

  for did,date in enumerate(dates):
    curr = count_file(date, silent=True)
    for kid,k in enumerate(sorted(curr, key=lambda x:int(x))):
      if k not in cls_map:
        continue
      mtrx[kid, did] = curr[k]
  if remove_major and False:
    mtrx = np.delete(mtrx, 11, 0) # remove 'Delete'
    mtrx = np.delete(mtrx, 7, 0) # remove 'Lying on bed'
    mtrx = np.delete(mtrx, 0, 0) # remove 'negative'
  print(mtrx.shape)
  normed = mtrx / np.clip(mtrx.sum(1, keepdims=True), a_min=1, a_max=np.inf)
  
  sorted_acts = [cls_map[k] for k in sorted(cls_map, key=lambda x:int(x)) if k not in ignored_keys]
  for rid,row in enumerate(normed):
    print(sorted_acts[rid])
    for elem in row:
      print(round(elem*100, 2), end='\t')
    print()

  if plot:
    plt.imshow(normed, cmap='hot')
    plt.savefig('heatmap_cls_by_day{}.png'.format('_rmMajor' if remove_major else ''))
    plt.clf()

  return normed


def train_val_wrapper():
  print('Train:')
  count_file('train.csv')
  print()
  print('Val:')
  count_file('val.csv')

def date_wrapper():
  dates = sorted(glob('17_06_08.csv'))
  for date in dates:
    print(date, ':')
    count_file(date)
    print()


def select_dates_wrapper():
  counts = cls_by_day(remove_major=True, plot=False)
  print()
  n_days = counts.shape[1]
  n_train, n_val = 10, 7
  assert(n_days == n_train+n_val), print('n_train:{} / n_val:{} / n_days:{}')
  n_trials = 100
  for _ in range(n_trials):
    train = sorted(random.sample(range(n_days), n_train))
    val = sorted([i for i in range(n_days) if i not in train])
    mtrx_train = counts[:, train]
    mtrx_val = counts[:, val]
    if mtrx_val.sum(1).min() > 0.1 and mtrx_val.sum(1).max()<0.6:
      print('train:', train)
      print([round(each*100, 2) for each in mtrx_train.sum(1)])
      print('val:', val)
      print([round(each*100, 2) for each in mtrx_val.sum(1)])
      print('\n')


if __name__ == "__main__":
  # date_wrapper()
  # cls_by_day(remove_major=True)
  select_dates_wrapper()
