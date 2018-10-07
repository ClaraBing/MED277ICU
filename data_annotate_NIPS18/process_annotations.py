import argparse
import csv
import cv2
import glob
import numpy as np
import os
import pickle
import time
import concurrent.futures

from .config import *
from utils import thermal_utils
from utils import imgproc
from utils import utils

def write_frames(task, depth_data_dir, thermal_frames, depth_output_dir, thermal_output_dir):
  for index, (_, frame_index, thermal_t, depth_t) in enumerate(task, 1):
    # Depth
    depth_file = os.path.join(depth_data_dir, 'd-{}.jpg'.format(depth_t))
    utils.check_exists(depth_file)
    img = cv2.imread(depth_file, cv2.IMREAD_UNCHANGED)
    # Inpainting
    img = imgproc.inpaint(img, threshold=5)
    new_file = os.path.join(depth_output_dir, 'D-{:08d}.jpg'.format(index))
    cv2.imwrite(new_file, img)
    # Thermal
    new_file = os.path.join(thermal_output_dir, 'T-{:08d}.png'.format(index))
    cv2.imwrite(new_file, thermal_frames[frame_index])

def process_annotations(args, task, clips, thermal_frames):
  """
  Each task has multiple annotated clips.
  Save each clip to the dataset.
  """
  depth_data_dir = os.path.join(args.data_root_dir, args.date, 'depth',
                                '10.0.1.' + args.depth_sensor)
  for s, e, cls in clips:
    action = ACTIONS[cls]
    t = task[s:(e+1)] # inclusive
    _, _, thermal_t, _ = t[0]
    # Use time of the first frame as the instance name
    time_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(thermal_t // 1000))
    instance_name = '{}_{}_{}'.format(time_str, args.thermal_sensor, args.depth_sensor)
    instance_dir = os.path.join(args.output_dir, action, instance_name)
    # Check if directory exists
    if os.path.exists(instance_dir):
      if args.overwrite:
        os.system('rm -rf {}'.format(instance_dir))
      else:
        raise Exception('instance already exists')

    # Output directories
    thermal_output_dir = os.path.join(instance_dir, 'thermal')
    depth_output_dir = os.path.join(instance_dir, 'depth')
    os.makedirs(thermal_output_dir)
    os.makedirs(depth_output_dir)
    #write_frames(t, depth_data_dir, thermal_frames, depth_output_dir, thermal_output_dir)
    executor.submit(write_frames, t, depth_data_dir, thermal_frames, depth_output_dir, thermal_output_dir)

def get_thermal_frames(videos, video_dir, time_str):
  """
  Return frames stored in videos cache, or read from the thermal video file.
  """
  if time_str in videos:
    return videos[time_str]
  else:
    print("Reading thermal video: {}".format(time_str))
    videos.clear() # Clear memory
    thermal_file = os.path.join(video_dir, time_str + '.000000_1.mov')
    frames = thermal_utils.read_thermal_file(thermal_file)
    videos[time_str] = frames
    return frames

def main(args):
  global executor
  executor = concurrent.futures.ThreadPoolExecutor(16)

  # Make dataset directories
  for action in ACTIONS:
    os.makedirs(os.path.join(args.output_dir, action), exist_ok=True)

  # Load match file
  match_file = os.path.join(args.data_root_dir, args.date,
                            'match_{}_{}.pkl'.format(args.thermal_sensor, args.depth_sensor))
  utils.check_exists(match_file)
  with open(match_file, 'rb') as f:
    tasks = pickle.load(f)

  thermal_video_dir = os.path.join(args.data_root_dir, args.date, 'thermal',
                                   args.thermal_sensor, 'videos')
  annotation_dir = os.path.join(args.data_root_dir, args.date, 'results',
                                '{}_{}'.format(args.thermal_sensor, args.depth_sensor))
  task_ids = sorted([int(f.split('.')[0]) for f in os.listdir(annotation_dir)])

  # Read and process each task.
  videos = {}
  for task_id in task_ids:
    print("Task: {}".format(task_id))
    clips = utils.read_csv(os.path.join(annotation_dir, '{}.csv'.format(task_id)))
    task = tasks[task_id]
    thermal_time_str = task[0][0]
    # Raw thermal data
    frames = get_thermal_frames(videos, thermal_video_dir, thermal_time_str)
    process_annotations(args, task, clips, frames)

  print("Waiting for jobs to finish...")
  executor.shutdown(wait=True)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('date', help="Date")
  parser.add_argument('--overwrite', action='store_true',
                      help="Overwrite existing files in output.")
  parser.add_argument('--data_root_dir', default='/data/onlok_processed/')
  parser.add_argument('--output_dir', default='/data/onlok_annotated/')
  parser.add_argument('--depth_sensor1', default='237')
  parser.add_argument('--depth_sensor2', default='238')
  args = parser.parse_args()
  main(args)
