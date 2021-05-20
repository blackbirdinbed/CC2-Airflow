from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

import pandas as pd
from sqlalchemy import create_engine

default_args = {
    'owner': 'Ivan Perez Fernandez',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['blackbirdinbed@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=20),
}

# DAG initialization

dag = DAG(
    'airflow-forecast-prediction',
    default_args=default_args,
    description='DAG for forecasting humidity and temperature from multiple sources',
    schedule_interval=timedelta(days=1),
)

# Prepare the route of the workflow

GetReady = BashOperator(
    task_id='GetReady',
    depends_on_past=False,
    bash_command='mkdir /tmp/workflow/',
    dag=dag,
)

# Download the data sources

DownloadDataA = BashOperator(
    task_id='DownloadDataA',
    depends_on_past=False,
    bash_command='wget --output-document /tmp/workflow/humidity.csv.zip https://github.com/manuparra/MaterialCC2020/raw/master/humidity.csv.zip',
    dag=dag,
)

DownloadDataB = BashOperator(
    task_id='DownloadDataB',
    depends_on_past=False,
    bash_command='curl -L -o /tmp/workflow/temperature.csv.zip https://github.com/manuparra/MaterialCC2020/raw/master/temperature.csv.zip',
    dag=dag,
)

# Unzip

Unzip = BashOperator(
    task_id='Unzip',
    depends_on_past=False,
    bash_command='unzip "/tmp/workflow/*.csv.zip" -d /tmp/workflow/',
    dag=dag,
)

# Clone the services from our repository

CloneSourceV1 = BashOperator(
    task_id='CloneSourceV1',
    depends_on_past=False,
    bash_command='git clone -b v1 https://github.com/blackbirdinbed/CC2-Airflow.git /tmp/workflow/servicev1',
    dag=dag,
)

CloneSourceV2 = BashOperator(
    task_id='CloneSourceV2',
    depends_on_past=False,
    bash_command='git clone -b v2 https://github.com/blackbirdinbed/CC2-Airflow.git /tmp/workflow/servicev2',
    dag=dag,
)

# Set up the DB

SetDB = BashOperator(
    task_id='SetDB',
    depends_on_past=False,
    bash_command='docker-compose -f ~/airflow/dags/docker-compose.yml up -d db',
    dag=dag,
)

# Prepare the data and insert in the DB


def prepare_data():

    # Prepare

    df_temperature = pd.read_csv('/tmp/workflow/temperature.csv', header=0)
    df_humidity = pd.read_csv('/tmp/workflow/humidity.csv', header=0)

    df_temperature.rename(
        columns={'San Francisco': 'Temperature'}, inplace=True)
    df_humidity.rename(columns={'San Francisco': 'Humidity'}, inplace=True)

    df_temperature = df_temperature.loc[:, ['datetime', 'Temperature']]
    df_humidity = df_humidity.loc[:, ['datetime', 'Humidity']]

    merged = df_temperature.merge(df_humidity, on='datetime')

    merged["Temperature"] = merged["Temperature"].fillna(
        merged["Temperature"].mean())
    merged["Humidity"] = merged["Humidity"].fillna(merged["Humidity"].mean())

    # Insert

    engine = create_engine('mysql+pymysql://ivan:ivan@localhost/forecast')
    merged.to_sql('forecast', con=engine, if_exists='replace')


PrepareData = PythonOperator(
    task_id='LimpiaCargaDatos',
    python_callable=prepare_data,
    dag=dag,
)

# Tests

TestServiceV1 = BashOperator(
    task_id='TestServiceV1',
    depends_on_past=False,
    bash_command='export HOST=localhost && cd /tmp/workflow/servicev1/test/v1 && pytest -q test.py',
    dag=dag,
)

TestServiceV2 = BashOperator(
    task_id='TestServiceV2',
    depends_on_past=False,
    bash_command='export HOST=localhost && cd /tmp/workflow/servicev2/test/v2 && pytest -q test.py',
    dag=dag,
)

# Run the containers

RunServices = BashOperator(
    task_id='RunServices',
    depends_on_past=False,
    bash_command='docker-compose -f ~/airflow/dags/docker-compose.yml up -d',
    dag=dag,
)

# -------- Dependencies -------- #

GetReady >> [CloneSourceV1, CloneSourceV2, DownloadDataA, DownloadDataB, SetDB]
[DownloadDataA, DownloadDataB] >> Unzip
[Unzip, SetDB] >> PrepareData
[PrepareData, CloneSourceV1] >> TestServiceV1
CloneSourceV2 >> TestServiceV2
[TestServiceV1, TestServiceV2] >> RunServices
