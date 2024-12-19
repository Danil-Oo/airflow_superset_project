from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from requests.auth import HTTPBasicAuth
import requests
import logging

default_args = {
    'owner': 'Danil',
    'start_date': datetime(2024, 1, 1),
}

SUPSET_URL = 'http://176.114.91.249:8088/superset/'
DASHBOARD_ID = 1 
# 'http://176.114.91.249:8088/superset/dashboard/1/'
        
def refresh_superset_dashboard():
    session = requests.Session()
    
    auth_data = {
        'username': 'admin',  
        'password': 'admin',  
        'provider': 'db',
        'refresh': True
    }
    response = session.post(f"{SUPSET_URL}/api/v1/security/login", json=auth_data)
    
    if response.status_code != 200:
        logging.error("Failed to log in to Superset.")
        return

    refresh_response = session.post(f"{SUPSET_URL}/api/v1/dashboard/{DASHBOARD_ID}/refresh")
    
    if refresh_response.status_code == 200:
        logging.info("Dashboard refreshed successfully in Superset.")
    else:
        logging.error(f"Failed to refresh dashboard: {refresh_response.json()}")

with DAG(
    dag_id="refreshing_superset",
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False,
) as dag:
    refresh_dashboard_task = PythonOperator(
        task_id='refresh_dashboard',
        python_callable=refresh_superset_dashboard,
        provide_context=True,
    )
    
refresh_dashboard_task