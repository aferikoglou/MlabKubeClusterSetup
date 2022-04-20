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
  esac
done

if [ -z "$INTERVAL" ]
then
  INTERVAL="30"
fi

if [ -z "$OUT" ]
then
  echo "(-o | --output) argument can not be empty"
  exit 0
fi

STEP="$(($INTERVAL / 100))"
if [ "$STEP" = 0 ]
then
  STEP="1"
fi

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

cd "$parent_path"

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params `{"step": "1s", "query": "DCGM_FI_DEV_DEC_UTIL"}` &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_ENC_UTIL"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_FB_FREE"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_FB_USED"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_GPU_TEMP"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_VGPU_LICENSE_STATUS"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_MEM_CLOCK"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_MEM_COPY_UTIL"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_PCIE_REPLAY_COUNTER"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_SM_CLOCK"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT

go run main.go -p 'api/v1/query_range' -i $INTERVAL -params '{"step": "1s", "query": "DCGM_FI_DEV_XID_ERRORS"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)" -o $OUT
