#!/bin/bash

for file in ./summary/*
do
    if [[ ! $file == *".ods"* ]]; then
        continue
    fi
    echo $file
    ./dataset.py -i $file
done
