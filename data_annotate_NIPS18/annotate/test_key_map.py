import cv2
import sys
import numpy as np

img = np.zeros([256,256])
targets = {
  '<':0,
  '>':0,
  'j':0,
  'k':0,
  '-':0,
  '+':0,
  '[':0,
  ']':0,
  ' ':0,
  'esc':0,
  'tab':0,
  'backspace':0,
}

for key in targets:
 cv2.imshow('test', img)
 print(key, end=':')
 sys.stdout.flush()
 inp = cv2.waitKey(0)
 print(inp)
 sys.stdout.flush()
