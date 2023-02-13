#!/bin/bash

for file in ./summary/*
do
    if [[ ! $file == *".ods"* ]]; then
        continue
    fi
    echo $file
    ./barplot.py -i $file # -x-axis
done
