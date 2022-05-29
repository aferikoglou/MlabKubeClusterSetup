## Install
Get required packages using:
``` bash
$ go mod tidy; go mod vendor
```

## Usage
``` bash
$ go run main.go --help
```

## Example usage
``` bash
$ go run main.go -c "/path/to/config" -yaml "/path/to/yaml"
```

## Build and run binary:
``` bash
$ go build -o bin/main main.go
# or
$ make build

$ ./bin/main -c "/path/to/config" -yaml "/path/to/yaml"
```

## Or install using makefile:
``` bash
make all
```

## Models and data

The folder [mlperf_gpu_pods](https://github.com/aferikoglou/mlab-k8s-cluster-setup/tree/main/benchmarks/mlpref_gpu_pods) contains the yaml files needed to deploy the benchmarks on the gpu nodes of your kubernetes cluster. In order to run those benchmarks you have to add the respective models in the **/mnt/mlperf/models** folder of your host gpu machine and the datasets in the **/mnt/mlperf/data/coco-300**, **/mnt/mlperf/data/coco-1200** and **/mnt/mlperf/data/imagenet2012** folders respectively.
A good way to share the the models and datasets among your gpu nodes, if you'd like to run the experiments in a distributed cluster, is to add them in the **/mnt/mlperf** directory of the master node and then use NFS (network file share) as described [here](https://www.tecmint.com/install-nfs-server-on-ubuntu/).

You can learn how to resize the datasets [here](https://github.com/mlcommons/inference/tree/master/vision/classification_and_detection#prepare-the-coco-dataset).

The models and datasets needed for each benchmark are illustrated in the following table: https://github.com/mlcommons/inference/tree/master/vision/classification_and_detection

---
Finally, you can run all the benchmarks from the top-level directory with:
``` bash
    # -n option means if a benchmark is already ran skip it, -s defines the number of seconds to sleep between 2
    # consecutive batch executions and -b defines the batch size i.e the number of pods to deploy and benchmark
    # in one go.
    ./benchmarks/benchmark_gpu_pods.sh -c /home/dimitris/.kube/config -n -s 3 -b 2
```
or just
``` bash
./benchmark_gpu_pods.sh -n
```
if you are using the /root/.kube/config.

> **Note1:** In order for the above to run you have to have installed the [Metrics cli](https://github.com/aferikoglou/mlab-k8s-cluster-setup/tree/main/prom_metrics_cli) first.

> **Note2:** In order to run benchmark_gpu_pods.sh you have to have built ($ make) main.go first.
