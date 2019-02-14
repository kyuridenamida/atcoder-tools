#!/usr/bin/env bash
mkdir -p ./src/auto_generated/
cd ./data_builder/
./prepare.sh
python3 ./build_full_data.py ../src/auto_generated/qualityResultList.js