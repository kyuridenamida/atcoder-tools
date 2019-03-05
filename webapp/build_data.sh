#!/usr/bin/env bash
mkdir -p ./src/auto_generated/
mkdir -p ./data_builder/out/
cd ./data_builder/
./prepare.sh
python3 -m compileall ./build_full_data.py
python3 ./__pycache__/build_full_data.*.pyc
