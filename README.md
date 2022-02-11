# Local Observability Stack
Author: Andres Kepler <andres.kepler@entigo.com>
Date: 11.02.2022


This project demonstrates Local Observability stack using 
* Prometheus
* Grafana

## Components

* alertmanager - Prometheus alertmanager
* demo-app - Python written demo application for promethus exporter
* grafana - Metrics visualisation app
* prometheus - Metrics collelector and Time Series Database
* grafana-init - initializes grafana. Appends 2. organisation 


# Requiments
* docker
* docker-compose

# How to bootstrap

0. Rename `.env.example` file to `.env` and change values

       GRAFANA_ADMIN_USER=admin
       GRAFANA_ADMIN_PASSWORD=<change_me>
       GRAFANA_ORG_NAME=<My_Super_Org>

1. Build containres

    `docker-compose build`

2. Bring it up

    `docker-compose up -d`

## Applications entrypoints

* Grafana http://localhost:3000

* Prometheus http://localhost:9090



