#!/bin/bash

while [[ $# -gt 0 ]]; do
  case $1 in
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
    NOTE: if bot -s and -e are defined they override -i"
      exit 0
      ;;
    *)
      shift
      shift
      ;;
  esac
done

if [ ! -z "$FILTER" ]
then
  FILTER=$(echo $FILTER | tr _ -)
fi

if [ ! -z "$FILTER" ]
then
  FILTER=".*"
fi

if [ -z "$INTERVAL" ]
then
  INTERVAL='30'
fi

if [ -z "$OUT" ]
then
  echo '(-o | --output) argument can not be empty'
  exit 0
fi

STEP="$(($INTERVAL / 100))"
if [ "$STEP" = 0 ]
then
  STEP="1"
fi

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

cd "$parent_path"

if [ ! -z "$START" ] && [ ! -z "$END" ]
then
  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_DEC_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o "$OUT" -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_ENC_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_FB_FREE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_FB_USED'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_GPU_TEMP'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_MEMORY_TEMP'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_MEM_CLOCK'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_MEM_COPY_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_PCIE_REPLAY_COUNTER'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_POWER_USAGE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_SM_CLOCK'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_VGPU_LICENSE_STATUS'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_XID_ERRORS'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_PROF_DRAM_ACTIVE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_PROF_GR_ENGINE_ACTIVE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_PROF_PCIE_RX_BYTES'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_PROF_PCIE_TX_BYTES'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_PROF_PIPE_TENSOR_ACTIVE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

else
  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_DEC_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_DEC_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o "$OUT" -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_ENC_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_FB_FREE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_FB_USED'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_GPU_TEMP'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_MEMORY_TEMP'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_MEM_CLOCK'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_MEM_COPY_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_PCIE_REPLAY_COUNTER'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_POWER_USAGE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_SM_CLOCK'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_VGPU_LICENSE_STATUS'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params"{'step': '$STEP', 'query': 'DCGM_FI_DEV_XID_ERRORS'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_PROF_DRAM_ACTIVE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_PROF_GR_ENGINE_ACTIVE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_PROF_PCIE_RX_BYTES'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_PROF_PCIE_TX_BYTES'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_PROF_PIPE_TENSOR_ACTIVE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILTER"'"}' -f "exported_pod" $TOTAL
fi
