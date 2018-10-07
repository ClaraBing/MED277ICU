#!/bin/bash
depth_sensor="183"
thermal_sensor="caregiver_4"
year=18
month=04

for d in {05..07}
do
  date=${year}-${month}-${d}
  echo ${date}

  sudo python3 process_onlok_data.py ${date} -d -t     \
      --depth_sensor $depth_sensor                     \
      --thermal_sensor $thermal_sensor

  echo ''
done
