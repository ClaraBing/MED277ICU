import argparse
import cv2
import glob
import numpy as np
import os
import pickle
import shutil
import concurrent.futures

from config import SENSOR_PAIRS
from utils.depth_utils import *
from utils.thermal_utils import *
from utils import utils

TIME_DIFF_THRESHOLD = 500
TASK_LENGTH_THRESHOLD = 30

def move_depth_images(data_dir, output_dir, timestamps, hour):
  """
  Move depth images within the specific hour to output.
  """
  count = 0
  for i in range(len(timestamps)):
    num, t = timestamps[i] # In milliseconds
    filename = "d-{:06d}.jpg".format(num)
    file_path = os.path.join(data_dir, filename)
    utils.check_exists(file_path)
    output_filename = "d-{}.jpg".format(t)
    output_file_path = os.path.join(output_dir, output_filename)
    # Move file
    os.system('cp {} {}'.format(file_path, output_file_path))
    count += 1
  return count

def process_depth(args):
  """
  Move depth images stored in /data/onlok/ to /data/onlok_processed/
  with each filename containing its timestamp.
  """
  jobs = []
  sensor_name = "10.0.1." + args.depth_sensor
  # Check if there is a data.txt file
  utils.check_exists(os.path.join(args.depth_data_root_dir, args.date, "data.txt"))
  # Output directory
  output_dir = os.path.join(args.output_dir, args.date, "depth", sensor_name)
  if args.overwrite and os.path.exists(output_dir):
    os.system('rm -r {}'.format(output_dir))
  os.makedirs(output_dir, exist_ok=True) # Ex. /data/onlok_processed/17-10-11/depth/10.0.1.188

  # Task file
  task_file = os.path.join(output_dir, "tasks.txt")
  if not args.overwrite and os.path.exists(task_file):
    print("Depth images from {} already processed".format(args.date))
    return

  print('Reading timestamps...')
  all_timestamps = get_all_timestamps(args.depth_data_root_dir, args.date, sensor_name)
  print(sorted(all_timestamps.keys()))

  total_tasks = []
  for hour in range(24):
    if hour in all_timestamps:
      print("Hour: {}".format(hour))
      timestamps = all_timestamps[hour]
      data_dir = os.path.join(args.depth_data_root_dir, args.date, "{:02d}".format(hour),
                              sensor_name, "d")
      # Make sure number of files and length of timestamps match
      files = glob.glob(os.path.join(data_dir, "*.jpg"))
      assert len(files) == len(timestamps), "{}, {}".format(len(files), len(timestamps))
      if not args.get_tasks_only:
        # Move the files
        job = executor.submit(move_depth_images, data_dir, output_dir, timestamps, hour)
        jobs.append(job)
      # Get tasks
      tasks = get_tasks(timestamps)
      total_tasks.extend(tasks)

  total_count = 0
  for job in jobs:
    total_count += job.result()
  print('Total number of frames: {}'.format(total_count))

  # Write tasks
  utils.write_tasks_to_file(total_tasks, task_file)
  print("Number of tasks: {}".format(len(total_tasks)))

def write_thermal_frames(frames, times, output_dir):
  """ Write thermal frames to output_dir """
  num_frames = len(frames)
  for i in range(len(frames)):
    img = frames[i]
    t = times[i]
    output_filename = "t-{}.png".format(t)
    output_path = os.path.join(output_dir, output_filename)
    cv2.imwrite(output_path, img)

def extract_and_write_frames(file_path, task, data_dir, video_name, save_frames):
  """
  Extract thermal frames from video and write frames to output_dir.
  task is a list of timestamps.
  If the number of frames does not match the number of timestamps,
  use linear interpolation to calculate the timestamps.
  """
  # Read frames
  frames = read_thermal_file(file_path, upside_down=False)
  # Save numpy array
  np.save(os.path.join(data_dir, 'videos', video_name), frames)
  if save_frames:
    for img, thermal_t in zip(frames, task):
      output_filename = "t-{}.png".format(thermal_t)
      output_path = os.path.join(data_dir, output_filename)
      cv2.imwrite(output_path, img)

