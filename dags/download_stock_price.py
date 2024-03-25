from __future__ import annotations

import yfinance as yf
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from datetime import timedelta


default_args = {
    "owner": "airflow",
    "email": ["example@com.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
}


def get_file_path(ticker):
    # NOT SAVE in distributed system.
    return f"/home/jasonj/devs/airflow/stock_data/{ticker}.csv"


def get_tickers(context):
    stock_list = Variable.get("stock_list_json", deserialize_json=True)

    stocks = (
        context["dag_run"].conf.get("stocks", None)
        if ("dag_run" in context and context["dag_run"] is not None)
        else None
    )

    if stocks:
        stock_list = stocks

    return stock_list


def download_prices(*args, **context):
    stock_list = get_tickers(context)
    valid_tickers = []

    for ticker in stock_list:
        dat = yf.Ticker(ticker)
        hist = dat.history(period="1mo")

        if hist.shape[0] > 0:
            valid_tickers.append(ticker)
        else:
            continue

        with open(get_file_path(ticker), "w") as writer:
            hist.to_csv(writer, index=True)
        print(f"Downloaded {ticker}")
    return valid_tickers


with DAG(
    dag_id="Download_Stock_List",
    default_args=default_args,
    description="This DAG download stock price.",
    schedule_interval="5 5 * * *",
    start_date=days_ago(2),
    tags=["airflow"],
    catchup=False,
    max_active_runs=1,
) as dag:
    dag.doc_md = """
    This DAG download stock price.
    """
    download_task = PythonOperator(
        task_id="download_prices",
        python_callable=download_prices,
    )
