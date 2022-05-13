all: apt pip tidy build

apt:
	sudo apt-get install -y python3-distutils
	sudo apt-get install -y tk

pip:
	pip install -r requirements.txt

tidy:
	go mod tidy; go mod vendor

build:
	go build -o bin/main main.go
