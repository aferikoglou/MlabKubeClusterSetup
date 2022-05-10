all: apt pip tidy build

apt:
	apt-get install -y python3-distutils
	apt-get install -y tk

pip:
	pip install -r requirements.txt

tidy:
	go mod tidy; go mod vendor

build:
	go build -o bin/main main.go
