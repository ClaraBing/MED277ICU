import argparse
import numpy as np
import os

def calc_mean_std(data_root_dir):
  '''
  Directly calculate the mean and std of all the frames.
  '''
  from data_pipeline.dataset import SeniorHomeDataset
  split = 'train'
  modalities = ['depth', 'thermal']
  dataset = SeniorHomeDataset(data_root_dir, split, modalities, 1, 1).dataset
  depth_frames, thermal_frames = [], []
  for _, _, d, t in dataset:
    depth_frames.append(d)
    thermal_frames.append(t)
  depth_frames = np.concatenate(depth_frames, axis=0)
  thermal_frames = np.concatenate(thermal_frames, axis=0)
  print("================= Statistics =================\n")
  # Depth
  depth_mean = np.mean(depth_frames)
  depth_std = np.std(depth_frames)
  print("Depth:")
  print("Mean: {}".format(depth_mean))
  print("Std: {}".format(depth_std))
  # Thermal
  thermal_mean = np.mean(thermal_frames)
  thermal_std = np.std(thermal_frames)
  print("Thermal:")
  print("Mean: {}".format(thermal_mean))
  print("Std: {}".format(thermal_std))

def basics(data_root_dir):
  data_root_dir = os.path.join(data_root_dir, 'data')
  for action in sorted(os.listdir(data_root_dir)):
    instances = os.listdir(os.path.join(data_root_dir, action))
    num_frames = 0
    for instance in instances:
      depth_frames = os.listdir(os.path.join(data_root_dir, action, instance, 'depth'))
      thermal_frames = os.listdir(os.path.join(data_root_dir, action, instance, 'thermal'))
      assert len(depth_frames) == len(thermal_frames)
      if len(depth_frames) < 10:
        print('Less than 10 frames:', action, instance)
      num_frames += len(depth_frames)
    print("{}\n{} instances, {} frames\n".format(action, len(instances), num_frames))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_root_dir', type=str, default='/data/onlok_annotated')
  args = parser.parse_args()

  basics(args.data_root_dir)
  calc_mean_std(args.data_root_dir)
