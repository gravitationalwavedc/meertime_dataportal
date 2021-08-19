#!/bin/bash

pushd test-data/kronos
list=$(find . -name 'obs.header')
popd

for file in $list; do

  beam=$(echo $file | awk -F/ '{print $2}')
  utc=$(echo $file | awk -F/ '{print $3}')
  src=$(echo $file | awk -F/ '{print $4}')
  freq=$(grep ^FREQ test-data/kronos/$beam/$utc/$src/obs.header | awk '{printf("%.0f\n",$2)}')

  poetry run python ingest_ptuse_folding.py $beam $utc $src $freq

done
