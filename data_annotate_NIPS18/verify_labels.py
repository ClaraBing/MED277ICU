'''
Verifies consistency of annotations by making sure every frame has exactly one label
'''
import os
import csv
import math
def verify(image_dir='data/', label_dir='result/', date='17-06-09', camera='176'):

    result_folder = os.path.join(label_dir, 'results64_' + date, date + "_" + camera)
    print("[*] Verifying labels from ", result_folder)
    if not os.path.isdir(result_folder):
        print("[*] Annotations not found ... skipping")
        return
    result_csvs = os.listdir(result_folder)
    num_csvs = len(result_csvs)

    for i in range(num_csvs):
        is_CSV_malformed = False
        with open(os.path.join(result_folder, str(i) + '.csv'), 'r') as csvfile:
            labelreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            labels = [None for _ in range(500)]
            for row in labelreader:
                if len(row) < 3:
                    if not is_CSV_malformed:
                        print("[*] CSV {} has malformed row {}".format(i, row))
                    is_CSV_malformed = True
                else:
                    for j in range(int(row[0]), int(row[1]) + 1):
                        if labels[j] is None:
                            labels[j] = int(row[2])
                        else:
                            print("[*] Labeling error, image {} in task {} was already labeled with {} and is now labeled with {}".format(j, i, labels[j], row[2]))
    print("[*] Done.")
if __name__ == '__main__':
    dates = ['17-06-03', '17-06-04', '17-06-06', '17-06-09', '17-06-10', '17-06-14', '17-06-16', '17-06-17', '17-06-18', '17-06-19']
    cameras = ['176', '157']
    for date in dates:
        for camera in cameras:
            verify(date=date, camera=camera)
