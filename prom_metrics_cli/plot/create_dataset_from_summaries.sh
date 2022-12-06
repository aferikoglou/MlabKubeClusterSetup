#!/bin/bash

for summary in ./summary/*
do
    echo $summary
    ./dataset.py -i $summary
done
