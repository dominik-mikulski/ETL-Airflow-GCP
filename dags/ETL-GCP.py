#Setup connection in Airlow UI -> Admin -> Connections. Conn_id=openweather, Type: HTTP, Host: api.openweathermap.org, Extra: {"api key": "your key"}
#Setup variable in Airflow UI -> Admin -> Variables. Key: gcp_project, Value: your GCP project id from GCP console

# imports important for Airflow
import pendulum #Ariflow requires pendulum for datetime management
from airflow.sdk import dag, task
from airflow.providers.standard.operators.python import PythonOperator
from google.cloud import bigquery


# Import Modules for code
from airflow.sdk.bases.hook  import BaseHook #allows to get connection info from Airflow UI
from airflow.models import Variable #allows to get variables from Airflow UI
import requests
import pandas as pd
#import datetime as dt


@dag(
    dag_id="ETL-Airflow-GCP",
    schedule='@hourly', #run the job every hour
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"), #start date of the DAG
    catchup=False, #do not catch up on past runs
    tags=['ETL-Airflow-GCP','ETL'], #tag for easier searching in Airflow UI
    )
def ETL():
    """This DAG will pull current weather from weatherapi.com every hour and store it in google bigquery table"""

    @task()
    def extract():
        """Extract current weather data from weatherapi.com"""
        # Get the OpenWeather API key from Airflow Connection
        conn = BaseHook.get_connection("openweather")
        api_key = conn.extra_dejson.get("api_key")  # <-- read key from Extras
        
        #set connection parameters
        payload = {'appid': api_key,'q': 'Krakow','units': 'metric'}
        
        #connect and raise error if bad response
        r = requests.get(f'https://{conn.host}/data/2.5/weather',params=payload,timeout=10)
        r.raise_for_status() #will raise an error for bad responses        
        
        # Get data as JSON
        data = r.json()
        return {"city": data["name"],
            "country": data["sys"]["country"],
            "temp_c": data["main"]["temp"],
            "humidity_pct": data["main"]["humidity"],
            "wind_speed_mps": data["wind"]["speed"],
            "weather_main": data["weather"][0]["main"],
            "weather_desc": data["weather"][0]["description"],
            "ts_unix": data["dt"],
            }
   
    @task()
    def transform(clean_data: dict) -> list[dict]:
        """Should do transformation for now only changes date to iso format"""
        clean_data["ts_iso"] = pd.to_datetime(clean_data["ts_unix"], unit="s").isoformat()
        return [clean_data]
    
    # update with your GCP project, dataset and table
    PROJECT_ID = Variable.get("gcp_project")  # your GCP project
    DATASET_ID = "airflow_gcp_dataset"
    TABLE_ID = "current_weather"

    # Define schema
    TABLE_SCHEMA = [
        bigquery.SchemaField("city", "STRING"),
        bigquery.SchemaField("country", "STRING"),
        bigquery.SchemaField("temp_c", "FLOAT"),
        bigquery.SchemaField("humidity_pct", "INTEGER"),
        bigquery.SchemaField("wind_speed_mps", "FLOAT"),
        bigquery.SchemaField("weather_main", "STRING"),
        bigquery.SchemaField("weather_desc", "STRING"),
        bigquery.SchemaField("ts_unix", "INTEGER"),
        bigquery.SchemaField("ts_iso", "STRING"),
    ]

    @task()
    def load(rows):
        client = bigquery.Client(project=PROJECT_ID)

        # --- Ensure dataset exists ---
        dataset_ref = client.dataset(DATASET_ID)
        try:
            client.get_dataset(dataset_ref)
        except Exception:
            client.create_dataset(bigquery.Dataset(dataset_ref))
            print(f"Created dataset {DATASET_ID}")

        # --- Ensure table exists ---
        table_ref = dataset_ref.table(TABLE_ID)
        try:
            client.get_table(table_ref)
        except Exception:
            table = bigquery.Table(table_ref, schema=TABLE_SCHEMA)
            client.create_table(table)
            print(f"Created table {TABLE_ID}")

        # --- Insert rows ---
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            print("Errors inserting rows:", errors)
        else:
            print(f"Inserted {len(rows)} rows into {TABLE_ID}")
        
    # Define task dependencies
    data=extract()
    clean_data=transform(data)
    load(clean_data)
    
# Instantiate the DAG
etl_dag = ETL()