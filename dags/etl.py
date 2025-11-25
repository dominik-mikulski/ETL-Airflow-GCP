#Code requires an API key from https://openweathermap.org/. Setup account at it, copy API below. 
OPENWEATHER_API_KEY = "PASTE YOUR API KEY HERE without spaces"

# imports important for Airflow
import pendulum #Ariflow requires pendulum for datetime management
from airflow.sdk import dag, task
from airflow.providers.standard.operators.python import PythonOperator


# Import Modules for code
import json
import requests
import pandas as pd
from pandas import DataFrame, json_normalize
import datetime as dt
import psycopg2 

@dag(
    dag_id="MyETL",
    schedule='@hourly', #run the job every hour
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"), #start date of the DAG
    catchup=False, #do not catch up on past runs
    tags=['MyETL'], #tag for easier searching in Airflow UI
    )
def ETL():
    """This DAG will pull current weather from weatherapi.com every hour and store it in postgres db"""
    @task()
    def extract():
        """Extract current weather data from weatherapi.com"""
        #Insert your API key into Key field below
        payload = {'appid': OPENWEATHER_API_KEY,'q': 'Krakow','units': 'metric'}
        r = requests.get('https://api.openweathermap.org/data/2.5/weather',params=payload,timeout=10)
        
        # Get the json
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

        # @task()
        # def transform(clean_data: dict) -> pd.DataFrame:
        #     """Transform the extracted data into a flat table format suitable for loading into Postgres"""
        #     df = pd.DataFrame([clean_data])
        #     df["ts_iso"] = pd.to_datetime(df["ts_unix"], unit="s")
        #     return df
        
    @task()
    def transform(clean_data: dict) -> dict:
        """Transform the extracted data into a flat table format suitable for loading into Postgres"""
        clean_data["ts_iso"] = pd.to_datetime(clean_data["ts_unix"], unit="s").isoformat()
        return clean_data
    
    @task()
    def load(row: dict): 
        """Load the transformed data into a Postgres database"""
        df = pd.DataFrame([row])
        # Database connection parameters
        conn = psycopg2.connect(
            host="postgres", #hostname of the postgres container
            database="airflow", #database name
            user="airflow", #username
            password="airflow" #password
        )
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS weather (
                id SERIAL PRIMARY KEY,
                city VARCHAR(100),
                country CHAR(2),
                temp_c NUMERIC(5,2),
                humidity_pct SMALLINT,
                wind_speed_mps NUMERIC(5,2),
                weather_main VARCHAR(50),
                weather_desc VARCHAR(100),
                ts_unix BIGINT,
                ts_iso TIMESTAMP,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO weather (
                    city, country, temp_c, humidity_pct, wind_speed_mps,
                    weather_main, weather_desc, ts_unix, ts_iso
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                row["city"], row["country"], row["temp_c"], row["humidity_pct"],
                row["wind_speed_mps"], row["weather_main"], row["weather_desc"],
                row["ts_unix"], row["ts_iso"]
            ))
        
        conn.commit()
        cur.close()
        conn.close()

    # Define task dependencies
    weather_json = extract()
    weather_data_transformed = transform(weather_json)
    load(weather_data_transformed)

# Instantiate the DAG
etl_dag = ETL()
        