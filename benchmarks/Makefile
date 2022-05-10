all: tidy build

tidy:
	go mod tidy; go mod vendor

build:
	go build -o bin/main main.go
