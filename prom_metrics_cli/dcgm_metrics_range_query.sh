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
    -f|--filename)
      FILENAME="$2"
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

if [ -z "$FILENAME" ]
then
  FILENAME=$(echo $OUT | tr _ -)
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
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o "$OUT" -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_ENC_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_FB_FREE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_FB_USED'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_GPU_TEMP'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_VGPU_LICENSE_STATUS'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_MEM_CLOCK'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_MEM_COPY_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_PCIE_REPLAY_COUNTER'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_SM_CLOCK'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -params "{'start': '$START', 'end': '$END', 'step': '$STEP', 'query': 'DCGM_FI_DEV_XID_ERRORS'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'
else
  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_DEC_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_ENC_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_FB_FREE'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_FB_USED'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_GPU_TEMP'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_VGPU_LICENSE_STATUS'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_MEM_CLOCK'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_MEM_COPY_UTIL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_PCIE_REPLAY_COUNTER'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_SM_CLOCK'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'

  ./bin/main -p "api/v1/query_range" -i $INTERVAL -params "{'step': '$STEP', 'query': 'DCGM_FI_DEV_XID_ERRORS'}" &>> log.txt
  tail -1 log.txt | python plot/plot.py -yf '__name__' -x 'Time(s)' -o $OUT -filter '{"exported_pod":"'"$FILENAME"'"}'
fi
