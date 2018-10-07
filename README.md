## Prerequisite
* Python 3
* OpenCV (i.e. able to `import cv2`)

## Data:
* 4.5G    18-01-01 -- Eric
* 7.3G    18-01-02 -- Laetitia
* 3.2G    18-02-01 -- Zaid
* 4.8G    18-02-02 -- Kye
* 5.8G    18-02-03 -- Ruchir
* 2.6G    18-03-01 -- Avishi
* 4.1G    18-03-02
* 2.3G    18-03-03
* 773M    18-03-04

## Steps
1. Please scp the corresponding folder (under `/data/icu/raw`) and scripts (`~/untar.py` and `~/data_annotate_NIPS18`) to your local machine (edited)

2. Prepare folder structure on your local machine:
* create a folder named e.g. `labeling_party`
* `cd` into `labeling_party`
* create a subfolder named `raw`
* put your data (e.g. `18-03-01`) under `labeling_party/raw`
* put scripts (`untar.py` and `data_annotate_NIPS18`) under `labeling_party`

3. Find the keymap for your machine: please run `data_annotate_NIPS18/annotate/test_key_map.py`, press keys following the prompts, and update the values in dictionary `KEYMAP` in `data_annotate_NIPS18/annotate/utils.py`.

4. To start the labeling interface:
* `cd data_annotate_NIPS18`
* Modify `scripts/annotate.sh`: update `date` and `sensor`.
* run `./scripts/annotate.sh`, or directly run `python -m annotate.run --date={your_date} --sensor={your_sensor}`, e.g. `python -m annotate.run --date=18-01-01 --sensor=171`
