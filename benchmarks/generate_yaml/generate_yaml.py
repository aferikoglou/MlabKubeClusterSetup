import argparse
import sys
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

def generate_yaml(path=None):
    file = os.path.join(dir_path, "template.yaml")

    if path:
        pods_path = path
    else:
        pods_path = os.path.join(dir_path, "../mlperf_gpu_pods")

    if not os.path.exists(pods_path):
        ans = input(f"Directory {pods_path} doesn't exist, would like to create it?[y/n]\n>>")
        if ans == 'y' or ans == 'Y':
            os.makedirs(pods_path)
        else:
            sys.exit(0)
    else:
        if len(os.listdir(pods_path)) > 0:
            ans = input(f"Directory {pods_path} not empty, would like to delete files?[y/n]\n>>")
            if ans == 'y' or ans == 'Y':
                for f in os.listdir(pods_path):
                    os.remove(os.path.join(pods_path, f))
            else:
                sys.exit(0)
                
    scenarios = ['SingleStream', 'MultiStream', 'Server', 'Offline']
    times = ['1', '10', '100']
    backends = ['onnxruntime', 'pytorch', 'tf', 'tflite']
    models = ['mobilenet', 'resnet50', 'ssd-mobilenet', 'ssd-resnet34']

    data = {
        'mobilenet': 'imagenet2012',
        'resnet50': 'imagenet2012',
        'ssd-mobilenet': 'coco-300',
        'ssd-resnet34': 'coco-1200',
    }

    with open(file, 'r') as f:
        lines = f.read()

    for backend in backends:
        for model in models:        
            for scenario in scenarios:
                for time in times:
                    new_lines = lines.replace(
                        "{scenario}", scenario
                    ).replace(
                        "{time}", time
                    ).replace(
                        "{model}", model
                    ).replace(
                        "{backend}", backend
                    ).replace("{data}", data[model]
                    )

                    with open(os.path.join(pods_path, f"{backend}-{model}-{scenario}-{time}.yaml"), "w") as f:
                        f.write(new_lines)
    print("Files created successfuly")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate yaml file for the gpu pods.')
    
    parser.add_argument('--path', action='store', required = False,  help="Directory to store output. Default=/benchmarks/mlperf_gpu_pods")

    args = parser.parse_args()

    generate_yaml(args.path)