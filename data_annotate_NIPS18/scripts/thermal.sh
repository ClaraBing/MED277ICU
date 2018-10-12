#!/bin/bash
thermal_sensor="caregiver_6"
year=18
month=04

# Download thermal videos from AWS
aws s3 cp s3://verzusdev/Users/${thermal_sensor}/unkown /data/onlok/thermal/${thermal_sensor} \
    --recursive --exclude "*" --include "20${year}*"
