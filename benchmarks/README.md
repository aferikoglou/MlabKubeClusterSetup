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
$ go run main.go -c "/path/to/config" -y "/path/to/yaml"
```

## Build and run binary:
``` bash
$ go build -o bin/main main.go
# or
$ make build

$ ./bin/main -c "/path/to/config" -y "/path/to/yaml"
```

## Or install using makefile:
``` bash
make all
```

## Models and data

The folder [mlperf_gpu_pods](https://github.com/aferikoglou/mlab-k8s-cluster-setup/tree/main/benchmarks/mlpref_gpu_pods) contains the yaml files needed to deploy the benchmarks on the gpu nodes of your kubernetes cluster. In order to run those benchmarks you have to add the respective models in the **/mnt/mlperf/models** folder of your host gpu machine and the datasets in the **/mnt/mlperf/data/coco-300**, **/mnt/mlperf/data/coco-1200** and **/mnt/mlperf/data/imagenet2012** folder. The  datasets must be in the folders

You can learn how to resize the datasets [here](https://github.com/mlcommons/inference/tree/master/vision/classification_and_detection#prepare-the-coco-dataset).

The models and datasets needed for each benchmark are illustrated in the following table: https://github.com/mlcommons/inference/tree/master/vision/classification_and_detection

---
Finally, you can run all the benchmarks with:
``` bash
./benchmark_gpu_pods.sh -c ~/.kube/config
```
or just
``` bash
./benchmark_gpu_pods.sh
```
if you are using the /root/.kube/config.

> **Note1:** In order for the above to run you have to have installed the [Metrics cli](https://github.com/aferikoglou/mlab-k8s-cluster-setup/tree/main/prom_metrics_cli) first.

> **Note2:** In order to run benchmark_gpu_pods.sh, you have to have built (make all) main.go first.