def process_thermal(args):
  """
  Process thermal videos. Move videos within the date to the output directory.
  """
  jobs = []
  output_dir = os.path.join(args.output_dir, args.date, "thermal")
  os.makedirs(output_dir, exist_ok=True)
  output_dir = os.path.join(output_dir, args.thermal_sensor)
  if args.overwrite and os.path.exists(output_dir):
    os.system('rm -r {}'.format(output_dir))
  os.makedirs(output_dir, exist_ok=True) # Ex. /data/onlok_processed/17-10-11/thermal/caregiver_6
  os.makedirs(os.path.join(output_dir, 'videos'), exist_ok=True) # Directory to save video numpy arrays

  # Task file
  task_file = os.path.join(output_dir, "tasks.pkl")
  if not args.overwrite and os.path.exists(task_file):
    print("Thermal videos from {} already processed".format(args.date))
    return

  data_dir = os.path.join(args.thermal_data_root_dir, args.thermal_sensor)
  raw_files = sorted(glob.glob(os.path.join(data_dir, "*_1.mov")))
  total_tasks = {}
  sorted_times = []
  # Get array of times. ["2017-10-11_23:17:42", "2017-10-11_23:28:07", ...]
  for file_path in raw_files:
    filename = os.path.basename(file_path)
    end_time_str = filename.split('.')[0] # Ex. 2017-10-11_23:17:42
    # Check that file is within the date
    if thermal_file_within_date(filename, args.date):
      # Raw video file
      raw_file_path = os.path.join(data_dir, end_time_str + ".000000_1.mov")
      # Timestamp file
      timestamp_file = os.path.join(data_dir, end_time_str + ".000000.txt")
      if os.path.exists(timestamp_file):
        times = read_thermal_timestamps(timestamp_file)
      else:
        print("No timestamps for {}".format(end_time_str))
        continue

      task = [int(t * 1000) for t in times] # milliseconds
      video_data = utils.get_video_data(raw_file_path)
      num_frames = video_data["num_frames"]
      if len(task) != num_frames:
        # Number of timestamps doesn't match! Linear interpolation.
        print('Mismatch {}: {} frames, {} timestamps.'.format(file_path, num_frames, len(task)))
        interval = (task[-1] - task[0]) / (num_frames - 1)
        task = [int(task[0] + i * interval) for i in range(num_frames)]

      # Write thermal frames
      print("{}\t Num frames: {}".format(file_path, num_frames))
      job = executor.submit(extract_and_write_frames, raw_file_path, task, output_dir,
                            end_time_str, args.save_thermal_frames)
      jobs.append(job)

      # Task, same format as depth
      total_tasks[end_time_str] = task
      sorted_times.append(end_time_str)

  assert(sorted_times == sorted(total_tasks.keys())) # Redundant check

  print("Waiting for extract_and_write_frames jobs to finish...")
  for job in jobs:
    job.result()
  # Write tasks
  print("Writing tasks to {}".format(task_file))
  utils.write_pickle(total_tasks, task_file)

def find_match(thermal_tasks, depth_tasks, time_diff):
  """
  Find matches between thermal and depth.
  Note: thermal_tasks (dict) and depth_tasks (array) do not have the same data structure.
  time_diff is in seconds.
  Tasks: An array of tasks.
         Each task is an array of [thermal_file, thermal_frame_index, thermal_time, depth_time].
         Ex. [ ['2017-10-14_05:35:40', 1742, 1507959241729, 1507959221710]
               ['2017-10-14_05:35:40', 1743, 1507959242017, 1507959222046]
               ['2017-10-14_05:35:40', 1744, 1507959242305, 1507959222309]
               ...
             ]
  """

  # Get a flat list of depth times
  all_depth_times = np.array([t for task in depth_tasks for t in task])
  if np.any(np.sort(all_depth_times) != all_depth_times):
    raise ValueError("Timestamps not sorted")

  prev_index = 0
  tasks = []
  current_task = []
  for time_str in sorted(thermal_tasks.keys()):
    thermal_times = thermal_tasks[time_str]
    print("{}, {} frames".format(time_str, len(thermal_times)))
    for frame_index in range(len(thermal_times)):
      t = thermal_times[frame_index]
      # Subtract the time difference to match depth time
      diff = time_diff * 1000 # milliseconds
      index = utils.find_nearest_neighbor(t - diff, all_depth_times,
                                          prev_index, TIME_DIFF_THRESHOLD)
      if index < 0:
        if len(current_task) >= TASK_LENGTH_THRESHOLD:
          tasks.append(current_task)
        current_task = []
      else:
        depth_t = all_depth_times[index]
        pair = [time_str, frame_index, t, depth_t]
        current_task.append(pair)
        prev_index = index
    # Finished one thermal task, add last current task
    if len(current_task) >= TASK_LENGTH_THRESHOLD:
      tasks.append(current_task)
    current_task = []
  return tasks

