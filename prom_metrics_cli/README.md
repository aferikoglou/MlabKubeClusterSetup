## Command line interface for extracting and visualising prometheus metrics by querying prometheus http api.

This project is written mainly in go 1.17 using multithreaded http requests and python for visualising the results with matplotlib.
Matplotlib figures are saved in "./plot/figures" as png files with ascending id.

## Install:
```bash
chmod +x install.sh
./install.sh
go run main.go --help
```

You can find an example query in "instant_query_up_test.sh" which makes an instant query to 'api/v1/query' (default value for -p argument) path to check if the system is up:
``` bash
./instant_query_up_test.sh
```

You can find a more sophisticated script for extracting dcgm metrics "dcgm_metrics_range_query.sh" which makes range queries for all the dcgm metrics for the past 30 seconds. You can run it with:
``` bash
./dcgm_metrics_range_query.sh
```
