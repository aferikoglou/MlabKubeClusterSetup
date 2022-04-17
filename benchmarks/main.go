package main

import (
	"benchmarks/benchmark"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"strconv"
)

func parsingError() {
	fmt.Println("Usage: main.go")
	flag.PrintDefaults()
	fmt.Println("\nNote: Yaml path cant be empty")
	os.Exit(1)
}

func main() {
	var configPath string
	var yamlPath string

	flag.StringVar(&configPath, "c", "/root/.kube/config", "Kube config path")
	flag.StringVar(&yamlPath, "y", "", "Path to the yaml file to be applied")

	flag.Parse()

	if yamlPath == "" {
		fmt.Println(yamlPath)
		parsingError()
	}

	duration := strconv.FormatFloat(benchmark.Benchmark(configPath, yamlPath), 'E', 3, 64)

	exec.Command("/bin/bash", "../prom_metrics_cli/dcgm_metrics_range_query.sh -i "+duration)
}
