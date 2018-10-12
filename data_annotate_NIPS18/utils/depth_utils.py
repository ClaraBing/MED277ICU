import glob
import os
import time

def read_depth_timestamp(timestamp_file):
  """ Read depth data timestamp file """
  timestamps = []
  with open(timestamp_file, 'r') as f:
    for line in f:
      if len(line.split()) != 2:
        # Incorrect data
        return []
      num = int(line.split()[0])
      t = int(line.split()[1])
      timestamps.append((num, t))
  return timestamps

def get_all_timestamps(data_root_dir, date, sensor_name):
  """
  Get timestamps for all hours for a specific date and sensor.
  Raise error if more than one timestamp is stored.
  """
  all_timestamps = {}
  for hour in range(24):
    data_dir = os.path.join(data_root_dir, date, "{:02d}".format(hour), sensor_name)
    if os.path.isdir(data_dir):
      files = glob.glob(os.path.join(data_dir, "timestamps*.txt"))
      frames = glob.glob(os.path.join(data_dir, 'd', '*.jpg'))
      if len(files) == 0:
        continue
      if len(files) > 1:
        print("More than one timestamp files in {}".format(data_dir))
        for f in files:
          n_timestamps = len(open(f, 'r').readlines())
          if n_timestamps == len(frames):
            files = [f]
            break
      timestamp_file = os.path.join(data_dir, files[0])
      all_timestamps[hour] = read_depth_timestamp(timestamp_file)
  return all_timestamps

def calc_depth_time(depth_data_dir, depth_frame_number):
  """
  Calculate exact time of a depth image.
  Return the time in seconds.
  Example:
    depth_data_dir: "/data/onlok/17-10-11/12/10.0.1.188"
    depth_frame_number: 1241
  """
  if not os.path.exists(depth_data_dir):
    raise ValueError("Depth data {} does not exist".format(depth_data_dir))
  # Some directories have more than 1 timestamp file for some reason. Find the longest one.
  files = sorted(glob.glob(os.path.join(depth_data_dir, "timestamps*.txt")))
  timestamps = []
  for filename in files:
    timestamp_file = os.path.join(depth_data_dir, filename)
    curr_timestamps = read_depth_timestamp(timestamp_file)
    if len(curr_timestamps) > len(timestamps):
      timestamps = curr_timestamps
  t = timestamps[depth_frame_number] # In milliseconds
  return t / 1000

def get_tasks(timestamps, time_diff_threshold=500, task_length_threshold=30):
  """
  Group consecutive timestamps to a task.
  Only include tasks that are longer than task_length_threshold frames.
  """
  tasks = []
  current_task = []
  prev_time = 0
  for i in range(len(timestamps)):
    _, t = timestamps[i] # In milliseconds
    diff = t - prev_time
    if diff > time_diff_threshold:
      if len(current_task) >= task_length_threshold:
        tasks.append(current_task)
      current_task = [t]
    else:
      current_task.append(t)
    prev_time = t
  # Add last current task
  if len(current_task) >= task_length_threshold:
    tasks.append(current_task)
  return tasks

