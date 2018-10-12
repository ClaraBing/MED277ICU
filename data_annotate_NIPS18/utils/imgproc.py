import cv2
import numpy as np
from scipy import interpolate

def inpaint(img, threshold=5):
  h, w = img.shape[:2]

  if len(img.shape) == 3:  # RGB
    mask = np.all(img == 0, axis=2).astype(np.uint8)
    img = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

  else:  # depth
    mask = np.where(img > threshold)
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))
    xym = np.vstack((np.ravel(xx[mask]), np.ravel(yy[mask]))).T
    img = np.ravel(img[mask])
    interp = interpolate.NearestNDInterpolator(xym, img)
    img = interp(np.ravel(xx), np.ravel(yy)).reshape(xx.shape)

  return img

def resize(video, size, interpolation):
  """
  :param video: ... x h x w x num_channels
  :param size: (h, w)
  :param interpolation: 'bilinear', 'nearest'
  :return:
  """
  shape = video.shape[:-3]
  H, W, num_channels = video.shape[-3:]
  video = video.reshape((-1, H, W, num_channels))
  resized_video = np.zeros((video.shape[0], size[0], size[1], video.shape[-1]))
  if interpolation == 'nearest':
    interpolation = cv2.INTER_NEAREST
  elif interpolation == 'bilinear':
    interpolation = cv2.INTER_LINEAR
  else:
    raise NotImplementedError

  for i in range(video.shape[0]):
    if num_channels == 3:
      resized_video[i] = cv2.resize(video[i], size, interpolation=interpolation)
    elif num_channels == 2:
      resized_video[i, ..., 0] = cv2.resize(video[i, ..., 0], size, interpolation=interpolation)
      resized_video[i, ..., 1] = cv2.resize(video[i, ..., 1], size, interpolation=interpolation)
    elif num_channels == 1:
      resized_video[i, ..., 0] = cv2.resize(video[i, ..., 0], size, interpolation=interpolation)
    else:
      raise NotImplementedError

  shape = shape + size + (video.shape[-1],)
  return resized_video.reshape(shape)

