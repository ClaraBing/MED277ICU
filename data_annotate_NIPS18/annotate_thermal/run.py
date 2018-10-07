from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import cv2
import os

from config import *
from .states import *
from . import utils

def main(args):
  # assert int(args.depth_sensor) in SENSOR_PAIRS[args.thermal_sensor]
  # match_filename = "match_{}_{}.pkl".format(args.thermal_sensor, args.depth_sensor)
  # match_file_path = os.path.join(args.data_root_dir, args.date, match_filename)
  # assert os.path.exists(match_file_path)
  # depth_sensor_name = args.sensor_prefix + args.depth_sensor
  # depth_data_dir = os.path.join(args.data_root_dir, args.date, "depth", depth_sensor_name)
  thermal_data_dir = os.path.join(args.data_root_dir, args.date, "thermal", args.thermal_sensor)
  thermal_filename = "tasks.pkl"
  thermal_file_path = os.path.join(args.data_root_dir, args.date, "thermal", args.thermal_sensor, thermal_filename)

  # directory = "{}_{}".format(args.thermal_sensor, args.depth_sensor)
  directory = args.thermal_sensor
  utils.makedir(os.path.join(args.data_root_dir, args.date, "results"))
  # Ex. /data/onlok_processed/17-10-13/results/caregiver_6_188/
  results_dir = os.path.join(args.data_root_dir, args.date, "results", directory)
  utils.makedir(results_dir)

  task_state = TaskState(ACTIONS, args.date, thermal_data_dir, thermal_file_path)
  print("Num tasks: {}".format(task_state.num_tasks))

  job, video_state, = 1, None
  while True:
    if job == 1:
      # Get the next task
      task_id = task_state.task_id
      video_state = VideoState(args.thermal_sensor, results_dir, task_state)

    utils.print_info(task_state, video_state)
    thermal_image = video_state.get_images()
    image = utils.visualize(thermal_image, video_state.white_balance)
    utils.draw_info(image, task_state, video_state)

    print('Task: {}'.format(task_state.task_id + 1))
    cv2.imshow('Video', image)
    job = utils.read_key(cv2.waitKey(0), task_state, video_state)

    if job == -1:
      break


if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('date', type=str)
  parser.add_argument('--data_root_dir', default='/data/onlok_processed/')
  parser.add_argument('--depth_sensor', default='188')
  parser.add_argument('--thermal_sensor', default='caregiver_6')
  parser.add_argument('--sensor_prefix', type=str, default='10.0.1.')

  args = parser.parse_args()

  main(args)
