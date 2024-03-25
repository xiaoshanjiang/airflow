#!/bin/bash
kill -9 $(cat airflow-webserver.pid)
kill -9 $(cat airflow-scheduler.pid)
rm airflow-webserver.pid
rm airflow-scheduler.pid