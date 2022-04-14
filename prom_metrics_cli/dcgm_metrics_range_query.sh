#!/bin/bash

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_DEC_UTIL"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"
 
go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_ENC_UTIL"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_FB_FREE"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_FB_USED"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_GPU_TEMP"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_VGPU_LICENSE_STATUS"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_MEM_CLOCK"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_MEM_COPY_UTIL"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_PCIE_REPLAY_COUNTER"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_SM_CLOCK"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"

go run main.go -p 'api/v1/query_range' -i 30 -params '{"step": "1s", "query": "DCGM_FI_DEV_XID_ERRORS"}' &>> log.txt
tail -1 log.txt | python plot/plot.py -f "__name__" -x "Time(s)"
