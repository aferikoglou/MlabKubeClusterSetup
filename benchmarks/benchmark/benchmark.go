package benchmark

import (
	"context"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"sync"

	pods "github.com/aferikoglou/mlab-k8s-cluster-setup/benchmarks/pods"

	"time"

	"gopkg.in/yaml.v2"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
)

type Image struct {
	Name string `yaml:"name"`
}

type Specification struct {
	Metadata struct {
		Namespace string `yaml:"namespace"`
	}
	Spec struct {
		Container []Image `yaml:"containers,flow"`
	}
}

func Benchmark(configPath string, yamlPath string) (duration float64) {

	var wg sync.WaitGroup
	var start time.Time
	var pod Specification

	yamlFile, err := ioutil.ReadFile(yamlPath)
	if err != nil {
		panic(err)
	}

	err = yaml.Unmarshal(yamlFile, &pod)
	if err != nil {
		panic(err)
	}

	// Create the config struct
	config, err := clientcmd.BuildConfigFromFlags("", configPath)
	if err != nil {
		panic(err)
	}

	// create the clientset
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err)
	}

	// Apply the pod yaml file
	pods.ApplyPod(configPath, yamlPath)

	// Watch the pod until its status becomes "Succeeded"
	watch, err := clientset.CoreV1().Pods(pod.Metadata.Namespace).Watch(
		context.TODO(),
		metav1.ListOptions{
			FieldSelector: "metadata.name=" + pod.Spec.Container[0].Name,
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
				// When pod gets ready start counting
				start = time.Now()
			}
			fmt.Println(p.Status.Phase)
			if p.Status.Phase == corev1.PodSucceeded {
				// When pod's state becomes Succeeded delete the pod and break out of the loop
				pods.DeletePod(configPath, pod.Metadata.Namespace, pod.Spec.Container[0].Name)
				break
			}
		}

	}()

	// Wait for the goroutine to finish
	wg.Wait()

	t := time.Now()
	// Converting time.Duration to seconds since t.Sub() return value is in nanoseconds
	elapsed := float64(t.Sub(start)) / math.Pow(10, 9)
	fmt.Printf("Time elapsed: %f", elapsed)
	return elapsed
}
