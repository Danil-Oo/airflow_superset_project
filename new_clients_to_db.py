from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd
import requests

default_args = {
    'owner': 'Danil',
    'start_date': datetime(2024, 1, 1),
}

def download_file(**kwargs):
    url = "https://9c579ca6-fee2-41d7-9396-601da1103a3b.selstorage.ru/credit_clients.csv"
    local_path = '/root/airflow/credit_clients.csv'
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully: {local_path}")
    else:
        raise ValueError(f"Failed to download file: {response.status_code}")
    
    
def load_new_customers_to_db(**kwargs):
    pg_hook = PostgresHook(postgres_conn_id='Danil')  
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT customerid FROM credit_clients;")
    existing_ids = set(row[0] for row in cursor.fetchall())
    print(f"Fetched {len(existing_ids)} existing CustomerIds from database.")
    
    file_path = '/root/airflow/credit_clients.csv'
    if file_path:
        data = pd.read_csv(file_path)
        print(f"Loaded {len(data)} rows from file.")
        
        new_data = data[~data['CustomerId'].isin(existing_ids)]
        print(f"Filtered {len(new_data)} new rows.")
    
    if not new_data.empty:
        for _, row in new_data.iterrows():
            cursor.execute(
                """
                INSERT INTO credit_clients (customerid, date, surname, creditscore, geography, gender, age, tenure, balance, numofproducts, hascrcard, isactivemember, estimatedsalary, exited)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (row['CustomerId'], row['Date'], row['Surname'], row['CreditScore'], row['Geography'], row['Gender'], row['Age'], row['Tenure'], row['Balance'],
                 row['NumOfProducts'], row['HasCrCard'], row['IsActiveMember'], row['EstimatedSalary'], row['Exited'])
            )
        conn.commit()
        print("New data successfully loaded into PostgreSQL.")
    else:
        print("No new data to load.")
    cursor.close()
    conn.close()
    
    
with DAG(
    dag_id="loading_new_clients_to_db",
    default_args=default_args,
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    download_task = PythonOperator(
        task_id='download_file_w_all_clients',
        python_callable=download_file,
    )
    
    load_task = PythonOperator(
        task_id='add_new_clients_to_db',
        python_callable=load_new_customers_to_db,
        provide_context=True,
    )
    
    
download_task >> load_task 
