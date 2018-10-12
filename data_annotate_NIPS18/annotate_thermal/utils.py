from __future__ import absolute_import, division, print_function, unicode_literals
import cv2
import numpy as np
import os
import time

# Support MAC and Linux
KEYMAP = {
  'left': [65361, 2],
  'up': [65362, 0],
  'right': [65363, 3],
  'down': [65364, 1],
}


def imread(image_path, white, resize=1):
  image = cv2.imread(image_path)
  image = np.clip(image, 0, white)/white*255
  image = np.array(image, dtype=np.uint8)
  image = cv2.applyColorMap(image, cv2.COLORMAP_OCEAN)
  image = cv2.resize(image, (0, 0), fx=resize, fy=resize, interpolation=cv2.INTER_NEAREST)
  return image

def read_video(video_path, upside_down=True):
  cap = cv2.VideoCapture(video_path)
  if not cap.isOpened():
    raise Exception("Unable to open {}".format(video_path))

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

def visualize_thermal(img):
  img = cv2.resize(img, (0, 0), fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
  upper = max(img.max(), 55)
  lower = min(img.min(), 35)
  img = ((img - lower) / (upper - lower) * 255).astype(np.uint8)
#  img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
  return img

def visualize_depth(img, white):
  img = (np.clip(img, 0, white) / white * 255).astype(np.uint8)
  img = cv2.applyColorMap(img, cv2.COLORMAP_OCEAN)
  img = cv2.resize(img, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
  return img

def visualize(thermal_image, white):
  thermal_image = visualize_thermal(thermal_image)
  # depth_image = visualize_depth(depth_image, white)
  # final = np.concatenate([depth_image, thermal_image], axis=1)
  return thermal_image

def makedir(directory):
  if not os.path.isdir(directory):
    os.mkdir(directory)

def get_time_str(t):
  """ t is in milliseconds """
  t_in_seconds = t / 1000
  ms = t % 1000
  time_str = time.strftime("%H:%M:%S", time.localtime(t_in_seconds)) + "." + str(ms)
  return time_str

def rotate(image, deg):
  if deg == 0:
    return image
  elif 1 <= deg <= 3:
    return np.rot90(image, deg).copy()
  else:
    raise NotImplementedError


def draw_info(image, task_state, video_state):
  color = (255, 255, 255) if video_state.white else (0, 0, 0)

  image_info = 'Sensor: {}, Frame {}/{}'.format( \
      video_state.thermal_sensor, video_state.frame_id+1, video_state.num_frames)
  cv2.putText(image, image_info, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

  time_info = 'Date: {}. Times: thermal: {}'.format(\
      task_state.date, video_state.thermal_time)
  cv2.putText(image, time_info, (5, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

  label_info = ['{}: {}/{}'.format(task_state.actions[action_id],
                                   video_state.frame_id-start+1, end-start+1)
                for (start, end, action_id) in video_state.clips 
                    if start <= video_state.frame_id <= end]
  if len(label_info) == 0:
    label_info = ['None']
  for i, row in enumerate(label_info):
    cv2.putText(image, row, (5, 55+i*20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


def orange_fg(text1, text2=''):
  print('\033[94m'+text1+'\033[0m'+text2)


def yellow_fg(text1, text2=''):
  print('\033[93m'+text1+'\033[0m'+text2)


def red_fg(text1, text2=''):
  print('\033[91m'+text1+'\033[0m'+text2)


def orange_fg(text1, text2='', newline=True):
  if newline:
    print('\033[33m'+text1+'\033[0m'+text2)
  else:
    print('\033[33m'+text1+'\033[0m'+text2, end='')


def blue_bg(text1, text2=''):
  print('\033[44m'+text1+'\033[40m'+text2)


def purple_fg(text1, text2=''):
  print('\033[45m'+text1+'\033[40m'+text2)


def red_bg(text1, text2=''):
  print('\033[41m'+text1+'\033[40m'+text2)


def print_info(task_state, video_state):
  os.system('clear')
  blue_bg('\n           Instructions           ')
  orange_fg('\u21e6 / \u21e8:\t', '1 frame backward/forward')
  orange_fg('\u21e9 / \u21e7:\t', '10 frame backward/forward')
  orange_fg('< / >:\t', '100 frame backward/forward')
  orange_fg('[ / ]:\t', 'Previous/next task')
  orange_fg('- / +:\t', 'Adjust white balance')
  orange_fg('Space:\t', 'Toggle text color')
  orange_fg('Esc:\t', 'Exit')
  orange_fg('s / e:\t', 'Start/End of action')
  orange_fg('0-9:\t', 'Current Action ID')
  orange_fg('a:\t', '[User Input] Current Action ID')
  orange_fg('r:\t', '[User Input] Remove Clip ID')
  orange_fg('t / f:\t', '[User Input] Jump to Task/Frame ID')
  red_fg('Hint:\t', '(a) Turn off Caps Lock  (b) No need for shift  (c) Active window set to video')

  blue_bg('\n              State               ')
  orange_fg('Date: ', '{}\t'.format(task_state.date), newline=False)
  orange_fg('Thermal Sensor: ', '{}'.format(video_state.thermal_sensor))
  # orange_fg('Depth Sensor: ', '{}'.format(video_state.depth_sensor))
  orange_fg('Task ID: ', '{}/{}\t'.format(task_state.task_id+1, task_state.num_tasks), newline=False)
  orange_fg('Frame ID: ', '{}/{}'.format(video_state.frame_id+1, video_state.num_frames))
  orange_fg('Start of action: ', str(video_state.start+1))
  orange_fg('Current Action: ', str(task_state.actions[video_state.action_id]))

  blue_bg('\n              Action              ')
  for action_id, action in enumerate(task_state.actions):
    orange_fg('Action {}: '.format(action_id+1), action)

  blue_bg('\n           Annotations            ')
  for clip_id, (start, end, action_id) in enumerate(video_state.clips):
    orange_fg('Clip {}: '.format(clip_id+1), '[{}, {}], {}'.format(start+1, end+1, task_state.actions[action_id]))


def get_user_input(prompt):
  while True:
    user_input = input(prompt)
    try:
      tmp = int(user_input)
      return tmp
    except ValueError:
      print('Not a number')


def read_key(key, task_state, video_state):
  """
  :param key: keycode
  :param task_state:
  :param video_state:
  :return: end annotation (-1); continue the task (0); new task (1)
  """
  print(key)
  if key in KEYMAP['left']:
    video_state.frame_id -= 1
    video_state.frame_id = min(max(0, video_state.frame_id), video_state.num_frames-1)

  elif key in KEYMAP['right']:
    video_state.frame_id += 1
    video_state.frame_id = min(max(0, video_state.frame_id), video_state.num_frames-1)

  elif key in KEYMAP['up']:
    video_state.frame_id -= 10
    video_state.frame_id = min(max(0, video_state.frame_id), video_state.num_frames-1)

  elif key in KEYMAP['down']:
    video_state.frame_id += 10
    video_state.frame_id = min(max(0, video_state.frame_id), video_state.num_frames-1)

  elif key == ord(','):  # <
    video_state.frame_id -= 100
    video_state.frame_id = min(max(0, video_state.frame_id), video_state.num_frames-1)

  elif key == ord('.'):  # >
    video_state.frame_id += 100
    video_state.frame_id = min(max(0, video_state.frame_id), video_state.num_frames-1)

  elif key == ord('\x1b'):  # esc
    video_state.save()
    return -1

  elif key == ord('s'):  # start
    video_state.start = video_state.frame_id

  elif key == ord('e'):  # end
    if video_state.start >= 0:
      clip = (video_state.start, video_state.frame_id, video_state.action_id)
      video_state.clips.append(clip)
      video_state.start = -1

  elif key == ord('a'):  # action
    tmp = get_user_input('Enter the Action ID: ')-1
    if 0 <= tmp < task_state.num_actions:
      video_state.action_id = tmp

  elif ord('0') <= key <= ord('9'):  # action
    tmp = key-ord('0')-1
    if 0 <= tmp < task_state.num_actions:
      video_state.action_id = tmp

  elif key == ord('r'):  # remove
    tmp = get_user_input('Enter the Remove Clip ID: ')-1
    if 0 <= tmp < len(video_state.clips):
      video_state.clips.pop(tmp)

  elif key == ord('f'):  # jump to frame
    tmp = get_user_input('Enter the Frame ID: ')-1
    if 0 <= tmp < video_state.num_frames:
      video_state.frame_id = tmp

  elif key == ord('t'):  # jump to task
    tmp = get_user_input('Enter the Task ID: ')-1
    if 0 <= tmp < task_state.num_tasks:
      task_state.task_id = tmp
    return 1

  elif key == ord(']'):  # next video
    task_state.task_id += 1
    task_state.task_id = min(max(0, task_state.task_id), task_state.num_tasks-1)
    video_state.save()
    return 1

  elif key == ord('['):  # previous video
    task_state.task_id -= 1
    task_state.task_id = min(max(0, task_state.task_id), task_state.num_tasks-1)
    video_state.save()
    return 1

  elif key == ord('-'):  # white balance down
    video_state.white_balance -= 8
    video_state.white_balance = min(max(0, video_state.white_balance), 255)

  elif key == ord('='):  # white balance up
    video_state.white_balance += 8
    video_state.white_balance = min(max(0, video_state.white_balance), 255)

  elif key == ord(' '):  # toggle text color
    video_state.white = not video_state.white

  return 0
