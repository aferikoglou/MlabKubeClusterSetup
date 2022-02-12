# Prometheus Setup Instructions

## Create monitoring namespace and add prometheus operator/adapter, grafana, alert manager and exporters in the cluster:
```bash 
git clone https://github.com/prometheus-operator/kube-prometheus.git
cd kube-prometheus
kubectl apply --server-side -f manifests/setup
until kubectl get servicemonitors --all-namespaces ; do date; sleep 1; echo ""; done
kubectl apply -f manifests

# Port forward grafana:
kubectl --namespace monitoring port-forward svc/grafana 3000
# Port forward prometheus:
kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090
# Port forward alert manager:
kubectl --namespace monitoring port-forward svc/alertmanager-main 9093
# Check this out for more: 
# https://computingforgeeks.com/setup-prometheus-and-grafana-on-kubernetes/
```
## A couple useful aliases I like to use monitoring:
```bash
alias graf="kubectl --namespace monitoring port-forward svc/grafana 3000"
alias prom="kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090"
```

**You can also permanently add all of them in your shell script configuration with the following command:**
```bash
cat <<EOF | tee -a ~/.bashrc && source ~/.bashrc

alias graf="kubectl --namespace monitoring port-forward svc/grafana 3000"
alias prom="kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090"
EOF

# In case you are using zsh as the default shell for your user you could use the same command as above by replacing "bashrc" either with "zshrc" or "profile"
```