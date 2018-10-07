from __future__ import absolute_import, division, print_function, unicode_literals
import csv
import cv2
import os
from glob import glob
import pickle
from . import utils
import platform
import pdb

class TaskState:
  def __init__(self, actions, date, depth_data_dir):
    self.depth_data_dir = depth_data_dir
    self.tasks = [sorted(glob(os.path.join(depth_data_dir, '*.jpg')))]
    self.num_tasks = len(self.tasks)
    print('Task states: #tasks =', self.num_tasks)

    self.task_id = 0
    self.date = date
    self.actions = actions
    self.num_actions = len(actions)
    self.depth_data_dir = depth_data_dir


class VideoState:
  def __init__(self, depth_sensor, output_dir, task_state):
    if 'windows' in platform.platform().lower():
      self.path_check = lambda x: x.replace('/', '\\')
    else:
      self.path_check = lambda x: x

    self.task_state = task_state
    self.task_id = task_state.task_id
    self.task = task_state.tasks[self.task_id]
    self.depth_sensor = depth_sensor
    self.depth_data_dir = self.path_check(task_state.depth_data_dir)
    self.depth_images = []


    # Read images for this task
    self.num_frames = len(self.task)
    self.read_images()

    csv_path = os.path.join(output_dir, '{}.csv'.format(self.task_id))
    clips = self._load(csv_path)
    self.frame_id = 0   # current frame_id
    self.action_id = 0  # current action_id; default
    self.clips = clips  # (start, end, action_id)
    self.start = -1     # current start
    self.white_balance = 128
    self.white = True
    self.csv_path = csv_path
    # Time to display
    self.thermal_time = ""
    self.depth_time = ""

  def read_images(self):
    print("Reading task {}, {} frames...".format(self.task_id, self.num_frames))
    self.depth_images = []
    for file_path in self.task:
      file_path = self.path_check(file_path)
      assert os.path.exists(file_path), file_path
      img = cv2.imread(file_path)
      self.depth_images.append(img)

  def get_images(self):
    # pdb.set_trace()
    depth_image1 = self.depth_images[self.frame_id]
    t = self.task[self.frame_id]
    self.depth_time = utils.get_time_str(t)
    self.thermal_time = utils.get_time_str(t)
    return depth_image1

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
