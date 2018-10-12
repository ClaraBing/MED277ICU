from __future__ import absolute_import, division, print_function, unicode_literals
import csv
import cv2
import glob
import numpy as np
import os
import pickle
from . import utils

class TaskState:
  def __init__(self, actions, date, thermal_data_dir, thermal_file_path):
    with open(thermal_file_path, 'rb') as f:
      self.tasks = pickle.load(f)

    self.thermal_files = sorted(glob.glob(os.path.join(thermal_data_dir, 'videos', '*.npy')))
    assert len(self.thermal_files) == len(self.tasks)
    keys = sorted(self.tasks.keys())

    self.id_to_keys = {i: keys[i] for i in range(len(keys))}

    self.task_id = 0
    self.date = date
    self.num_tasks = len(self.tasks)
    self.actions = actions
    self.num_actions = len(actions)
    self.thermal_data_dir = thermal_data_dir


class VideoState:
  def __init__(self, thermal_sensor, output_dir, task_state):
    self.task_id = task_state.task_id
    self.task = task_state.tasks[task_state.id_to_keys[self.task_id]]
    self.thermal_sensor = thermal_sensor
    self.thermal_data_dir = task_state.thermal_data_dir
    self.id_to_keys = task_state.id_to_keys

    # Read images for this task
    self.num_frames = len(self.task)
    self.read_images()

    csv_path = os.path.join(output_dir, '{}.csv'.format(self.task_id))
    clips = self._load(csv_path)
    self.frame_id = 0   # current frame_id
    self.action_id = 0  # current action_id
    self.clips = clips  # (start, end, action_id)
    self.start = -1     # current start
    self.white_balance = 128
    self.white = True
    self.csv_path = csv_path
    # Time to display
    self.thermal_time = ""
    # self.depth_time = ""

  def read_images(self):
    print("Reading task {}, {} frames...".format(self.task_id, self.num_frames))
    key = self.id_to_keys[self.task_id]
    path = os.path.join(self.thermal_data_dir, 'videos', key + '.npy')
    self.thermal_images = np.load(path)
    return

    self.thermal_images = []
    for thermal_t in self.task:
      # Depth
      # filename = "d-{}.jpg".format(depth_t)
      # file_path = os.path.join(self.depth_data_dir, filename)
      # assert os.path.exists(file_path)
      # img = cv2.imread(file_path)
      # self.depth_images.append(img)
      # Thermal
      filename = "t-{}.png".format(thermal_t)
      file_path = os.path.join(self.thermal_data_dir, filename)
      assert os.path.exists(file_path), file_path
      img = cv2.imread(file_path)
      self.thermal_images.append(img)
    assert(len(self.thermal_images) == self.num_frames)

  def get_images(self):
    thermal_image = self.thermal_images[self.frame_id]
    # depth_image = self.depth_images[self.frame_id]
    thermal_t = self.task[self.frame_id]
    # depth_t = self.task[self.frame_id][3]
    # self.depth_time = utils.get_time_str(depth_t)
    self.thermal_time = utils.get_time_str(thermal_t)
    # return thermal_image, depth_image
    return thermal_image

  @staticmethod
  def _load(csv_path):
    if os.path.isfile(csv_path):
      f = open(csv_path)
      reader = csv.reader(f)
      clips = [[int(x) for x in row] for row in reader]
      return clips
    else:
      return []

  def save(self):
    if len(self.clips) > 0:
      f = open(self.csv_path, 'wt')
      writer = csv.writer(f)
      for clip in self.clips:
        writer.writerow(clip)
      f.close()
