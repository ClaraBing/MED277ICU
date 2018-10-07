from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import cv2
import os
import sys
from glob import glob
import codecs
if sys.stdout.encoding != 'UTF-8':
  sys.stdout = codecs.getwriter('UTF-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
  sys.stderr = codecs.getwriter('UTF-8')(sys.stderr.buffer, 'strict')


from config import *
from .states import *
from . import utils

TASK_SIZE = 64

keymap = {
    'arrows':0,
    'j': 106, 'k': 107,
    ' ': 32, 'esc': 27,
    '0': 48, '1': 49,
    ',/<': 44, './>': 46,
    '-/_': 45, '=/+': 61,
    '~': 96,
    'tab':9,
    'backspace':8,
}

# data_root1 = '..\\sim2\\raw\\237\\fps3\\'
# data_root2 = '..\\sim2\\raw\\238\\fps3\\'

def main(args):
  # assert int(args.depth_sensor) in SENSOR_PAIRS[args.thermal_sensor]
  depth_data_dir = os.path.join(args.data_root_dir, args.date, 'all', '10.233.219.'+args.sensor)

  directory = os.path.join("{}_{}".format(args.date, args.sensor))
  results_dir_root = os.path.join(args.result_root, "results{:d}_{:s}".format(TASK_SIZE, args.date))
  utils.makedir(results_dir_root)
  results_dir = os.path.join(results_dir_root, directory)
  utils.makedir(results_dir)

  ACTIONS = {
    0: 'Negative',
    1: 'Get in bed',
    2: 'Get out of bed',
    3: 'Get in chair',
    4: 'Get out of chair',
    5: 'Moving in bed',
    6: 'Walking',
    7: 'Lying on bed',
    8: 'Sittinng on bed',
    9: 'Sitting in chair',
    10: 'Standing',
    11: 'Delete',
  }

# for MLHC:
# 5: turning patient
# 6: delete

  task_state = TaskState(ACTIONS, args.date, depth_data_dir)
  print("Num tasks: {}".format(task_state.num_tasks))

  job, video_state, = 1, None
  images = sorted(glob(os.path.join(depth_data_dir, '*.jpg')))
  print('# frames:', len(images))
  sys.stdout.flush()

  iid = 0
  while True:
    if job == 1:
      # Get the next task
      task_id = task_state.task_id
      video_state = VideoState(args.sensor, results_dir, task_state)

    utils.print_info(task_state, video_state)
    depth_image = video_state.get_images()

    image = utils.visualize(depth_image, 255)# video_state.white_balance)

    utils.draw_info(image, task_state, video_state)

    cv2.imshow('Video', image)
    job = utils.read_key(cv2.waitKey(0), task_state, video_state)

    if job == -1:
      break


if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('--date', type=str)
  parser.add_argument('--data_root_dir', default='../raw/')
  parser.add_argument('--result-root', default='../result')
  parser.add_argument('--sensor', default='237')

  args = parser.parse_args()

  main(args)
