#!/bin/bash

while [[ $# -gt 0 ]]; do
  case $1 in
    -url)
      PROM_URL="$2"
      shift
      shift
      ;;
    --out-dir)
      OUT_DIR="--out-dir $2"
      shift
      shift
      ;;
    -step)
      STEP="$2"
      shift
      shift
      ;;
    -i|--interval)
      INTERVAL="$2"
      shift
      shift
      ;;
    -o|--output)
      OUT="$2"
      shift
      shift
      ;;
    -e|--end)
      END="$2"
      shift
      shift
      ;;
    -s|--start)
      START="$2"
      shift
      shift
      ;;
    -f|--filter)
      FILTER="$2"
      shift
      shift
      ;;
    --total)
      TOTAL="$1"
      shift
      ;;
    -h|--help)
      echo "usage: Extract all dcgm metrics from prometheus api
  options:
    -i Time interval within which the metrics will belong, default = 30s
    -s Starting time for the interval, not required
    -e Ending time for the interval, not required
    -o Output name (./plot/figures/<output_name>), required
    -f Name of the pod, not required
    -url URL of prometheus service
    NOTE: if both -s and -e are defined they override -i"
      exit 0
      ;;
    *)
      echo -e `Unexpected argument: $1`
      exit 0
  esac
done

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

cd "$parent_path"

if [ ! -z "$FILTER" ]
then
  FILTER=$(echo $FILTER | tr _ -)
else
  FILTER=".*"
fi

if [ -z "$INTERVAL" ] && [ -z "$START" ] && [ -z "$END" ]
then
  echo "Either (-i|--interval) or (-s|--start and -e|--end) should be provided"
  exit 0
fi

if [ ! -z "$INTERVAL" ] && [ ! -z "$START" ] && [ ! -z "$END" ]
then
  echo "(-i|--interval and -s|--start and -e|--end) can not be provided simultanuousley"
  exit 0
fi

if [ -z "$OUT" ]
then
  echo '(-o | --output) argument can not be empty'
  exit 0
fi

if [ -z "$PROM_URL" ]
then
    PROM_URL="http://localhost:30090/"
fi

if [ ! -z "$INTERVAL" ]
then
  STEP="$(($INTERVAL / 100))"
  if [ "$STEP" = 0 ]
  then
    STEP="1"
  fi
fi

if [ -z "$STEP" ]
then 
  STEP="1"
fi

if [ -z "$TOTAL" ]
then
  python plot/parse_mlperf_metrics.py -o "$OUT" $OUT_DIR
fi

METRICS=(
  'DCGM_FI_DEV_DEC_UTIL'
  'DCGM_FI_DEV_ENC_UTIL' 
  'DCGM_FI_DEV_FB_FREE' 
  'DCGM_FI_DEV_FB_USED' 
  'DCGM_FI_DEV_GPU_TEMP' 
  'DCGM_FI_DEV_MEMORY_TEMP' 
  'DCGM_FI_DEV_MEM_CLOCK' 
  'DCGM_FI_DEV_MEM_COPY_UTIL'
  'DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL'
  'DCGM_FI_DEV_PCIE_REPLAY_COUNTER'
  'DCGM_FI_DEV_POWER_USAGE'
  'DCGM_FI_DEV_SM_CLOCK'
  'DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION'
  'DCGM_FI_DEV_VGPU_LICENSE_STATUS'
  'DCGM_FI_DEV_XID_ERRORS'
  'DCGM_FI_PROF_DRAM_ACTIVE'
  'DCGM_FI_PROF_GR_ENGINE_ACTIVE'
  'DCGM_FI_PROF_PCIE_RX_BYTES'
  'DCGM_FI_PROF_PCIE_TX_BYTES'
  'DCGM_FI_PROF_PIPE_TENSOR_ACTIVE'
)

if [ ! -z "$START" ] && [ ! -z "$END" ]
then
  for METRIC in "${METRICS[@]}"
  do
    ./bin/main -url $PROM_URL -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': '$METRIC'}" 2>&1 | tee -a log.txt >(python plot/plot.py -yf '__name__' -x 'Time(s)' $OUT_DIR -o "$OUT" -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL) >/dev/null
  done

else
  for METRIC in "${METRICS[@]}"
  do
    ./bin/main -url $PROM_URL -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': '$METRIC'}" 2>&1 | tee -a log.txt >(python plot/plot.py -yf '__name__' -x 'Time(s)' $OUT_DIR -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL) >/dev/null
  done
fi
