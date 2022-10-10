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
	"sync"
	"time"

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
	// Check if dir exists
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return false, nil
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
	for _, f := range files {
		tmp = strings.Split(f.Name(), "_")
		tmp := strings.Join(tmp[:len(tmp)-1], "_")
		if tmp == filenamePrefix {
			return true, nil
		}
	}

	// Check for logs.txt
	for _, f := range files {
		if f.Name() == logFilename {
			return true, nil
		}
	}

	return false, nil
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

	for _, f := range files {
		tmp = strings.Split(f.Name(), "_")
		tmp := strings.Join(tmp[:len(tmp)-1], "_")
		if tmp == filenamePrefix {
			os.Remove(fmt.Sprintf("%s/%s", path, f.Name()))
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

func inArray(val int, arr []int) bool {
	for _, x := range arr {
		if x == val {
			return true
		}
	}
	return false
}

func findMax(arr []int) int {
	if len(arr) == 0 {
		return -1
	}

	max := 0
	for i, x := range arr {
		if x > arr[max] {
			max = i
		}
	}
	return max
}

func findMin(arr []int) int {
	if len(arr) == 0 {
		return -1
	}

	min := 0
	for i, x := range arr {
		if x < 0 {
			continue
		}

		if x < arr[min] || arr[min] < 0 {
			min = i
		}
	}
	return min
}

func convertDateStringToInt(date string) int {
	if date == "" {
		return -1
	}

	timestamp, _ := time.Parse("2006-01-02T15:04:05Z", date)

	hr, min, sec := timestamp.Clock()

	return hr*10000 + min*100 + sec
}

func parsingError() {
	fmt.Println("Usage: main.go")
	flag.PrintDefaults()
	os.Exit(1)
}

func main() {
	var configPath, promURL, yamlPath, logsFile, totalFiles, timezone, outDir string
	var autoskip, autodelete, appendTime bool
	var batch, sleep int
	var wg sync.WaitGroup
	var mu sync.Mutex

	flag.StringVar(&configPath, "c", "/root/.kube/config", "Kube config path")
	flag.StringVar(&outDir, "o", "", "Output directory")
	flag.StringVar(&yamlPath, "yaml", "", "Path to the yaml file or to a directory containing the yaml file(s) to be applied.")
	flag.StringVar(&logsFile, "l", "logs.txt", "Filename to save output logs")
	flag.StringVar(&totalFiles, "t", "total", "Name for the figures for the total duration")
	flag.StringVar(&promURL, "url", "http://localhost:30090/", "URL of prometheus service")
	flag.StringVar(&timezone, "tz", "UTC", "Location related to the timezone")
	flag.BoolVar(&autoskip, "n", false, "If this flag is set then if files exist the program will exit")
	flag.BoolVar(&autodelete, "y", false, "If this flag is set then all existing files will be automatically deleted")
	flag.BoolVar(&appendTime, "a", false, "If this flag is set then starting time of the benchmarks will be appended on the folders' names")
	flag.IntVar(&batch, "b", 1, "Number of pods to be ran concurrently")
	flag.IntVar(&sleep, "s", 60, "Number of seconds to sleep between consecutive batch executions")

	flag.Parse()

	layout := "2006-01-02T15:04:05Z"

	if yamlPath == "" {
		fmt.Println("Note: -yaml cant be empty")
		parsingError()
	}

	if autoskip == true && autodelete == true {
		fmt.Println("Note: -n and -y can't be set simultaneously")
		parsingError()
	}

	if batch < 1 {
		fmt.Println("Note: -b can't be less than one")
		parsingError()
	}

	if sleep < 0 {
		fmt.Println("Note: -s can't be less than zero")
		parsingError()
	}

	// If yamlPath ends with '/' remove it for consistency
	if yamlPath[len(yamlPath)-1:] == "/" {
		yamlPath = yamlPath[:len(yamlPath)-1]
	}

	var files []string
	tmp := strings.Split(yamlPath, ".")
	// If yamlPath is path to a file then add this file to the files to be ran
	if tmp[len(tmp)-1] == "yaml" || tmp[len(tmp)-1] == "yml" {
		files = append(files, yamlPath)
	} else {
		// Else add all the yaml files from this directory
		yamlFiles, err := ioutil.ReadDir(yamlPath)
		if err != nil {
			log.Fatal(fmt.Sprintf("Unable to open directory %s", yamlPath))
		}
		for _, file := range yamlFiles {
			tmp = strings.Split(file.Name(), ".")
			if tmp[len(tmp)-1] == "yaml" {
				files = append(files, fmt.Sprintf("%s/%s", yamlPath, file.Name()))
			}
		}
	}

	if len(files) == 0 {
		log.Fatalf("Directory %s is empty", yamlPath)
	}

	var skip []int
	var appendInd []int
	for i, file := range files {
		tmp = strings.Split(file, "/")
		filename := strings.Split(tmp[len(tmp)-1], ".")[0]
		path := fmt.Sprintf("%s/%s", outDir, filename)

		if appendTime {
			// Append starting times on folders' names
			log.Printf("Time will be appended to folder's name for pod [%s]\n", filename)
			appendInd = append(appendInd, i)
			continue
		}

		exist, err := filesExist(path, logsFile)
		if err != nil {
			log.Fatalf("Error occured in filesExist(): %+v", err)
		}
		if exist {
			log.Printf("Files for pod [%s] already exist", filename)
			if autoskip {
				log.Printf("Skipping file %s", file)
				skip = append(skip, i)
			} else if autodelete {
				// Delete files
				log.Println("Deleting")
				err := deleteFiles(path, logsFile)
				if err != nil {
					log.Fatalf("Could not delete files")
				}
			} else if appendTime {
				log.Printf("Time will be appended to folder's name for pod [%s]\n", filename)
				appendInd = append(appendInd, i)
			} else {
				fmt.Printf("Would you like to append starting datetime in the name of the output folder?[Y/N]\n>>")
				var ans string
				fmt.Scanln(&ans)
				if ans == string('Y') || ans == string('y') {
					log.Printf("Time will be appended to folder's name for pod [%s]\n", filename)
					appendInd = append(appendInd, i)
				} else {
					fmt.Printf("Would you like to delete existing files?[Y/N]\n>>")
					fmt.Scanln(&ans)
					if ans == string('Y') || ans == string('y') {
						err := deleteFiles(path, logsFile)
						if err != nil {
							log.Fatalf("Could not delete files")
						}
					} else {
						log.Printf("Skipping file %s", file)
						skip = append(skip, i)
					}
				}
			}
		}
	}

	var start []string = make([]string, len(files))
	var end []string = make([]string, len(files))
	var logs []string = make([]string, len(files))
	var nodeNames []string = make([]string, len(files))
	var duration []float64 = make([]float64, len(files))
	var totalDuration float64
	totalDuration = 0
	count := 0
	finishedCounter := 0
	for i, file := range files {
		if inArray(i, skip) {
			continue
		}

		if count == batch {
			log.Println("Waiting for the previous batch to finish")
			wg.Wait()
			log.Printf("Sleeping for %d seconds before starting next batch", sleep)
			time.Sleep(time.Duration(sleep) * time.Second)
		}
		count++

		wg.Add(1)
		go func(ind int, filePath string) {
			defer wg.Done()

			var newErr error
			var outfile string
			tmp := strings.Split(filePath, "/")
			filename := strings.Split(tmp[len(tmp)-1], ".")[0]

			start[ind], end[ind], duration[ind], logs[ind], nodeNames[ind], newErr = benchmark.Benchmark(timezone, configPath, filePath)
			mu.Lock()
			count--
			if count == 0 {
				totalDuration += duration[ind]
			}
			mu.Unlock()
			if finishedCounter == 0 {
				if outDir == "" {
					outDir = fmt.Sprintf("%s/../../prom_metrics_cli/plot/figures/%s", getDirname(), strings.ReplaceAll(start[ind], "-", "_"))
				}
				finishedCounter += 1
			}
			if inArray(ind, appendInd) {
				outfile = fmt.Sprintf(
					"%s_%s_%s",
					filename,
					strings.ReplaceAll(nodeNames[ind], "-", "_"),
					strings.ReplaceAll(start[ind], "-", "_"),
				)
			} else {
				outfile = filename
			}

			outPath := fmt.Sprintf("%s/%s", outDir, outfile)
			if _, err := os.Stat(outPath); os.IsNotExist(err) {
				err = os.MkdirAll(outPath, os.ModePerm)
				if err != nil {
					log.Println(err)
				}
			}

			if newErr != nil {
				if logs[ind] != "" {
					_, writeErr := writeFile(outPath, logsFile, logs[ind])
					if writeErr != nil {
						log.Printf("%+v", writeErr)
					}
				}
				log.Printf("Error occured while running benchmarks for file %s: %+v", filename, newErr)
				return
			}

			_, newErr = writeFile(outPath, logsFile, logs[ind])
			if newErr != nil {
				log.Printf("%+v, exiting", newErr)
				return
			}
			log.Printf("Started at: %s\nEnded at: %s\nTime elapsed: %f\n", start[ind], end[ind], duration[ind])

			log.Printf("Output filename: [%s]", outfile)

			// Now let's execute the dcgm script to compute the cli metrics
			// Unlike the "system" library call from C and other languages,
			// the os/exec package intentionally does not invoke the system shell
			// and does not expand any glob patterns or handle other expansions, pipelines,
			// or redirections typically done by shells
			// Note: args should be provided in variadic form as a slice of strings
			step := strconv.Itoa(int(duration[ind] / 100))
			if step == "0" {
				step = "1"
			}
			s := fmt.Sprintf("%f", duration[ind])
			cmd := exec.Command(
				"../prom_metrics_cli/dcgm_metrics_range_query.sh",
				[]string{
					"-s", start[ind],
					"-e", end[ind],
					"-f", filename,
					"-o", outfile,
					"--out-dir", outDir,
					"-url", promURL,
					"-step", step,
					"--duration", s,
				}...,
			)

			out, newErr := cmd.CombinedOutput()
			if newErr != nil {
				output := string(out[:])
				if output != "" {
					log.Printf("Output: %s\n", output)
				}
				log.Print(newErr)
				return
			}
			log.Printf("Figures saved at %s\n", outDir)
		}(i, file)
	}

	wg.Wait()

	// Find the min and max indices for start and end arrays respectively
	// and then run the metrics' queries again for the total duration
	var tmpStart []int
	var tmpEnd []int
	for i := 0; i < len(start); i++ {
		if start[i] == "" || end[i] == "" {
			continue
		}
		tmpStart = append(tmpStart, convertDateStringToInt(start[i]))
		tmpEnd = append(tmpEnd, convertDateStringToInt(end[i]))
	}

	minInd := findMin(tmpStart)
	maxInd := findMax(tmpEnd)
	if minInd == -1 || maxInd == -1 || tmpStart[minInd] == -1 || tmpEnd[maxInd] == -1 {
		log.Fatal("Couldn't save total benchmarks")
	}

	totalEndTime, err := time.Parse(layout, end[maxInd])
	if err != nil {
		log.Fatal("Unable to convert total ending time")
	}
	totalStartTime, err := time.Parse(layout, start[minInd])
	if err != nil {
		log.Fatal("Unable to convert total starting time")
	}
	expadedDuration := totalEndTime.Sub(totalStartTime).Seconds()
	step := strconv.Itoa(int(expadedDuration / 100))
	if step == "0" {
		step = "1"
	}
	totalOut := fmt.Sprintf("%s_%s", totalFiles, start[minInd])
	outPath := fmt.Sprintf("%s/%s", outDir, totalOut)
	if _, err := os.Stat(outPath); os.IsNotExist(err) {
		err = os.MkdirAll(outPath, os.ModePerm)
		if err != nil {
			log.Println(err)
		}
	}

	s := fmt.Sprintf("%f", totalDuration)
	log.Println(fmt.Sprintf("Total starting time: %s\nTotal ending time: %s\nTotal duration: %s", start[minInd], end[maxInd], s))
	cmd := exec.Command(
		"../prom_metrics_cli/dcgm_metrics_range_query.sh",
		[]string{
			"-s", start[minInd],
			"-e", end[maxInd],
			"-o", totalOut,
			"--out-dir", outDir,
			"--total",
			"-url", promURL,
			"-step", step,
			"--duration", s,
		}...,
	)

	cmdOut, newErr := cmd.CombinedOutput()
	if newErr != nil {
		output := string(cmdOut[:])
		if output != "" {
			log.Printf("Output: %s\n", output)
		}
		log.Fatal(newErr)
	}
	log.Printf("Total figures saved at %s\n", outDir)
}
