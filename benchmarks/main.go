package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"

	"github.com/aferikoglou/mlab-k8s-cluster-setup/benchmarks/benchmark"
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
		parsingError()
	}

	tmp := strings.Split(yamlPath, "/")
	filename := strings.Split(tmp[len(tmp)-1], ".")[0]

	start, end, duration, err := benchmark.Benchmark(configPath, yamlPath)
	if err != nil {
		log.Fatalf("Error occured while running benchmarks: %s", err)
	}

	fmt.Printf("Started at: %s\nEnded at: %s\nTime elapsed: %f\n", start, end, duration)

	// Now let's execute the dcgm script to compute the cli metrics

	// Unlike the "system" library call from C and other languages,
	// the os/exec package intentionally does not invoke the system shell
	// and does not expand any glob patterns or handle other expansions, pipelines,
	// or redirections typically done by shells
	// Note: args should be provided in variadic form as a slice of strings
	cmd := exec.Command("../prom_metrics_cli/dcgm_metrics_range_query.sh", []string{"-s", start, "-e", end, "-o", filename}...)

	err = cmd.Run()
	if err != nil {
		log.Fatal(err)
		panic(err)
	}
	log.Println("Figures saved at prom_metrics_cli/plot/figures/" + filename)
}
