#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd $parent_path

for file in ./summary/*
do
    if [[ ! $file == *".ods"* ]]; then
        continue
    fi
    echo $file
    ./barplot.py -i $file -x-axis configuration
done
