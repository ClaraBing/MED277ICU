#!/bin/bash
year=18
month=03

for d in {31..31}
do
  date=${year}-${month}-${d}
  echo ${date}

  # Unzip files and create data.txt
  sudo python3 -m untar ${date}

  echo ''
done
