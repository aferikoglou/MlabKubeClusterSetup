#!/bin/bash

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--instance)
            CREATE="TRUE"
            PARTITION="$2"
            shift
            shift
            ;;
        --di|--destroy-instance)
            DESTROY="TRUE"
            shift
            ;;
        -gi|--gpu-instance)
            GI="$2"
            shift
            shift
            ;;
        -ci|--compute-instance)
            CI="$2"
            shift
            shift
            ;;
        --e|--enable)
            ENABLE="True"
            shift
            ;;
        --d|--disable)
            DISABLE="True"
            shift
            ;;
        --p|--profiles)
            PROFILES="True"
            shift
            ;;
        -h|--help)
            echo "usage: Manage MIG partitions on A30 GPU
        options:
            -i|--instance  Create new MIG partition based on one of the following profiles: [0, 14, 19]
            --di|--destroy-instance  Flag used to destroy MIG compute and gpu instances according to -ci and -gi arguments respectively
            --e|--enable  Flag used to enable MIG mode on the GPU
            --d|--diable  Flag used to disable MIG mode on the GPU
            --p|--profiles  Flag used to list MIG profiles"
            exit 0
            ;;
        *)
            echo -e "Unexpected argument: "$1
            exit 0
    esac
done

if ([ ! -z "$DESTROY" ] || [ ! -z "$CI" ] || [ ! -z "$GI" ]) && (! ([ ! -z "$DESTROY" ] && [ ! -z "$CI" ] && [ ! -z "$GI" ]))
then
    echo -e "--di , -ci and -gi must be provided simultanuously"
    exit 0
fi

if [ -z "$ENABLE" ] 
then
    ENABLE="False"
fi

if [ -z "$DISABLE" ] 
then
    DISABLE="False"
fi

if [ -z "$PROFILES" ] 
then
    PROFILES="False"
fi

if [[ "$PARTITION" == "21" ]] 
then 
    PARTITION="21,1g.6gb+me"
elif [[ "$PARTITION" == "5" ]]
then 
    PARTITION="5,2g.12gb"
elif [[ "$PARTITION" == "0" ]]
then
    PARTITION="0,4g.24gb"
elif [[ "$PARTITION" == "14" ]]
then
    PARTITION="14,1g.6gb"
elif [[ ! -z "$PARTITION" ]]
then 
    echo -e `partition must be one of the following: {0, 5, 14, 21} run "mig -p for more"`
    exit 0
fi

if [[ $ENABLE == "True" ]] 
then
    sudo nvidia-smi -i 0 -mig 1
fi

if [[ $DISABLE == "True" ]] 
then
    sudo nvidia-smi -i 0 -mig 0
fi

if [[ $PROFILES == "True" ]] 
then
    sudo nvidia-smi mig -lgip
    sudo nvidia-smi mig -lgipp
fi

if [[ ! -z $DESTROY ]] 
then
    sudo nvidia-smi mig -dci -ci $CI -gi $GI
fi

if [[ ! -z $CREATE ]] 
then
    sudo nvidia-smi mig -cgi $PARTITION -C
fi
