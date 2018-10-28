# Interface for object/person bounding boxes

import argparse
import os
import sys
from glob import glob
import cv2
import pickle
import numpy as np

import pdb

# NOTE: change keymap according to your computer
keymap = {
    'arrows':0,
    'j': 106, 'k': 107,
    ' ': 32, 'esc': 27,
    '0': 48, '1': 49, '2':50,
    ',/<': 44, './>': 46,
    '-/_': 45, '=/+': 61,
    '~': 96,
    'tab':9,
    'backspace':8,
}
CONFIG = {}
VERBOSE = False

COLOR = { # BGR
    'red': (0,0,255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'cyan': (255, 255, 0),
    'yellow': (0, 255, 255),
}


# Bounding box label configs.
bbox_globals = {
    'x1': 10,
    'y1': 10,
    'x2': 200,
    'y2': 200,
    'cx': 105,
    'cy': 105,
    'mouse_down': False,
}
BOX_THICKNESS = 2

obj_name = ''
obj_type = None
obj_type_map = {
    'person': 0,
    'chair': 1,
    'bed': 2,
}
obj_color_map = {
    0: COLOR['cyan'],
    1: COLOR['red'],
    2: COLOR['blue'],
}

centroid_globals = {
    'x': 10,
    'y': 10,
    'mouse_down': False,
}
DOT_RADIUS = 5
DRAGGING = False
LID, BID = None, None

BASE_IP = '10.233.219.'
DATE = None
OUT_DIR = None
OCEAN_PATH = None

prev_labels = [[], [], []]

PREV_FRAME = 0
FRAME_ID = 0
N_FRAMES = 0

def instructions():
    print("Welcome! :)")
    print("Here are some labeling instructions, you can turn them off next time using 'python annot_loc.py --instruct=0'.")
    print('1. When labeling: use the mouse / touch pad to drag a bbox over the object.')
    print('2. To remove some bbox from current frame:')
    print('  - press `Backspace` to undo the bbox you just drew.')
    print('  - press `Space` to remove all bboxes of the object type & newly added by you')
    print('  - press `Tab` to remove bboxes of the object type & loaded from pickle or carried over from other frames.')
    print('3. To exit: press "esc" then follow the prompts in the command line.')
    print('\nThank you so much for helping with labeling!! >u<\n\n')


def main(args):
    if args.instruct:
        instructions()
    # - Use mouse to drag bounding boxes
    global CONFIG, DATE, FRAME_ID, OUT_DIR
    global obj_name, obj_type, obj_type_map

    CONFIG = {
        'util': args.util,
        'IMG_DIR_BASE': args.IMG_DIR_BASE,
        'ANNOT_DIR_BASE': args.ANNOT_DIR_BASE,
    }

    annot_func = None
    if args.util == 'bboxes':
        annot_func = bboxes
    elif args.util == 'centroids':
        raise NotImplementedError("'centroids' is currently not available. Sorry! ^ ^b")
        annot_func = centroids
    else:
        raise NotImplementedError("args.util could only be 'bboxes'. Got {:s}. o_O".format(args.util))

    print os.getcwd()
    print os.path.join(CONFIG['IMG_DIR_BASE'] , args.date)

    if args.date:
        date_folders = glob(os.path.join(CONFIG['IMG_DIR_BASE'] , args.date))
    else:
        date_folders = sorted(glob(os.path.join(CONFIG['IMG_DIR_BASE'] , '18-*')))

    print('# dates:', len(date_folders))
    # pdb.set_trace()
    for date_folder in date_folders:
        print(date_folder)
        DATE = date_folder.split('\\')[-1] if '\\' in date_folder else date_folder.split('/')[-1]
        OUT_DIR = os.path.join(CONFIG['ANNOT_DIR_BASE'], DATE)
        os.makedirs(OUT_DIR)

        print('Current date:', DATE)
        sys.stdout.flush()
        print(os.path.join(date_folder, '*.jpg'))
        depth_frames = sorted(glob(os.path.join(date_folder, '*.png')))
        print('# depth_frames:', len(depth_frames))
        while True:
            obj_type = obj_type_map['person']
            annot_func(depth_frames)
            key_next = str(input("Exit current folder? (y/[n])"))
            if 'y' in key_next or 'Y' in key_next:
                FRAME_ID = 0
                break
        
        key_exit = str(input("Exit annotation tool? (y/[n])"))
        if 'y' in key_exit or 'Y' in key_exit:
            print('\nThank you for labeling~ Bye! =^_^=')
            sys.exit(0)


def bboxes(depth_frames):
    global CONFIG, DATE, FRAME_ID, N_FRAMES, PREV_FRAME, OUT_DIR, OCEAN_PATH
    global bbox_globals, ocean, obj_name, obj_type, prev_labels

    def save(labels, timestamp):
        labels_fqn = os.path.join(OUT_DIR, timestamp+'.p')
        flattened = [bbox for label in labels for bbox in label]
        with open(labels_fqn, 'wb') as handle:
            for bbox in flattened:
                if len(bbox) == 5:
                    cx = (bbox[0]+bbox[2]) // 2
                    cy = (bbox[1]+bbox[3]) // 2
                    bbox += [cx, cy]
                assert(len(bbox)==7), "bbox: {}".format(bbox)
            node_ids = np.asarray([label[-3] for label in flattened])
            bboxs = np.stack(flattened)[:, :-3] if flattened else np.zeros(0,)
            centroids = np.stack([[cx, cy] for _,_,_,_,_,cx,cy in flattened]) if flattened else np.zeros(0,)
            pickle.dump({'node_ids':node_ids, "node_centroid_2d":centroids, "node_bbox_2d":bboxs},
                handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load(timestamp):
        labels_fqn = os.path.join(OUT_DIR, timestamp+'.p')
        if os.path.exists(labels_fqn):
            with open(labels_fqn, 'rb') as f:
                labels = pickle.load(f)
                assert('node_ids' in labels and 'node_centroid_2d' in labels and 'node_bbox_2d' in labels)
                assert(len(labels['node_ids']) == len(labels['node_centroid_2d']) and len(labels['node_ids']) == len(labels['node_bbox_2d']))
                bboxes_with_ids = [list(labels['node_bbox_2d'][i]) + [labels['node_ids'][i]] + list(labels['node_centroid_2d'][i]) for i in range(len(labels['node_ids']))]
                return bboxes_with_ids
        else:
            return []

    N_FRAMES = len(depth_frames)

    # Define mouse callback attached to window.
    cv2.namedWindow(obj_name)
    cv2.setMouseCallback(obj_name, click)

    # Step through and annotate frames.
    while 0 <= FRAME_ID < N_FRAMES:
        # Display frame in ocean.
        OCEAN_PATH = depth_frames[FRAME_ID]
        ocean = cv2.imread(depth_frames[FRAME_ID])
        # NOTE: the 'if' statement in the following line is for checking Windows/Linux path format
        timestamp = depth_frames[FRAME_ID].split('\\')[-1].split('.')[0] if '\\' in depth_frames[FRAME_ID] else depth_frames[FRAME_ID].split('/')[-1].split('.')[0]
        labels = load(timestamp)
        currObj_loaded = [label for label in labels if label[-3]==obj_type]
        otherObj_loaded = [label for label in labels if label[-3]!=obj_type]
        labels = [currObj_loaded, otherObj_loaded, []]
        currObj_prev = [label for label in prev_labels[0]]
        sys.stdout.flush()
        if PREV_FRAME<FRAME_ID:
            if len(currObj_loaded) < len(currObj_prev):
                labels[0] = currObj_prev
        else:
            prev_labels = [[], [], []]
        bbox_globals['labels'] = labels  # Set the labels globally for current frame.

        # print('ocean size:', ocean.shape)
        cv2.putText(ocean, "{:d}/{:d}".format(FRAME_ID+1, N_FRAMES), (5, 15),
            cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=COLOR['yellow'])
        cv2.imshow(obj_name, ocean)

        refresh_frame()

        k = cv2.waitKey()
        # print(k)
        # sys.stdout.flush()
        # continue
        PREV_FRAME = FRAME_ID
        # Define general actions.
        if k == keymap[',/<'] or k == keymap['-/_'] or k == keymap['1']: # Go to previous frame
            FRAME_ID = FRAME_ID - 1 if FRAME_ID > 0 else FRAME_ID
        elif k == keymap['./>'] or k == keymap['=/+'] or k == keymap['2']:  # Go to next frame.
            FRAME_ID = FRAME_ID + 1 if FRAME_ID < N_FRAMES - 1 else FRAME_ID
        elif k == keymap[' ']: 
            # Clear boxes in the current frame that are
            # 1) of type obj_type and 2) newly added
            labels[-1] = []
        elif k == keymap['tab']:
            # Clear boxes in the current frame that are
            # 1) of type obj_type and 2) loaded from previous pickle or carried over from other frames.
            labels[0] = []
        elif k == keymap['backspace']:
            labels[-1] = labels[-1][:-1]
        elif k == keymap['esc']:  # Exit annotator tool.
            save(labels, timestamp)
            cv2.destroyWindow(obj_name)
            return
        sys.stdout.flush()
        save(labels, timestamp)
        prev_labels = labels
        prev_labels[0] += prev_labels[-1]
        prev_labels[-1] = []


def centroids(depth_frames, date):
    """
    NOTE: Deprecated.
    """
    global DATE

    def save(labels, timestamp):
        labels_fqn = os.path.join(CONFIG['out_dir'], 'centroid_{:s}_{:s}.p'.format(DATE, timestamp))
        with open(labels_fqn, 'wb') as handle:
            labels_nd = np.stack(labels)
            pickle.dump(labels_nd, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load(timestamp):
        labels_fqn = os.path.join(CONFIG['out_dir'], 'centroid_{:s}_{:s}.p'.format(DATE, timestamp))
        if os.path.exists(labels_fqn):
            with open(labels_fqn, 'rb') as f:
                labels = list(pickle.load(f))
                return labels
        else:
            return []

    global centroid_globals, ocean, obj_type
    n_frames = len(depth_frames)

    # Define initial configurations for the annotation tool.
    i = 0  # Frame index.
    wb = 100  # White balance.
    rotate = 0  # The frame rotation, which ranges from 0 to 4.

    # Define mouse callback attached to window.
    cv2.namedWindow(obj_name)
    cv2.setMouseCallback(obj_name, click)

    # Step through and annotate frames.
    while 0 <= i < n_frames:
        # Display frame in ocean.
        ocean = cv2.imread(depth_frames[i])
        timestamp = depth_frames[i].split('/')[-1].split('.')[0]
        labels = load(timestamp)
        centroid_globals['labels'] = labels  # Set the labels globally for current frame.

        print('%d / %d\tObjects: %d' % (i, n_frames, len(labels)))

        # print('ocean size:', ocean.shape)
        cv2.imshow(obj_name, ocean)

        # Draw previously labeled boxes.
        for point in labels:
            x, y, obj = point
            draw_point(x, y, obj)

        k = cv2.waitKey()
        # Define general actions.
        if k == keymap[',/<'] or k == keymap['-/_']: # Go to previous frame
            i = i - 1 if i > 0 else i
        elif k == keymap['./>'] or k == keymap['=/+']:  # Go to next frame.
            i = i + 1 if i < n_frames - 1 else i
        elif k == keymap[' ']:  # Clear boxes for current frame.
            remaining_centroids = []
            for centroid in labels:
                if centroid[-1] != obj_type:
                    remaining_centroids += centroid,
            labels = remaining_centroids
        elif k == keymap['esc']:  # Exit annotator tool.
            save(labels, timestamp)
            return
        save(labels, timestamp)


def refresh_frame():
    global ocean
    ocean = cv2.imread(OCEAN_PATH)

    flattened =  [bbox for label in bbox_globals['labels'] for bbox in label]

    if VERBOSE:
        print('labels:', flattened)
        print('%d / %d\tObjects: %d' % (FRAME_ID, N_FRAMES, len(flattened)))

    cv2.putText(ocean, "{:d}/{:d}".format(FRAME_ID+1, N_FRAMES), (5, 15),
        cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=COLOR['yellow'])
    # Draw all boxes on the current frame.
    for box in flattened:
        draw_box(*box)


def draw_box(x1, y1, x2, y2, obj, cx=None, cy=None, temp=False):
    global ocean, obj_name

    if cx is None or cy is None:
        cx = (x1+x2) // 2
        cy = (y1+y2) // 2

    if temp:
        ocean_temp = ocean.copy()
        cv2.rectangle(ocean_temp, (x1, y1), (x2, y2), COLOR['yellow'], BOX_THICKNESS)
        cv2.circle(ocean_temp, (cx, cy), DOT_RADIUS, COLOR['yellow'], -1)
        cv2.imshow(obj_name, ocean_temp)
    else:
        cv2.rectangle(ocean, (x1, y1), (x2, y2), obj_color_map[obj], BOX_THICKNESS)
        cv2.circle(ocean, (cx, cy), DOT_RADIUS, obj_color_map[obj], -1)
        cv2.imshow(obj_name, ocean)


def record_box(x1, y1, x2, y2, cx=None, cy=None):
    global bbox_globals, obj_type
    global LID, BID
    if cx is None or cy is None:
        cx = (x1+x2) // 2
        cy = (y1+y2) // 2
    if LID is not None and BID is not None:
        bbox_globals['labels'][LID][BID] = [x1, y1, x2, y2, obj_type, cx, cy]
    else:
        bbox_globals['labels'][-1].append([x1, y1, x2, y2, obj_type, cx, cy])
    # NOTE: put cx/cy at the end so that when unrolling a loaded previously labeled box,
    # cx/cy would appear at the end thus could be the optional arguments to draw_box


def get_box_coordinates():
    global bbox_globals

    x1, y1, x2, y2 = [bbox_globals[k] for k in ['x1', 'y1', 'x2', 'y2']]
    return x1, y1, x2, y2


def draw_point(x, y, obj, temp=False):
    global ocean, obj_name
    
    if temp:
        ocean_temp = ocean.copy()
        cv2.circle(ocean_temp, (x, y), DOT_RADIUS, COLOR['yellow'], -1)
        cv2.imshow(obj_name, ocean_temp)
    else:
        cv2.circle(ocean, (x, y), DOT_RADIUS, obj_color_map[obj], -1)
        cv2.imshow(obj_name, ocean)


def record_point(x, y):
    global centroid_globals, obj_type
    centroid_globals['labels'].append([x, y, obj_type])


def click(event, x, y, flags, param):
    global obj_type
    """The callback function that is called when the user clicks the window."""
    if CONFIG['util'] == 'bboxes':
        global bbox_globals, DRAGGING, BID, LID

        if DRAGGING:
            if event == cv2.EVENT_MOUSEMOVE:
                bbox = bbox_globals['labels'][LID][BID]
                bbox[-2] = x
                bbox[-1] = y
                draw_box(bbox[0], bbox[1], bbox[2], bbox[3], bbox[4], bbox[5], bbox[6], temp=True)
                refresh_frame()
            elif event == cv2.EVENT_LBUTTONUP:
                bbox = bbox_globals['labels'][LID][BID]
                bbox[-2] = x
                bbox[-1] = y
                draw_box(bbox[0], bbox[1], bbox[2], bbox[3], bbox[4], bbox[5], bbox[6], temp=False)
                refresh_frame()
                # record_box(bbox[0], bbox[1], bbox[2], bbox[3], bbox[5], bbox[6])
                DRAGGING = False
                LID = None
                BID = None
            return

        if event == cv2.EVENT_LBUTTONDOWN:  # Start drawing.
            for lid,bboxes in enumerate(bbox_globals['labels']):
                for bid,bbox in enumerate(bboxes):
                    if len(bbox) == 5:
                        cx = (bbox[0]+bbox[2]) // 2
                        cy = (bbox[1]+bbox[3]) // 2
                        bbox += [cx, cy]
                    assert(len(bbox)==7)
                    if abs(bbox[-2] -x) <= DOT_RADIUS and abs(bbox[-1]-y) <= DOT_RADIUS:
                        DRAGGING = True
                        LID = lid
                        BID = bid
                        return
            bbox_globals['mouse_down'] = True
            bbox_globals['x1'] = x
            bbox_globals['y1'] = y
        elif event == cv2.EVENT_MOUSEMOVE and bbox_globals['mouse_down']:  # Draw the rectangle so far.
            bbox_globals['x2'] = x
            bbox_globals['y2'] = y
            x1, y1, x2, y2 = get_box_coordinates()
            draw_box(x1, y1, x2, y2, obj_type, temp=True)
        elif event == cv2.EVENT_LBUTTONUP:  # Stop drawing.
            bbox_globals['mouse_down'] = False
            bbox_globals['x2'] = x
            bbox_globals['y2'] = y
            x1, y1, x2, y2 = get_box_coordinates()
            draw_box(x1, y1, x2, y2, obj_type)
            record_box(x1, y1, x2, y2)
    elif CONFIG['util'] == 'centroids':
        global centroid_globals
        if event == cv2.EVENT_LBUTTONDOWN:
            centroid_globals['x'] = x
            centroid_globals['y'] = y
            centroid_globals['mouse_down'] = True
        elif event == cv2.EVENT_MOUSEMOVE and centroid_globals['mouse_down']:  # Draw the rectangle so far.
            bbox_globals['x'] = x
            bbox_globals['y'] = y
            draw_point(x, y, obj_type, temp=True)
        elif event == cv2.EVENT_LBUTTONUP:  # Stop drawing.
            bbox_globals['mouse_down'] = False
            bbox_globals['x'] = x
            bbox_globals['y'] = y
            draw_point(x, y, obj_type)
            record_point(x, y)
    else:
        raise NotImplementedError("Right now we can only draw bboxes or centroids. Sorry! :/")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--instruct', default=1, type=int, help="Show instructions to labeling tool.")
    parser.add_argument('--IMG_DIR_BASE', default='', type=str, help='Base directory for depth images.')
    parser.add_argument('--ANNOT_DIR_BASE', default='labels/objects/', type=str, help='Base directory to save annotations in.')
    parser.add_argument('--date', default='', type=str, help='Date (e.g. 17-08-20) of the folder. Loop over all dates if not specified.')
    parser.add_argument('--util', default='bboxes', type=str, help="Type of annotations; currently only support 'bboxes'.")
    args = parser.parse_args()

    main(args)
