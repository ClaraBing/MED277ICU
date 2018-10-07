import os
import shutil
from glob import glob
import pdb

wd = os.path.join(os.getcwd(), 'raw')
os.chdir(wd)

dates = sorted(glob('18-*'))
for date in dates:
  print('######')
  print(date)
  os.system('mkdir -p {}'.format(os.path.join(date, 'all')))
  hours = glob(os.path.join(date, '*'))
  for hour in hours:
    print(hour)
    hour_num = os.path.basename(hour)
    cams = glob(os.path.join(hour, '*'))
    for cam in cams:
      print(cam)
      cam_num = os.path.basename(cam)
      tgt_dir = os.path.join(date, 'all', cam_num)
      os.system('mkdir -p {}'.format(tgt_dir))
      os.chdir(cam)
      os.system('tar -xzf output.tar.gz')
      os.chdir('home/station/ipCamDetection_v2/bin/output/cvpr/')
      ts_file = glob('timestamp*')[0]
      timestamps = [line.strip().split(' ')[1] for line in open(ts_file, 'r')]
      frames = sorted(glob('d/*'))
      assert(len(timestamps) == len(frames)), print('#ts:{} / #frames:{}'.format(len(timestamps), len(frames)))
      # pdb.set_trace()
      for (ts, frame) in zip(timestamps, frames):
        shutil.move(os.path.join(frame), os.path.join(wd, tgt_dir, ts+'.jpg'))
      # os.system('mv home/station/ipCamDetection_v2/bin/output/cvpr/d/* {}/'.format(os.path.join(wd, tgt_dir)))
      os.chdir(wd)
    print()
