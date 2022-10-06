#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd $parent_path

while [[ $# -gt 0 ]]; do
  case $1 in
    -url)
      PROM_URL="$2"
      shift
      shift
      ;;
    --benchmark)
      BENCHMARK="$2"
      shift
      shift
      ;;
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
    -a|--append)
      APPEND="-a"
      shift
      ;;
    --no)
      NO="-n"
      shift
      ;;
    --yes)
      YES="-y"
      shift
      ;;
    -s|--sleep)
      SLEEP="$2"
      shift
      shift
      ;;
    -o|--out)
      OUT="$2"
      shift
      shift
      ;;
    --tsv-out)
      TSV_OUT="$2"
      shift
      shift
      ;;
    -h|--help)
      echo "usage: Loop through all mlperf_gpu_pods and run the benchmarks
  options:
    -c|--config /path/to/kube_config
    -y|--yaml Path to the yaml file(s) (absolute)
    -b|--batch Number of pods to be deployed and benchmarked simultanouesly
    -a|--append Append times on folders' names
    --no Boolean argument to skip loop if files exist
    --yes Boolean argument to delete files if they exist
    -s|--sleep Number of seconds to sleep between each loop. Default=60 secs
    -url URL of prometheus service
    --benchmark Name for the benchmark
    --tsv-out Output folder for summarized metrics under /mlab-k8s-cluster-setup/prom_metrics_cli/plot/figures/ (dcgm_metrics_summary_ and mlperf_logs_summary_ will be prepended respectively)
    -o|--out Output folder for dcgm figures and mlperf logs. Default: /mlab-k8s-cluster-setup/prom_metrics_cli/plot/figures/$(date +'%Y_%m_%dT-%H:%mZ')"
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

if [ -z "$TSV_OUT" ]
then
    echo "--tsv-out can't be empty"
    exit 0
fi

if [ -z "$BENCHMARK" ]
then
    echo "--benchmark can not be empty"
fi


if [ -z "$OUT" ]
then
    OUT="$parent_path/../prom_metrics_cli/plot/figures/$(date +'%Y_%m_%dT-%H:%MZ')"
fi

if [ -z "$PROM_URL" ]
then
    PROM_URL="http://localhost:30090/"
fi

if [ -z "$BATCH" ]
then
    BATCH="1"
fi

if [ -z "$SLEEP" ]
then
    SLEEP="60"
fi

if ([ ! -z "$NO" ] && [ ! -z "$YES" ]) || ([ ! -z "$NO" ] && [ ! -z "$APPEND" ]) || ([ ! -z "$APPEND" ] && [ ! -z "$YES" ])
then
    echo "Only one from -n, -y and -a can be set at a time"
fi

if [ -z $YAML ]
then
  YAML="$PWD/mlperf_gpu_pods"
fi

./bin/main -c $CONFIG -b $BATCH -yaml $YAML $NO $YES $APPEND -s $SLEEP -url $PROM_URL -o $OUT
../prom_metrics_cli/plot/summarize_dcgm_metrics.py -i "$OUT" --benchmark "$BENCHMARK" --tsv-out "$parent_path/../prom_metrics_cli/plot/figures/dcgm_metrics_summary_$TSV_OUT"
../prom_metrics_cli/plot/summarize_mlperf_logs.py -i "$OUT" --benchmark "$BENCHMARK" --tsv-out "$parent_path/../prom_metrics_cli/plot/figures/mlperf_logs_summary_$TSV_OUT"
../prom_metrics_cli/plot/dcgm_metrics_heatmaps.py -i "$parent_path/../prom_metrics_cli/plot/figures/dcgm_metrics_summary_$TSV_OUT"
../prom_metrics_cli/plot/mlperf_logs_heatmaps.py -i "$parent_path/../prom_metrics_cli/plot/figures/mlperf_logs_summary_$TSV_OUT"
