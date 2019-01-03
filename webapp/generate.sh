#!/usr/bin/env bash

copy_file(){
    echo "Copying $1 to $2"
    cp $1 $2
}
auto_gen_dir=./src/auto_generated/
rm -r ${auto_gen_dir}
mkdir -p ${auto_gen_dir}

copy_file ../README.md ${auto_gen_dir}