'''
Creates CSV dataset for depth data with
video | frame | image_path | label
'''
from pathlib import Path
import os
import numpy as np
import csv

DATA_ROOT= 'data/'
CSV_FILE = "videos2.csv"
RESULT_ROOT = "result"
csv_columns = ['Video_name', 'Frame', 'Image_path', 'Label']
pathlist = Path('data/''').glob('**/*.jpg')


# Aggregate labels from all CSV files
labels = {}
result_folders = os.listdir(RESULT_ROOT)
for folder in result_folders:
    if os.path.isdir(os.path.join(RESULT_ROOT, folder)):
        print(folder)
        camera_folders = os.listdir(os.path.join(RESULT_ROOT, folder))
        for camera in camera_folders:
            result_folder = os.path.join(RESULT_ROOT, folder, camera)
            result_csvs = os.listdir(result_folder)
            num_csvs = len(result_csvs)
            labels[camera] = []
            for i in range(num_csvs):
                with open(os.path.join(result_folder, str(i) + '.csv'), 'r') as csvfile:
                    labelreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                    for row in labelreader:
                        if len(row) == 3:
                            for j in range(int(row[0]), int(row[1]) + 1):
                                labels[camera].append(int(row[2]))

# Aggregate file names for all labeled data:
frames = {}
for name in labels.keys():
    details = name.split("_")
    date = details[0]
    camera = details[1]
    folder_path = os.path.join(DATA_ROOT, date, "10.233.219."+camera)
    if os.path.isdir(folder_path):
        all_frames = os.listdir(folder_path)
        all_frames.sort()
        frames[name] = all_frames
    else:
        print("[*] Error data not found at {}".format(folder_path))

with open(CSV_FILE, "w") as data_file:
    writer = csv.DictWriter(data_file, fieldnames=csv_columns, delimiter=' ')
    writer.writeheader()
    for k, v in frames.items():
        assert(len(v) == len(labels[k])), "Number of labels and images don't match for video {}: {} v. {}".format(
            k,
            len(v),
            len(labels[k])
        )
        details = k.split("_")
        date = details[0]
        camera = details[1]
        for (i, x) in enumerate(v):
            writer.writerow({
                'Video_name': k,
                'Frame': i,
                'Image_path': os.path.join(date, "10.233.219." + camera, x),
                'Label': labels[k][i]})
