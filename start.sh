#!/bin/bash
airflow webserver -p 8080 -D
airflow scheduler -D