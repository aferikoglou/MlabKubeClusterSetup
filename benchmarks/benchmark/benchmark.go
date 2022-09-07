package benchmark

import (
	"fmt"
	"io/ioutil"
	"log"
	"strings"
	"math"
	"strconv"
	"sync"

	pods "github.com/aferikoglou/mlab-k8s-cluster-setup/benchmarks/pods"

	"time"

	"gopkg.in/yaml.v2"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/watch"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
)

type Image struct {
	Name string `yaml:"name"`
}

type Specification struct {
	Metadata struct {
		Namespace string `yaml:"namespace"`
		Name      string `yaml:"name"`
	}
	Spec struct {
		Container []Image `yaml:"containers,flow"`
	}
}

func fixDate(year int, month time.Month, day int) (y, m, d string) {
	if year < 10 {
		y = "0" + strconv.Itoa(year)
	} else {
		y = strconv.Itoa(year)
	}

	if month < 10 {
		m = "0" + strconv.Itoa(int(month))
	} else {
		m = strconv.Itoa(int(month))
	}

	if day < 10 {
		d = "0" + strconv.Itoa(day)
	} else {
		d = strconv.Itoa(day)
	}

	return y, m, d
}

func fixTime(hours, minutes, seconds int) (h, m, s string) {
	// if hours >= 3 && hours < 13 {
	// 	h = "0" + strconv.Itoa(hours-3)
	// } else if hours >= 13 {
	// 	h = strconv.Itoa(hours - 3)
	// } else if hours < 3 {
	// 	h = strconv.Itoa(23 - (3 - (hours + 1)))
	// }

	if hours < 10 {
		h = "0" + strconv.Itoa(hours)
	} else {
		h = strconv.Itoa(hours)
	}

	if minutes < 10 {
		m = "0" + strconv.Itoa(minutes)
	} else {
		m = strconv.Itoa(minutes)
	}

	if seconds < 10 {
		s = "0" + strconv.Itoa(seconds)
	} else {
		s = strconv.Itoa(seconds)
	}

	return h, m, s
}

func Benchmark(timezone string, configPath string, yamlPath string) (begin string, end string, durationSecs float64, logs string, nodeName string, err error) {

	var wg sync.WaitGroup
	var start time.Time
	var pod Specification
	nodeName = ""
	// diff := -time.Hour * time.Duration(timezone)
	loc, _ := time.LoadLocation(timezone)

	yamlFile, err := ioutil.ReadFile(yamlPath)
	if err != nil {
		return "", "", -1, "", nodeName, err
	}

	err = yaml.Unmarshal(yamlFile, &pod)
	if err != nil {
		return "", "", -1, "", nodeName, err
	}

	// If no namespace is provided in the file then the pod will be automatically created in the default namespace
	if pod.Metadata.Namespace == "" {
		pod.Metadata.Namespace = "default"
	}

	// Create the config struct
	config, err := clientcmd.BuildConfigFromFlags("", configPath)
	if err != nil {
		return "", "", -1, "", nodeName, err
	}

	// Create the clientset
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		return "", "", -1, "", nodeName, err
	}

	FieldSelector := "metadata.name=" + pod.Metadata.Name

	// If pod already exists delete it first
	list, err := pods.ListPods(clientset, pod.Metadata.Namespace, FieldSelector)
	if err != nil {
		return "", "", -1, "", nodeName, err
	}

	if len(list.Items) > 0 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			watchDelete, err := pods.WatchPods(clientset, pod.Metadata.Namespace, FieldSelector)
			if err != nil {
				log.Fatal(err)
			}

			// Block untill the pod gets deleted
			for event := range watchDelete.ResultChan() {
				t := event.Type
				if t == watch.Deleted {
					break
				}
			}
		}()

		pods.DeletePod(configPath, pod.Metadata.Namespace, pod.Metadata.Name)
		// Wait for go routine to return meaning that pod has been deleted
		wg.Wait()
	}

	// Apply the pod yaml file
	pods.ApplyPod(configPath, yamlPath)

	// Watch the pod until its status becomes "Succeeded"
	watch, err := pods.WatchPods(clientset, pod.Metadata.Namespace, FieldSelector)
	if err != nil {
		log.Fatal(err)
	}

	tmp := strings.Split(yamlPath, "/")
	filename := strings.Split(tmp[len(tmp)-1], ".")[0]
	failed := false
	wg.Add(1)
	go func(filename string, started bool) {
		defer wg.Done()
		for event := range watch.ResultChan() {
			p, ok := event.Object.(*corev1.Pod)
			if !ok {
				log.Fatal("got unexpected type while running pod")
			}
			if p.Status.Phase == corev1.PodRunning {
				// When pod gets ready start counting
				nodeName = p.Spec.NodeName
				if (!started) {
					started = true
					start = time.Now().In(loc)		
				}
			}
			log.Printf("%s pod's status: %s\n", filename, p.Status.Phase)
			if p.Status.Phase == corev1.PodSucceeded {
				// When pod's state becomes Succeeded delete the pod and break out of the loop
				logs = pods.GetLogs(clientset, *p)
				break
			} else if p.Status.Phase == corev1.PodFailed {
				// If pod's state becomes Failed or Unknown, mark as failed and break
				failed = true
				logs = pods.GetLogs(clientset, *p)
				break
			}
		}
		pods.DeletePod(configPath, pod.Metadata.Namespace, pod.Metadata.Name)
	}(filename, false)

	// Wait for the goroutine to finish
	wg.Wait()

	if failed {
		return "", "", -1, logs, nodeName, fmt.Errorf(fmt.Sprintf("Pod %s failed", pod.Metadata.Name))
	}

	t := time.Now().In(loc)
	duration := t.Sub(start)
	// Converting time.Duration to seconds since t.Sub() return value is in nanoseconds
	durationSecs = float64(duration) / math.Pow(10, 9)

	startYear, startMonth, startDay := fixDate(start.Date())
	startHour, startMinutes, startSeconds := fixTime(start.Clock())
	begin = fmt.Sprintf("%s-%s-%sT%s:%s:%sZ", startYear, startMonth, startDay, startHour, startMinutes, startSeconds)

	endYear, endMonth, endDay := fixDate(start.Add(duration).Date())
	endHour, endMinutes, endSeconds := fixTime(start.Add(duration).Clock())
	end = fmt.Sprintf("%s-%s-%sT%s:%s:%sZ", endYear, endMonth, endDay, endHour, endMinutes, endSeconds)

	return begin, end, durationSecs, logs, nodeName, nil
}
