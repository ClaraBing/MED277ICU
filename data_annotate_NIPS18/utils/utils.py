import cv2
import csv
import numpy as np
import os
import pickle

def makedir(directory):
  if not os.path.isdir(directory):
    os.mkdir(directory)

def check_exists(file_path):
  if not os.path.exists(file_path):
    raise ValueError("File {} does not exist".format(file_path))

def write_pickle(obj, file_path):
  with open(file_path, 'wb') as f:
    pickle.dump(obj, f)

def read_csv(file_path):
  with open(file_path, 'r') as f:
    reader = csv.reader(f)
    data = [[int(x) for x in row] for row in reader]
  return data

def prompt_yes_no(question):
  i = input(question + ' [y/n]: ')
  if i[0] == 'y' or i[0] == 'Y':
    return True
  else:
    return False

def get_video_data(video_path):
  cap = cv2.VideoCapture(video_path)
  if not cap.isOpened():
    raise ValueError("OpenCV cannot open {}.\nTry using /usr/bin/python3.".\
                     format(video_path))
  num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  fps = cap.get(cv2.CAP_PROP_FPS)
  width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  cap.release()
  data = {"num_frames": num_frames,
          "fps": fps,
          "video_length": num_frames / fps,
          "width": width,
          "height": height
         }
  return data

def write_tasks_to_file(tasks, output_file):
  """ Write tasks to a file """
  with open(output_file, 'w+') as f:
    for task in tasks:
      task = [str(t) for t in task]
      line = ",".join(task) + "\n"
      f.write(line)

def read_tasks_from_file(task_file):
  """ Read tasks from a task file """
  tasks = []
  with open(task_file, 'r') as f:
    for line in f:
      task = line.strip().split(',')
      task = [int(t) for t in task]
      tasks.append(task)
  return tasks

def find_nearest_neighbor(t, timestamps, start_index=0, time_diff_threshold=150):
  """
  t and timestamps should both be in milliseconds.
  Returns -1 if a valid time is not found.
  """
  index = np.searchsorted(timestamps[start_index:], t, side='left')
  index += start_index

  # Check valid neighbor
  if index == 0:
    if timestamps[index] - t > time_diff_threshold:
      return -1
    else:
      return index
  elif index == len(timestamps):
    if t - timestamps[index - 1] > time_diff_threshold:
      return -1
    else:
      return index - 1
  else:
    prev_diff = t - timestamps[index - 1]
    next_diff = timestamps[index] - t
    assert(prev_diff >= 0 and next_diff >= 0)
    if min(prev_diff, next_diff) > time_diff_threshold:
      return -1
    # Return the closest one.
    if prev_diff < next_diff:
      return index - 1
    else:
      return index
  return -1

