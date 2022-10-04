## NVIDIA Multi-Instance GPU Guide

Having installed the NVIDIA drivers and CUDA libraries, you should now be able to partition the MIG GPU into multiple GPU instances in order to isolate the execution of CUDA applications. 

In order for this to be achieved you have to first **enable MIG mode**. 

By default, MIG mode is not enabled on the NVIDIA A30 and A30. For example, running nvidia-smi shows that MIG mode is disabled: 

```
nvidia-smi -i 0
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 460.73.01    Driver Version: 460.73.01    CUDA Version: 11.2     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  A30                 Off  | 00000000:00:07.0 Off |                    0 |
| N/A   43C    P0    32W / 165W |      0MiB / 24258MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+

```

MIG mode can be enabled on a per-GPU basis with the following command: nvidia-smi -i <GPU_IDs> -mig 1 (and disabled with -mig 0). The GPUs can be selected using comma separated GPU indexes, PCI Bus Ids or UUIDs. If no GPU ID is specified, then MIG mode is applied to all the GPUs on the system. Note that **MIG mode (Disabled or Enabled states) is persistent across system reboots**. 

```
$ sudo nvidia-smi -i 0 -mig 1
Enabled MIG Mode for GPU 00000000:00:07.0
All done.


$ nvidia-smi -i 0 --query-gpu=pci.bus_id,mig.mode.current --format=csv
pci.bus_id, mig.mode.current
00000000:00:07.0, Enabled
```

## List GPU Instance Profiles

The NVIDIA driver provides a number of profiles that users can opt-in for when configuring the MIG feature in A100. The profiles are the sizes and capabilities of the GPU instances that can be created by the user. The driver also provides information about the placements, which indicate the type and number of instances that can be created. 

```
$ sudo nvidia-smi mig -lgip
+--------------------------------------------------------------------------+
| GPU instance profiles:                                                   |
| GPU   Name          ID    Instances   Memory     P2P    SM    DEC   ENC  |
|                           Free/Total   GiB              CE    JPEG  OFA  |
|==========================================================================|
|   0  MIG 1g.3gb     19     4/4        2.88       No     14     0     0   |
|                                                          1     0     0   |
+--------------------------------------------------------------------------+
|   0  MIG 2g.6gb     14     2/2        5.88       No     28     1     0   |
|                                                          2     0     0   |
+--------------------------------------------------------------------------+
|   0  MIG 4g.24gb     0     1/1        23.69      No     56     4     0   |
|                                                          4     1     1   |
+--------------------------------------------------------------------------+
```

List the possible placements available using the following command. The syntax of the placement is {<_Index>}:<GPU_Slice_Count> and shows the placement of the instances on the GPU. The placement index shown indicates how the profiles are mapped on the GPU as shown in the supported profiles tables.

        
```
$ sudo nvidia-smi mig -lgipp
GPU  0 Profile ID 19 Placements: {0,1,4,5}:1
GPU  0 Profile ID 14 Placements: {0,4}:2
GPU  0 Profile ID  0 Placement : {0}:8
```     

## Creating GPU Instances
Before starting to use MIG, the user needs to create GPU instances using the -cgi option. One of three options can be used to specify the instance profiles to be created:

* Profile ID (e.g. 9, 14, 5)
* Short name of the profile (e.g. 3g.20gb)
* Full profile name of the instance (e.g. MIG 3g.20gb)

Once the GPU instances are created, one needs to create the corresponding Compute Instances (CI). By using the -C option, nvidia-smi creates these instances.

>Note:
Without creating GPU instances (and corresponding compute instances), CUDA workloads cannot be run on the GPU. In other words, simply enabling MIG mode on the GPU is not sufficient. Also **note that, the created MIG devices are not persistent across system reboots**. Thus, the user or system administrator needs to recreate the desired MIG configurations if the GPU or system is reset. For automated tooling support for this purpose, refer to the NVIDIA MIG Partition Editor (or mig-parted) [tool](https://github.com/nvidia/mig-parted).

The following example shows how the user can create GPU instances (and corresponding compute instances). In this example, the user can create two GPU instances (of type 2g.6gb), with each GPU instance having half of the available compute and memory capacity. In this example, we purposefully use profile ID and short profile name to showcase how either option can be used:

```    
$ sudo nvidia-smi mig -cgi 14,2g.6gb -C
Successfully created GPU instance ID  3 on GPU  0 using profile MIG 2g.6gb (ID 14)
Successfully created compute instance ID  0 on GPU  0 GPU instance ID  3 using profile MIG 2g.6gb (ID  1)
Successfully created GPU instance ID  5 on GPU  0 using profile MIG 2g.6gb (ID 14)
Successfully created compute instance ID  0 on GPU  0 GPU instance ID  5 using profile MIG 2g.6gb (ID  1)
```     

For more information on this topic click [here](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/).