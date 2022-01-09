import cv2 as cv
import numpy as np

frames_per_seconds = 60

# fungsi zoom in

def zoomFollowFace(frame, face_cascade: cv.CascadeClassifier):
  frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
  frame_gray = cv.equalizeHist(frame_gray)  # normalisasi

  # Detect faces
  faces = face_cascade.detectMultiScale(frame_gray)
  for (x, y, w, h) in faces:
    y2 = y-50 if y > 50 else y
    frame = frame[y2:y+h+30, x:x+h]
    break
  return frame

def verify_alpha_channel(frame):
  try:
    frame.shape[3]  # looking for the alpha channel
  except IndexError:
    frame = cv.cvtColor(frame, cv.COLOR_BGR2BGRA)
  return frame


def apply_senja(frame, intensity=0.5):
  frame = verify_alpha_channel(frame)
  frame_h, frame_w, frame_c = frame.shape
  senja_bgra = (20, 66, 112, 1)
  overlay = np.full((frame_h, frame_w, 4), senja_bgra, dtype='uint8')
  cv.addWeighted(overlay, intensity, frame, 1.0, 0, frame)
  frame = cv.cvtColor(frame, cv.COLOR_BGRA2BGR)
  return frame

def put_hat(hat, fc, x, y, w, h):
  face_width = w
  face_height = h

  hat_width = face_width + 1
  hat_height = int(0.50 * face_height) + 1

  hat = cv.resize(hat, (hat_width, hat_height))

  for i in range(hat_height):
    for j in range(hat_width):
      for k in range(3):
        if hat[i][j][k] < 235:
          fc[y + i - int(0.40 * face_height)][x + j][k] = hat[i][j][k]
  return fc


def put_glass(glass, fc, x, y, w, h):
  face_width = w
  face_height = h

  hat_width = face_width + 1
  hat_height = int(0.50 * face_height) + 1

  glass = cv.resize(glass, (hat_width, hat_height))

  for i in range(hat_height):
    for j in range(hat_width):
      for k in range(3):
        if glass[i][j][k] < 235:
          fc[y + i - int(-0.20 * face_height)][x + j][k] = glass[i][j][k]
  return fc

def resizeToDesiredSize(frame, width, height):
  fheight, fwidth = frame.shape[:2]
  blank_image = np.zeros((height, width, 3), np.uint8)
  blank_image[:,:] = (0,0,0)

  x_offset = 0 if fwidth == width else width//2 - fwidth//2
  y_offset = 0 if fheight == height else height//2 - fheight//2

  blank_image[y_offset:y_offset+fheight, x_offset:x_offset+fwidth] = frame.copy()
  return blank_image


def main(input, name):

  # Load the cascades
  face_cascade = cv.CascadeClassifier()
  eyes_cascade = cv.CascadeClassifier()
  face_default_cascade = cv.CascadeClassifier()

  # memanggil fungsi glass and hat
  if not face_cascade.load('./cv_project/cv/data/haarcascade_frontalface_alt.xml'):
    print('[!!] Error loading face cascade')
    exit()

  if not eyes_cascade.load('./cv_project/cv/data/haarcascade_eye_tree_eyeglasses.xml'):
    print('[!!] Error loading eyes cascade')
    exit()

  if not face_default_cascade.load('./cv_project/cv/data/haarcascade_frontalface_default.xml'):
    print('[!!] Error loading face default cascade')
    exit()
    
  hat=cv.imread('./cv_project/cv/Filters/hat.png')
    
  glass=cv.imread('./cv_project/cv/Filters/glasses.png')

  if hat is None:
    print('[!!] Error open hat.png')
    exit()
  if glass is None:
    print('[!!] Error open glass.png')
    exit()

  # camera
  cap = cv.VideoCapture('.{}'.format(input))
  # cap = cv.VideoCapture(0)
  _, frame = cap.read()
  fshape = frame.shape
  fheight = fshape[0]
  fwidth = fshape[1]

  fourcc = cv.VideoWriter_fourcc(*'MPEG')
  out = cv.VideoWriter('{}.avi'.format(name), fourcc, 15, (fwidth, fheight))

  cap.set(cv.CAP_PROP_BUFFERSIZE,3)

  if not cap.isOpened:
    print("[!!] Cannot open camera")
    exit()

  # while ret:
  while True:
    ret, frame = cap.read()

    if not ret:
      print("[!!] Can't receive frame, Exiting ...")
      break

    # manipulate the frame(menu)
    frame = cv.flip(frame, 1)

    # zoom
    frame = zoomFollowFace(frame, face_cascade)

    # hat and glasses
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    fl = face_default_cascade.detectMultiScale(gray,1.19,7)

    for (x, y, w, h) in fl:
      frame = put_hat(hat, frame, x, y, w, h)
      frame = put_glass(glass, frame, x, y, w, h)

    #filter
    frame = apply_senja(frame)

    frame = resizeToDesiredSize(frame, fwidth, fheight)
    out.write(frame)
    # cv.imshow('frame', frame)
    key_input = cv.waitKey(1)
    if key_input == ord('q'):
      break

  cap.release()
  out.release()
