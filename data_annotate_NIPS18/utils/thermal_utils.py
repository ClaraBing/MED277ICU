import cv2
import datetime
import numpy as np
import os
import time

# Thermal filenames format
DATE_FORMAT = "%Y-%m-%d_%H:%M:%S"

def get_local_time_from_utc(time_str, date_format="%Y-%m-%d_%H:%M:%S"):
  """ Parse the time string and get local time """
  # Convert to UTC-7
  t = datetime.datetime.strptime(time_str, date_format) - datetime.timedelta(hours=7)
  return t

def thermal_file_within_date(thermal_filename, date):
  """
  Check that the thermal file is within the given date
  thermal_filename: Ex. 2017-10-12_21:35:34.000000.mov
  date: Ex. 17-10-13
  """
  # Get time of the thermal video
  time_str = thermal_filename.split('.')[0]
  t = get_local_time_from_utc(time_str)
  # Get start and end time of the day
  year, month, day = [int(x) for x in date.split('-')]
  year += 2000
  start = datetime.datetime(year=year, month=month, day=day)
  try:
    end = datetime.datetime(year=year, month=month, day=day+1)
  except:
    # (day+1) is out of range for month
    end = datetime.datetime(year=year, month=month+1, day=1)
  return t > start and t < end

def get_time_from_frame(end_time_in_seconds, video_length, frame_number, num_frames):
  """
  Linearly calculate the time. frame_number can be a numpy array.
  """
  # Time difference between frame and start of video
  delta = video_length / (num_frames - 1) * frame_number
  return end_time_in_seconds - video_length + delta

def calc_thermal_time(thermal_end_time, video_data, frame_number):
  """ Calculate time of a frame from thermal video. """
  num_frames = video_data["num_frames"]
  video_length = video_data["video_length"]
  # Get end time
  end_time = get_local_time_from_utc(thermal_end_time)
  end_time_in_seconds = time.mktime(end_time.timetuple())
  t_in_seconds = get_time_from_frame(end_time_in_seconds, video_length, frame_number, num_frames)
  return t_in_seconds

def read_thermal_file(file_path, upside_down=False):
  """
  Read a thermal video file, e.g. 2017-10-11_18:56:18.000000_1.mov.
  """
  cap = cv2.VideoCapture(file_path)
  if not cap.isOpened():
    raise ValueError("OpenCV cannot open {}.\nTry using /usr/bin/python3.".format(file_path))

  frames = []
  while True:
    ret, frame = cap.read()
    if not ret:
      break
    if upside_down:
      frame = np.rot90(frame, k=2)
    # 3 channels, each channel is one frame.
    frames.append(frame[:,:,0])
  frames = np.array(frames)
  cap.release()
  return frames

def scale_thermal_frame(frame):
  """ Frame values are (temperature * 2) """
  frame = (frame / 2).clip(10, 40) - 10
  frame = (frame / 30 * 255).astype(np.uint8)
  return frame

def write_thermal_frames(file_path, output_dir, scale_frame=False, upside_down=True):
  frames = read_thermal_file(file_path, upside_down)
  num_frames, height, width = frames.shape
  for i in range(num_frames):
    filename = "t-{:06d}.png".format(i)
    output_file = os.path.join(output_dir, filename)
    frame = frames[i]
    if scale_frame:
      frame = scale_thermal_frame(frames[i])
    cv2.imwrite(output_file, frame)

def read_thermal_timestamps(timestamps_file):
  """
  Each line is in this format: 2017-10-20T05:45:05.458018Z
  Return timestamps in seconds.
  """
  timestamps = []
  with open(timestamps_file, 'r') as f:
    for line in f:
      time_str, suffix = line.strip().split('.')
      date_format = "%Y-%m-%dT%H:%M:%S"
      t = get_local_time_from_utc(time_str, date_format)
      t_in_seconds = time.mktime(t.timetuple())
      ms = int(suffix[:3]) / 1000.0
      t_in_seconds += ms
      timestamps.append(t_in_seconds)
  return timestamps

