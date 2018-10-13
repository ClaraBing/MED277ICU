import argparse
import glob
import os
import concurrent.futures

def move_files(d_path, fs_path, d_filenames, fs_filenames):
  for name in d_filenames:
    frame_id = name.split('-')[1].split('.')[0]
    new_name = name.split('-')[0]+'-'+frame_id.zfill(6)+'.'+name.split('.')[1]
    os.system('mv {} {}'.format(os.path.join(d_path, name), os.path.join(d_path, new_name)))

  for name in fs_filenames:
    frame_id = name.split('-')[1].split('.')[0]
    new_name = name.split('-')[0]+'-'+frame_id.zfill(6)+'.'+name.split('.')[1]
    os.system('mv {} {}'.format(os.path.join(fs_path, name), os.path.join(fs_path, new_name)))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('date', type=str)
  parser.add_argument('--data_path', type=str, default='/data/onlok/')
  parser.add_argument('--hour', type=int)
  parser.add_argument('--sensor', type=str)
  parser.add_argument('--tar_prefix', type=str, default='home/station/ipCamDetection_v2/bin/output/cvpr')
  parser.add_argument('--output_filename', type=str, default="data.txt")
  parser.add_argument('--overwrite', action="store_true")
  opt = parser.parse_args()

  # Thread Pool
  executor = concurrent.futures.ThreadPoolExecutor(16)

  if not os.path.isdir(os.path.join(opt.data_path, opt.date)):
    print("No data from {}", opt.date)
    exit(0)
  output_file = os.path.join(opt.data_path, opt.date, opt.output_filename)
  if not opt.overwrite and os.path.exists(output_file):
    print("{} already exists".format(output_file))
    exit(0)

  f = open(output_file, 'w+')
  f.write("hour,sensor,num_frames\n")

  hours = sorted([hour for hour in os.listdir(os.path.join(opt.data_path, opt.date)) if
           os.path.isdir(os.path.join(opt.data_path, opt.date, hour))])
  if opt.hour:
    hours = ["{:02d}".format(opt.hour)]
  for hour in hours:
    sensors = sorted([sensor for sensor in os.listdir(os.path.join(opt.data_path, opt.date, hour)) if
           os.path.isdir(os.path.join(opt.data_path, opt.date, hour, sensor))])
    if opt.sensor:
      sensors = ["10.0.1." + opt.sensor]
    for sensor in sensors:
      out_path = os.path.join(opt.data_path, opt.date, hour, sensor)
      tar_files = glob.glob(os.path.join(out_path, "*.tar.gz"))
      if len(tar_files) != 1:
        continue
      tar_path = tar_files[0]
      d_path = os.path.join(out_path, 'd')
      fs_path = os.path.join(out_path, 'fs')

      # cleanup
      os.system('rm -rf {}'.format(d_path))
      os.system('rm -rf {}'.format(fs_path))
      os.system('rm -rf {}'.format(os.path.join(out_path, '*.txt')))

      if not os.path.isfile(tar_path):
        print('{} does not exist'.format(tar_path))
        continue
      os.system('tar -xvzf {} -C {}'.format(tar_path, out_path))
      os.system('mv -v {} {}'.format(os.path.join(out_path, opt.tar_prefix, '*'), out_path))
      os.system('rm -rf {}'.format(os.path.join(out_path, opt.tar_prefix.split('/')[0])))

      # post-processing
      empty = False
      if (not os.path.isdir(d_path)) or (not os.path.isdir(fs_path)):
        empty = True
      else:
        d_filenames = os.listdir(d_path)
        fs_filenames = os.listdir(fs_path)
        if (len(d_filenames) != len(fs_filenames)) or (len(d_filenames) == 0):
          empty = True

      if empty:
        print('{} is empty'.format(tar_path))
        os.system('rm -rf {}'.format(d_path))
        os.system('rm -rf {}'.format(fs_path))
        os.system('rm -rf {}'.format(os.path.join(out_path, '*.txt')))
        continue

      # Write data to output file
      num_frames = len(d_filenames)
      sensor_id = sensor.split('.')[-1]
      f.write("{},{},{}\n".format(hour, sensor_id, num_frames))

      # Move the extracted files
      executor.submit(move_files, d_path, fs_path, d_filenames, fs_filenames)

  print("Waiting to move files...")
  executor.shutdown(wait=True)
  f.close()

if __name__ == '__main__':
  main()
