#!/bin/bash
python -m annotate.run $1 --date=18-01-01 --sensor=171 

# python -m annotate.run $1   \
#   --depth_sensor 188              \
#   --thermal_sensor caregiver_6    \
#   --data_root_dir C:\\Users\\Bingbin\\Pictures\\onlok\\

#echo 'Processing annotations'
#for d in {06..06}
#do
#  /usr/bin/python3 -m data.process_annotations 17-11-${d} --overwrite
#done