def extract_frames(tasks, data_dir):
  """
  Extract and save the thermal frames in tasks.
  """
  tasks_in_video = {}
  for task in tasks:
    time_str = task[0][0]
    if time_str not in tasks_in_video:
      tasks_in_video[time_str] = list(task)
    else:
      tasks_in_video[time_str].extend(list(task))

  # Read video and write frames
  video_dir = os.path.join(data_dir, "videos")
  for time_str in sorted(tasks_in_video.keys()):
    filename = time_str + ".000000.mov"
    file_path = os.path.join(video_dir, filename)
    utils.check_exists(file_path)
    task = tasks_in_video[time_str]
    executor.submit(extract_and_write_frames, file_path, task, data_dir)
    #extract_and_write_frames(file_path, task, data_dir)

def match_thermal_and_depth(args):
  # Output as a pickle file
  output_filename = "match_{}_{}.pkl".format(args.thermal_sensor, args.depth_sensor)
  output_file_path = os.path.join(args.output_dir, args.date, output_filename)
  if not args.overwrite and os.path.exists(output_file_path):
    print("Match file {} on {} already exists.".format(output_filename, args.date))
    return
  if args.overwrite and os.path.exists(output_file_path):
    os.remove(output_file_path)

  sensor_name = "10.0.1." + args.depth_sensor
  depth_task_file = os.path.join(args.output_dir, args.date, "depth",
                                 sensor_name, "tasks.txt")
  thermal_task_file = os.path.join(args.output_dir, args.date, "thermal",
                                   args.thermal_sensor, "tasks.pkl")
  utils.check_exists(depth_task_file)
  utils.check_exists(thermal_task_file)
  depth_tasks = utils.read_tasks_from_file(depth_task_file) # Array
  with open(thermal_task_file, 'rb') as f:
    thermal_tasks = pickle.load(f) # Dict

  # Find tasks
  tasks = find_match(thermal_tasks, depth_tasks, args.time_diff)

#  output_dir = os.path.join(args.output_dir, args.date, "thermal", args.thermal_sensor)
#  extract_frames(tasks, output_dir)

#  print("Extracting frames...")
#  executor.shutdown(wait=True)

  # Sanity check
  prev_t = 0
  for task in tasks:
    for _, _, t, _ in task:
      assert t > prev_t
      prev_t = t

  print("Number of matches (tasks): {}".format(len(tasks)))
  print("Writing matches to {}".format(output_file_path))
  utils.write_pickle(tasks, output_file_path)

def main(args):
  global executor
  executor = concurrent.futures.ProcessPoolExecutor(4)

  # Sanity check
  assert int(args.depth_sensor) in SENSOR_PAIRS[args.thermal_sensor], \
            'Thermal {} and depth {} are not paired.'.format(args.thermal_sensor, args.depth_sensor)

  if args.process_depth:
    process_depth(args)
  if args.process_thermal:
    process_thermal(args)
  if args.match_thermal_and_depth:
    match_thermal_and_depth(args)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('date', help="Date")
  parser.add_argument('-d', '--process_depth', action='store_true')
  parser.add_argument('-t', '--process_thermal', action='store_true')
  parser.add_argument('-m', '--match_thermal_and_depth', default=False, action='store_true')
  parser.add_argument('--overwrite', action='store_true',
                      help="Overwrite existing files in output.")
  parser.add_argument('--get_tasks_only', action='store_true',
                      help="Get tasks only. No files are moved.")
  parser.add_argument('--time_diff', type=float, default=0,
                      help="Time difference between depth and thermal")
  parser.add_argument('--depth_data_root_dir', default='/data/onlok/')
  parser.add_argument('--output_dir', default='/data/onlok_processed/')
  parser.add_argument('--depth_sensor', default='188')
  parser.add_argument('--thermal_data_root_dir', default='/data/onlok/thermal/')
  parser.add_argument('--thermal_sensor', default='caregiver_6')
  parser.add_argument('--save_thermal_frames', type=int, default=1, help='Save the thermal frames or not')
  args = parser.parse_args()
  main(args)
