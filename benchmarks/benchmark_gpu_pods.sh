#!/bin/bash

while [[ $# -gt 0 ]]; do
  case $1 in
    -c|--config)
      CONFIG="$2"
      shift
      shift
      ;;
    -h|--help)
      echo "usage: Loop through all mlperf_gpu_pods and run the benchmarks
  options:
    -c  /path/to/kube_config"
      exit 0
      shift
      shift
      ;;
    *)
      shift
      shift
      ;;
    esac
done

if [ -z "$CONFIG" ]
then
    echo "-c|--config argument not set, default: CONFIG=/root/.kube/config"
    CONFIG="/root/.kube/config"
fi

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

for YAML in mlpref_gpu_pods/*;
do
    echo "File: $YAML"
    ./bin/main -c $CONFIG -y $PWD/$YAML
    echo -e "\n"
done
