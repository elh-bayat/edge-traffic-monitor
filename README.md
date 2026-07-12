# Edge Traffic Monitoring Platform

A production-grade IoT traffic monitoring system built with modern DevOps practices. Simulates 50 traffic cameras sending real-time data through a microservices pipeline, deployed on AWS EKS with full CI/CD automation.

## Architecture

```
[50 Camera Simulators] --> [FastAPI] --> [RabbitMQ] --> [Processor] --> [PostgreSQL]
                                |                            |
                          [Prometheus]              [Congestion Score]
                                |
                            [Grafana]
```

## Tech Stack

| Category | Technology |
|----------|-----------|
| API | Python FastAPI, Pydantic, Uvicorn |
| Messaging | RabbitMQ (AMQP) |
| Database | PostgreSQL, SQLAlchemy Async |
| Monitoring | Prometheus, Grafana |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes (AWS EKS) |
| Infrastructure | Terraform |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (ghcr.io) |
| Cloud | AWS (EKS, VPC, EC2, ELB) |

## Features

- Real-time simulation of 50 concurrent traffic cameras using asyncio
- Congestion scoring algorithm: speed_factor x 0.6 + count_factor x 0.4
- Message queue for decoupled, scalable data processing
- Async database writes with SQLAlchemy and asyncpg
- Prometheus metrics exposed on every service
- Grafana dashboards for live cluster and application monitoring
- CI/CD pipeline that tests, builds, and pushes Docker images on every commit
- Infrastructure as Code — entire AWS infrastructure in Terraform
- Kubernetes deployment with 2 API replicas and load balancing

## Quick Start (Local)

### Prerequisites

- Docker and Docker Compose
- Python 3.12

### Run locally

```bash
git clone https://github.com/elh-bayat/edge-traffic-monitor.git
cd edge-traffic-monitor
docker compose up --build
```

Services available after startup:

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- RabbitMQ Dashboard: http://localhost:15672 (guest/guest)
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Send a traffic reading
curl -X POST http://localhost:8000/api/v1/traffic \
  -H "Content-Type: application/json" \
  -d '{"camera_id":"cam-001","location":"Main St","vehicle_count":45,"average_speed_kmh":60,"weather":"clear"}'
```

## Deploy to AWS

### Prerequisites

- AWS account with CLI configured
- Terraform >= 1.0
- kubectl

### 1. Provision infrastructure

```bash
cd terraform
terraform init
terraform apply
```

### 2. Connect kubectl to the cluster

```bash
aws eks update-kubeconfig --region eu-west-1 --name edge-traffic-cluster
```

### 3. Create image pull secret

```bash
kubectl create secret docker-registry ghcr-secret \
  --namespace edge-traffic \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_PAT
```

### 4. Deploy application

```bash
kubectl apply -f k8s/
kubectl get pods -n edge-traffic
```

### 5. Destroy when done (to stop AWS charges)

```bash
kubectl delete service api -n edge-traffic
cd terraform && terraform destroy
```

## CI/CD Pipeline

Every push to main triggers two jobs:

1. Run Tests — runs pytest with FastAPI TestClient
2. Build and Push Images — builds api, processor, and simulator Docker images and pushes to ghcr.io

## Monitoring

The kube-prometheus-stack Helm chart is deployed in the monitoring namespace. Grafana shows live metrics for all pods in the edge-traffic namespace including CPU usage, memory utilization, and network bandwidth per pod.

## Project Structure

```
edge-traffic-monitor/
├── api/                  # FastAPI application
├── processor/            # RabbitMQ consumer + PostgreSQL writer
├── simulator/            # 50-camera traffic data generator
├── tests/                # pytest test suite
├── monitoring/           # Prometheus configuration
├── k8s/                  # Kubernetes manifests
├── terraform/            # AWS infrastructure (VPC + EKS)
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## How the Congestion Score Works

Each traffic reading from a camera contains vehicle count and average speed. The processor calculates a congestion score between 0 and 1:

- speed_factor = 1 - (speed / 300) — lower speed means higher congestion
- count_factor = vehicle_count / 500 — more vehicles means higher congestion
- congestion_score = speed_factor x 0.6 + count_factor x 0.4

A score above 0.7 indicates heavy congestion.
