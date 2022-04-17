package benchmark

import (
	apply "benchmarks/applyyaml"
	"context"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"sync"

	"time"

	"gopkg.in/yaml.v2"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
)

type Pod struct {
	Namespace string `yaml:"metadata.namespace"`
	PodName   string `yaml:"spec.containers.name"`
}

func Benchmark(configPath string, yamlPath string) (duration float64) {

	var wg sync.WaitGroup
	var start time.Time
	var pod Pod

	yamlFile, err := ioutil.ReadFile(yamlPath)
	if err != nil {
		panic(err)
	}

	err = yaml.Unmarshal(yamlFile, &pod)
	if err != nil {
		panic(err)
	}

	fmt.Println(pod)

	// Create the config struct
	config, err := clientcmd.BuildConfigFromFlags("", "/home/dimitris/.kube/config")
	if err != nil {
		panic(err)
	}

	// create the clientset
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err)
	}

	// Apply the pod yaml file
	apply.Apply(configPath, yamlPath)

	// Watch the pod until its status becomes "Completed"
	watch, err := clientset.CoreV1().Pods(pod.Namespace).Watch(
		context.TODO(),
		metav1.ListOptions{
			FieldSelector: "metadata.name=" + pod.PodName,
		})
	if err != nil {
		log.Fatal(err.Error())
	}

	wg.Add(1)
	go func() {
		defer wg.Done()
		for event := range watch.ResultChan() {
			p, ok := event.Object.(*corev1.Pod)
			if !ok {
				log.Fatal("unexpected type")
			}
			if p.Status.Phase == corev1.PodRunning {
				start = time.Now()
			}
			if p.Status.Phase == corev1.PodSucceeded {
				break
			}
		}

	}()

	wg.Wait()

	t := time.Now()
	// Converting time.Duration to seconds since t.Sub() return value is in nanoseconds
	elapsed := float64(t.Sub(start)) / math.Pow(10, 9)
	fmt.Printf("Time elapsed: %f", elapsed)
	return elapsed
}
