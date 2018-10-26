'''
Verifies consistency of annotations by making sure every frame has exactly one label
'''
import os
import csv
import math
def verify(image_dir='data/', label_dir='result/', date='17-06-09', camera='176'):

    # image_folder = os.path.join(image_dir, date, '10.233.219.' + camera)
    # # print(image_folder)
    # images = os.listdir(image_folder)
    # images.sort()
    # # print(images)
    result_folder = os.path.join(label_dir, 'results64_' + date, date + "_" + camera)
    print("[*] Verifying labels from ", result_folder)
    if not os.path.isdir(result_folder):
        print("[*] Annotations not found ... skipping")
        return
    result_csvs = os.listdir(result_folder)
    num_csvs = len(result_csvs)

    # labels = [None for _ in range(len(images))]
    # batch_size = 500
    # num_iters = math.ceil(len(images) / batch_size)
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
    dates = ['18_04_18']
    # dates = ['17-06-04', '17-06-09', '17-06-10', '17-06-14', '17-06-16', '17-06-17']
    cameras = ['237', '157']
    for date in dates:
        for camera in cameras:
            verify(date=date, camera=camera)
