#!/bin/bash

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--instance)
            PARTITION="$2"
            shift
            shift
            ;;
        -di|--destroy-instance)
            DESTROY="$2"
            shift
            shift
            ;;
        -e|--enable)
            ENABLE="True"
            shift
            ;;
        -d|--disable)
            DISABLE="True"
            shift
            ;;
        -p|--profiles)
            PROFILES="True"
            shift
            ;;
        -h|--help)
      echo "usage: Manage MIG partitions on A30 GPU
  options:
    -i|--instance  Create new MIG partition based on one of the following profiles: [0, 14, 19]
    -di|--destroy-instance  Destroy MIG partiion based on one of the following profiles: [0, 14, 19]
    -e|--enable  Enable MIG mode on the GPU
    -d|--diable  Disable MIG mode on the GPU
    -p|--profiles  List MIG profiles"
      exit 0
      ;;
    esac
done

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

if [[ "$PARTITION" == "14" ]] 
then 
    PARTITION="14,2g.6gb"
elif [[ "$PARTITION" == "19" ]]
then 
    PARTITION="19,1g.3gb"
elif [[ "$PARTITION" == "0" ]]
then
    PARTITION="0,4g.24gb"
elif [[ ! -z "$PARTITION" ]]
then 
    echo -e "partition must be one of the following: {0, 14, 19}"
fi

if [[ "$DESTROY" == "14" ]] 
then 
    DESTROY="14,2g.6gb"
elif [[ "$DESTROY" == "19" ]]
then 
    DESTROY="19,1g.3gb"
elif [[ "$DESTROY" == "0" ]]
then
    DESTROY="0,4g.24gb"
elif [[ ! -z "$DESTROY" ]]
then 
    echo -e "partition must be one of the following: {0, 14, 19}"
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
    sudo nvidia-smi mig -dci -ci 0 -gi $DESTROY
fi

if [[ ! -z $PARTITION ]] 
then
    sudo nvidia-smi mig -cgi $PARTITION -C
fi
