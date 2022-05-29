#!/bin/bash

while [[ $# -gt 0 ]]; do
  case $1 in
    -c|--config)
      CONFIG="$2"
      shift
      shift
      ;;
    -y|--YAML)
      YAML="$2"
      shift
      shift
      ;;
    -b|--batch)
      BATCH="$2"
      shift
      shift
      ;;
    --no)
      NO="-n"
      shift
      shift
      ;;
    --yes)
      YES="-y"
      shift
      shift
      ;;
    -s|--sleep)
      SLEEP="$2"
      shift
      shift
      ;;
    -h|--help)
      echo "usage: Loop through all mlperf_gpu_pods and run the benchmarks
  options:
    -c|--config /path/to/kube_config
    -y|--yaml Path to the yaml file(s)
    -b|--batch Number of pods to be deployed and benchmarked simultanouesly
    --no Boolean argument to skip loop if files exist
    --yes Boolean argument to delete files if they exist
    -s|--sleep Number of seconds to sleep between each loop. Default=60 secs"
      exit 0
      ;;
    *)
      echo "Unknown argument $1"
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

if [ -z "$BATCH" ]
then
    BATCH="1"
fi

if [ -z "$SLEEP" ]
then
    SLEEP="60"
fi

if [ ! -z "$NO" ] && [ ! -z "$YES" ]
then
    echo "-n and -y can't be set simultaneously"
fi

if [ -z $YAML ]
then
  YAML="mlpref_gpu_pods"
fi

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

./bin/main -c $CONFIG -b $BATCH -yaml $PWD/$YAML $NO $YES -s $SLEEP
