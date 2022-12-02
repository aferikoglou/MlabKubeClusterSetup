#!/bin/bash

for x in ./summary/*
do
    ./barplot.py -i $x
done
