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
  match_filename = "match{:d}_{}_{}_{}.pkl".format(TASK_SIZE, args.depth_sensor1, args.depth_sensor2, args.date)
  match_file_path = os.path.join(args.data_root_dir, match_filename)
  assert os.path.exists(match_file_path), match_file_path
  depth_data_dir1 = os.path.join(args.data_root_dir, "raw/", args.depth_sensor1, 'fps3_{:s}'.format(args.date))
  depth_data_dir2 = os.path.join(args.data_root_dir, "raw/", args.depth_sensor2, 'fps3_{:s}'.format(args.date))

  directory = "{}_{}".format(args.depth_sensor1, args.depth_sensor2)
  results_dir_root = os.path.join(args.data_root_dir, "results{:d}_{:s}".format(TASK_SIZE, args.date))
  utils.makedir(results_dir_root)
  # Ex. /data/onlok_processed/17-10-13/results/caregiver_6_188/
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

  task_state = TaskState(ACTIONS, args.date, depth_data_dir1, depth_data_dir2, match_file_path)
  print("Num tasks: {}".format(task_state.num_tasks))

  job, video_state, = 1, None
  # while True:
  images_1 = sorted(glob(os.path.join(depth_data_dir1, '*.png')))
  images_2 = sorted(glob(os.path.join(depth_data_dir2, '*.png')))
  print('# frames:', len(images_1))
  sys.stdout.flush()

  iid = 0
  # while iid < len(images_1):
  while True:
    if job == 1:
      # Get the next task
      task_id = task_state.task_id
      video_state = VideoState(args.depth_sensor1, args.depth_sensor2, results_dir, task_state)
    # print('Video state ready')
    # sys.stdout.flush()

    utils.print_info(task_state, video_state)
    depth_image1, depth_image2 = video_state.get_images()
    # print("Images ready")
    # sys.stdout.flush()

    # depth_image1, depth_image2 = images_1[iid], images_2[iid]
    image = utils.visualize(depth_image1, depth_image2, 255)# video_state.white_balance)
    # print("Visualize ready")
    # sys.stdout.flush()

    utils.draw_info(image, task_state, video_state)
    # print("Draw ready")
    # sys.stdout.flush()

    cv2.imshow('Video', image)
    job = utils.read_key(cv2.waitKey(0), task_state, video_state)
    # print(job)
    # print()
    # sys.stdout.flush()

    if job == -1:
      break


if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('--date', type=str)
  parser.add_argument('--data_root_dir', default='/data/onlok_processed/')
  parser.add_argument('--depth_sensor1', default='237')
  parser.add_argument('--depth_sensor2', default='238')
  parser.add_argument('--sensor_prefix', type=str, default='10.0.1.')

  args = parser.parse_args()

  main(args)
