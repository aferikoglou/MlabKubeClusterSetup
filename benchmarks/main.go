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
		err = os.MkdirAll(path, os.ModePerm)
		if err != nil {
			log.Println(err)
			return false, fmt.Errorf("error in os.MkdirAll(): %s", err)
		}
	}

	// List files in path
	files, err := ioutil.ReadDir(path)
	if err != nil {
		log.Println(err)
		return false, fmt.Errorf("error in ioutil.ReadDir(): %s", err)
	}

	// Parse filename's prefix from path
	tmp := strings.Split(path, "/")
	filenamePrefix := tmp[len(tmp)-1]

	// Check for figures
	var found bool
	for i := 0; i < 12; i++ {
		found = false
		for _, f := range files {
			if f.Name() == fmt.Sprintf("%s_%s", filenamePrefix, strconv.Itoa(i+1)) {
				found = true
				break
			}
		}
		if found {
			return true, nil
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

	return found, nil
}

func deleteFiles(path string, logFilename string) error {
	// Parse filename's prefix from path
	tmp := strings.Split(path, "/")
	filenamePrefix := tmp[len(tmp)-1]

	// List files in path
	files, err := ioutil.ReadDir(path)
	if err != nil {
		log.Println(err)
		return fmt.Errorf("error in ioutil.ReadDir(): %s", err)
	}

	for i := 0; i < 12; i++ {
		for _, f := range files {
			if f.Name() == fmt.Sprintf("%s_%s", filenamePrefix, strconv.Itoa(i+1)) {
				os.Remove(fmt.Sprintf("%s/%s", path, f.Name()))
			}
		}
	}

	// Check for logs.txt
	for _, f := range files {
		if f.Name() == logFilename {
			os.Remove(fmt.Sprintf("%s/%s", path, f.Name()))
		}
	}

	return nil
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
	os.Exit(1)
}

func main() {
	var configPath string
	var yamlPath string
	var logsFile string
	var autoskip bool
	var autodelete bool

	flag.StringVar(&configPath, "c", "/root/.kube/config", "Kube config path")
	flag.StringVar(&yamlPath, "yaml", "", "Path to the yaml file to be applied")
	flag.StringVar(&logsFile, "l", "logs.txt", "Filename to save output logs")
	flag.BoolVar(&autoskip, "n", false, "If this flag is set then if files exist the program will exit")
	flag.BoolVar(&autodelete, "y", false, "If this flag is set then all existing files will be automatically deleted")

	flag.Parse()

	if yamlPath == "" {
		fmt.Println("Note: Yaml path cant be empty")
		parsingError()
	}

	if autoskip == true && autodelete == true {
		fmt.Println("Note: -n and -y can't be se simultaneously")
		parsingError()
	}

	tmp := strings.Split(yamlPath, "/")
	filename := strings.Split(tmp[len(tmp)-1], ".")[0]
	path := fmt.Sprintf("%s/../../prom_metrics_cli/plot/figures/%s", getDirname(), filename)

	exist, err := filesExist(path, logsFile)
	if err != nil {
		log.Fatalf("Error occured in filesExist(): %+v", err)
	}
	if exist {
		log.Printf("Files for pod [%s] already exist", filename)
		if autoskip {
			log.Fatalf("Exiting")
		} else if autodelete {
			// Delete files
			log.Println("Deleting it")
			err := deleteFiles(path, logsFile)
			if err != nil {
				log.Fatalf("Could not delete files")		
			}
		} else {
			fmt.Printf("Would you like to delete them?[Y/N]\n>>")
			var ans string
			fmt.Scanln(&ans)
			if ans == string('Y') || ans == string('y') {
				// Delete files
				err := deleteFiles(path, logsFile)
				if err != nil {
					log.Fatalf("Could not delete files")		
				}
			} else {
				log.Fatalf("Exiting")
			}
		}
	}
	
	

	start, end, duration, logs, err := benchmark.Benchmark(configPath, yamlPath)
	if err != nil {
		_, writeErr := writeFile(path, logsFile, logs)
		if writeErr != nil {
			log.Printf("%+v, exiting", writeErr)
		}
		log.Fatalf("Error occured while running benchmarks: %+v", err)
	}

	_, err = writeFile(path, logsFile, logs)
	if err != nil {
		log.Fatalf("%+v, exiting", err)
	}
	log.Printf("Started at: %s\nEnded at: %s\nTime elapsed: %f\n", start, end, duration)

	// Now let's execute the dcgm script to compute the cli metrics
	// Unlike the "system" library call from C and other languages,
	// the os/exec package intentionally does not invoke the system shell
	// and does not expand any glob patterns or handle other expansions, pipelines,
	// or redirections typically done by shells
	// Note: args should be provided in variadic form as a slice of strings
	cmd := exec.Command("../prom_metrics_cli/dcgm_metrics_range_query.sh", []string{"-s", start, "-e", end, "-o", filename}...)

	out, err := cmd.Output()
	if err != nil {
		output := string(out[:])
		if output != "" {
			log.Printf("Output: %s\n", output)
		}
    	log.Fatal(err)
	}
	log.Printf("Figures saved at prom_metrics_cli/plot/figures/%s\n", filename)
}
