# Senior Home Data Processing

## Process raw data

**Make sure everythig is run with python3 in this directory.**

The date format must be YY-MM-DD. Here we use 17-11-06 as example.
Note: the default depth sensor is 188, and the default thermal sensor is caregiver_6.

1. Unzip depth files
    
   Modify the dates in `scripts/depth.sh` and run
    ```
    ./scripts/depth.sh
    ```

   or directly run the command
    ```
    sudo python3 -m data.untar 17-11-06
    ```

2. Download thermal videos

   Modify the sensor ID and dates in `scripts/thermal.sh` and run
    ```
    ./scripts/thermal.sh
    ```

   or directly run the command
    ```
    aws s3 cp s3://verzusdev/Users/caregiver_6/unkown /data/onlok/thermal/caregiver_6 --recursive --exclude "*" --include "2017-11-06*"
    ```
   **Thermal video time is in UTC. Remember to download data from the next day!!** (If today is 2017-11-06, download data from 2017-11-07 as well).

3. Process depth and thermal, and match the timestamps between depth and thermal frames.

   Modify the depth and thermal sensor IDs, dates, and flags in `scripts/data.sh`, and run
    ```
    ./scripts/data.sh
    ```

   Flags

   `-d`: Reorganize depth images to `/data/onlok_processed/depth/` and generate a depth task file.
    ```
    sudo python3 -m process_onlok_data 17-11-06 -d
    ```

   `-t`: Process and store thermal videos in `/data/onlok_processed/thermal/`, and generate a thermal task file.
    ```
    sudo python3 -m process_onlok_data 17-11-06 -t
    ```

   `-m`: Match thermal times to depth times.
    ```
    sudo python3 -m process_onlok_data 17-11-06 -m
    ```

## Annotation
Make sure to use X11 forwarding.
```
sudo python3 -m annotate.run 17-11-06
```

A window will pop up and follow the instructions to annotate data.

## Generate annotated dataset
The annotations are stored in /data/onlok_processed/. The next step is to organize the annotated frames into a dataset. The dataset is (by default) /data/onlok_annotated/, and the dataset structure is
- Action (ex. sleeping_on_bed)
  - Instance name (ex. 20171106_061708_caregiver_6_188)
    - depth
      - D-00000001.jpg
      - D-00000002.jpg
      - ...
    - thermal
      - T-00000001.png
      - T-00000002.png
      - ...

Run the following for a specific date.
```
python -m process_annotations 17-11-06
```

