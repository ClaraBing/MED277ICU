import os
from glob import glob
import csv
import pickle
import argparse

ACT_DELETE = 7

parser = argparse.ArgumentParser()

parser.add_argument('--date', type=str)
parser.add_argument('--task_size', default=64, type=int, help="Number of frames in each clip. Default as 64.")
parser.add_argument('--one_file', required=1, type=int, help="Whether to produce a single txt files or break down by clips. Required argument.")
parser.add_argument('--depth_sensor1', default='237')
parser.add_argument('--depth_sensor2', default='238')
parser.add_argument('--pCLoud_path', type=str, default='/vision/group/intermountain/sim2/pc/{:s}/fps3/', help="path to be put in the output pkl file.\n"
	+ "Models will use these paths to locate the point clouds (*.npy).")

args = parser.parse_args()

in_results_root = '/mnt/c/Users/Bingbin/csPrograms/PAC/ICU/sim2/' # for input csv files and output txt files
out_results_root = in_results_root if args.one_file else os.path.join(in_results_root, 'label_clip{:d}_{:s}'.format(args.task_size, args.date))
if not os.path.exists(out_results_root):
	os.mkdir(out_results_root)
print('Results saved under', out_results_root)
in_csv_dir = os.path.join(in_results_root, 'results{:d}_{:s}/{:s}_{:s}/'.format(args.task_size, args.date, args.depth_sensor1, args.depth_sensor2))
in_match_file = os.path.join(in_results_root, 'match{:d}_{:s}_{:s}_{:s}.pkl'.format(args.task_size, args.depth_sensor1, args.depth_sensor2, args.date))

def read_csv(file_path):
  with open(file_path, 'r') as f:
    reader = csv.reader(f)
    data = [[int(x) for x in row] for row in reader if row]
  return data

def parse(args):
	pkl = pickle.load(open(in_match_file, 'rb'))

	delete_cnt = 0

	for cid,clip in enumerate(pkl):
		if not args.one_file:
			out_txt = os.path.join(out_results_root, 'match{:d}_2views_{:d}_{:s}.txt'.format(args.task_size, cid, args.date))
			fout = open(out_txt, 'w')
		else:
			out_txt = os.path.join(out_results_root, 'match{:d}_2views_{:s}.txt'.format(args.task_size, args.date))
			fout = open(out_txt, 'a')
		csv_file = os.path.join(in_csv_dir, '{:d}.csv'.format(cid))
		csv_labels = read_csv(csv_file)
		clip_labels = {}
		for start,end,act in csv_labels:
			has_delete = False
			if act == ACT_DELETE:
				# Throw away the entire clip if it contains frames markded as delete
				print("Delete:", csv_file)
				delete_cnt += 1
				has_delete = True
				break
			for fid in range(start, end+1):
				clip_labels[clip[fid]] = act
		if has_delete:
			continue
		for frame in sorted(clip_labels.keys()):
			fout.write('{:s} {:d}\n'.format(os.path.join(args.pCLoud_path, '{:d}.npy'.format(frame)), clip_labels[frame]))
		fout.close()

	print('# deleted clips:', delete_cnt)

if __name__ == '__main__':
	parse(args)