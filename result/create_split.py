import os
from glob import glob


# NOTE: values for train/val are found by
# function `select_dates_wrapper` in `stats.py`

train = [0, 1, 2, 3, 5, 6, 8, 11, 13, 14]
# [66.48, 65.49, 62.64, 60.64, 45.0, 73.33, 49.98, 79.28, 54.3]
val = [4, 7, 9, 10, 12, 15, 16]
# [33.52, 34.51, 37.36, 39.36, 55.0, 26.67, 50.02, 20.72, 45.7]

dates = sorted(glob('17_*.csv'))
# train
os.makedirs('train', exist_ok=True)
for i in train:
  os.system('mv {} train/'.format(dates[i]))

os.system('echo "Video_name Frame Image_path Label" > train.csv')
os.system('cat train/*.csv | grep -v "Frame" >> train.csv')

# val
os.makedirs('val', exist_ok=True)
for i in val:
  os.system('mv {} val/'.format(dates[i]))
os.system('echo "Video_name Frame Image_path Label" > val.csv')
os.system('cat val/*.csv | grep -v "Frame" >> val.csv')

