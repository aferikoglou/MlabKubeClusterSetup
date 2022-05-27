#!/bin/bash

while [[ $# -gt 0 ]]; do
  case $1 in
    -c|--config)
      CONFIG="$2"
      shift
      shift
      ;;
    -n)
      NO="$1"
      shift
      shift
      ;;
    -y)
      YES="$1"
      shift
      shift
      ;;
    -h|--help)
      echo "usage: Loop through all mlperf_gpu_pods and run the benchmarks
  options:
    -c  /path/to/kube_config
    -n skip loop if files exist
    -y delete files if exist"
      exit 0
      ;;
    *)
      echo "Unknown argument $1"
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

if [ ! -z "$NO" ] && [ ! -z "$YES" ]
then
    echo "-n and -y can't be set simultaneously"
fi

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

# kubectl port-forward -n prometheus svc/prometheus-operated 9090
for YAML in mlpref_gpu_pods/*;
do
    echo "File: $YAML"
    ./bin/main -c $CONFIG -yaml $PWD/$YAML $NO $YES
    echo -e "\n"
done
