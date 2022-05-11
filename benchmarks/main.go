package main

import (
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/aferikoglou/mlab-k8s-cluster-setup/benchmarks/benchmark"
)

func getDirname() string {
	ex, err := os.Executable()
	if err != nil {
		panic(err)
	}
	dirname := filepath.Dir(ex)
	return dirname
}

func filesExist(path string, logFilename string) (bool, error) {
	// Make directory if not exists
	if _, err := os.Stat(path); os.IsNotExist(err) {
		err = os.Mkdir(path, 002)
		if err != nil {
			log.Println(err)
			return false, err
		}
	}

	// List files in path
	files, err := ioutil.ReadDir(path)
	if err != nil {
		log.Println(err)
		return false, err
	}

	// Parse filename's prefix from path
	tmp := strings.Split(path, "/")
	filenamePrefix := tmp[len(tmp)-1]

	// Check for figures
	found := false
	for i := 0; i < 12; i++ {
		found = false
		for _, f := range files {
			if f.Name() == fmt.Sprintf("%s_%s", filenamePrefix, strconv.Itoa(i+1)) {
				found = true
				break
			}
		}
		if !found {
			return false, nil
		}
	}

	// Check for logs.txt
	found = false
	for _, f := range files {
		if f.Name() == logFilename {
			found = true
			break
		}
	}
	if !found {
		return false, nil
	}
	return true, nil
}

func writeFile(path string, filename string, s string) (string, error) {
	fullPath := fmt.Sprintf("%s/%s", path, filename)

	if _, err := os.Stat(fullPath); !os.IsNotExist(err) {
		log.Printf("File with name: %s, already exists", fullPath)
		return "", errors.New("file already exists")
	}

	f, err := os.Create(fullPath)
	if err != nil {
		log.Println(err)
		return "", err
	}
	bytesCount, err := f.WriteString(s)
	if err != nil {
		log.Println(err)
		f.Close()
		return "", err
	}
	err = f.Close()
	if err != nil {
		log.Println("Error occured in writeFile() while closing file:", err)
		return "", err
	}
	return fmt.Sprintf("%s %s %s", strconv.Itoa(bytesCount), "bytes written successfully to:", fullPath), nil
}

func parsingError() {
	fmt.Println("Usage: main.go")
	flag.PrintDefaults()
	fmt.Println("\nNote: Yaml path cant be empty")
	os.Exit(1)
}

func main() {
	var configPath string
	var yamlPath string
	var logsFile string

	flag.StringVar(&configPath, "c", "/root/.kube/config", "Kube config path")
	flag.StringVar(&yamlPath, "y", "", "Path to the yaml file to be applied")
	flag.StringVar(&logsFile, "l", "logs.txt", "Filename to save output logs")

	flag.Parse()

	if yamlPath == "" {
		parsingError()
	}

	tmp := strings.Split(yamlPath, "/")
	filename := strings.Split(tmp[len(tmp)-1], ".")[0]
	path := fmt.Sprintf("%s/../../prom_metrics_cli/plot/figures/%s", getDirname(), filename)

	exist, err := filesExist(path, logsFile)
	if err != nil {
		log.Fatalf("Error occured in filesExist(): %s", err)
	}
	if exist {
		log.Fatalf("Figures for pod [%s] already exist, exitting", filename)
	}

	start, end, duration, logs, err := benchmark.Benchmark(configPath, yamlPath)
	if err != nil {
		_, err = writeFile(path, logsFile, logs)
		if err != nil {
			log.Printf("%s, exiting", err)
		}
		log.Fatalf("Error occured while running benchmarks: %s", err)
	}

	_, err = writeFile(path, logsFile, logs)
	if err != nil {
		log.Fatalf("%s, exiting", err)
	}
	log.Printf("Started at: %s\nEnded at: %s\nTime elapsed: %f\n", start, end, duration)

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
