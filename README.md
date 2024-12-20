# Инструкция по развертыванию платформы с PostgreSQL и Superset
## 1. Установка Docker и настройка
### 1.1 Устанавливаем Docker
```bash
sudo apt-get update
sudo apt-get install docker.io
```
### 1.2 Создаем сеть для будующих двух контейнеров
```bash
docker network create app_net
```
### 1.3 Запуск контейнера с PostgresDB
* Cоздаем хранилище для контейнера 
```bash
docker volume create postgres_vol
```
* Запуск контейнера (логин и пароль запомнить!)
```bash  
docker run -d \                
    --name <Ваше имя для контейнера> \ 
    -e POSTGRES_USER=<Логин> \
    -e POSTGRES_PASSWORD=<Пароль> \ 
    -e POSTGRES_DB=test_app \
    -v postgres_vol:/var/lib/postgresql \
    postgres:15
```
* Заходим в контейнер
```bash
docker exec -it <Название контейнера с постгресом> bash
```
* Проваливаемся в папку(тут будут храниться все наши базы данных)
```bash
cd /var/lib/postgresql/
```
* Скачиваем пакеты
```bash
apt-get update
apt-get install -y wget  
```
* Скачиваем датасет
```bash
wget path/to/credit_clients.csv
```
* Заходим в PSQL
```bash
psql -U postgres
```
* Создаем базу данных
```bash
CREATE DATABASE <Имя БД>;
```
* Заходим в бд
```bash
\c <Имя БД>
```
* Создаем таблицу (пример, у вас может отличаться)
```bash
CREATE TABLE credit_clients (
    CustomerId BIGINT PRIMARY KEY, 
    Date TEXT,                
    Surname TEXT,                 
    CreditScore INT,             
    Geography TEXT,             
    Gender TEXT,               
    Age INT,                     
    Tenure INT,                 
    Balance FLOAT,              
    NumOfProducts INT,        
    HasCrCard INT,                 
    IsActiveMember INT,           
    EstimatedSalary FLOAT,        
    Exited INT                     
);
```
* Проверяем создалась ли таблица
```bash
\dt
```
* Копируем данных в нашу таблицу
```bash
COPY credit_clients(CustomerId, Date, Surname, CreditScore, Geography, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary, Exited)
FROM '/var/lib/postgresql/credit_clients.csv'
DELIMITER ','
CSV HEADER;
```
* Выводим первы 10 строк
```bash
SELECT * FROM credit_clients LIMIT 10;
```
### 1.4 Запуск контейнера с Superset
* Запускаем контейнер 
```bash
docker run -d \
    -p 8088:8088 \
    -e "SUPERSET_SECRET_KEY=$(openssl rand -base64 42)" \
    --name superset \
    apache/superset
```
* После запускаем команду для добавления пользователя с правами админа (также запомним логин и пароль)
```bash
docker exec -it superset superset fab create-admin \
            --username <Логин> \
            --firstname <Ваше имя> \
            --lastname <Ваше фамилия> \
            --email <почта> \
            --password <пароль>
```
* Устанавливаем библиотеку для подключения с PostgresDB
```bash
docker exec -it superset pip install psycopg2-binary
```
* Обновляем данные в superset
```bash
docker exec -it superset superset db upgrade
```
* Запускаем сервер
```bash
docker exec -it superset superset init
```
### 1.5 Подключаем два контейнера в одну сеть
```bash
docker network connect <имя вашей сети> <имя контейнера postgres>
```
```bash
docker network connect <имя вашей сети> <имя контейнера superset>
```
## 2. Настраиваем Superset
### 2.1 Подготовка Superset
* Перезапускаем докер
```bash
docker restart superset
```
* Прописываем в локальном терминале
```bash
ssh -L  8088:localhost:8088 <user_name>@<ip-address>
```
* В браузере переходим по адресу: http://localhost:8088/login/
* Username
`<Логин от Superset>`
* Password
`<Пароль от Superset>`
### 2.2 Подключение БД к Superset
* Host
`<Название контейнера с постгресом>`
* Port
`5432`
* Database name
`<Имя БД>`
* Username
`<Логин от Postgres>`
* Password
`<Пароль от Postgres>`
## 3. Финал
* Если ничего не упало, поздравляю! Всегда валидируйте себя на каждой шаге. В помощь логи:
```bash
docker logs <имя контейнера>
```
# Инструкция по развертыванию Airflow 
## 1. Установка miniconda
### 1.1 Загружаем последнюю версию Miniconda, открыв терминал и выполнив команду
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```
### 1.2 Устанавливаем миниконду 
```bash
bash ~/Miniconda3-latest-Linux-x86_64.sh
```
### 1.3 Обновляем терминал 
```bash
source ~/.bashrc
```
### 1.4 Деактивиурем окружение ```base```
```bash
conda deactivate
```
### 1.5 Создаем окружение  ```airflow_env```
```bash
conda create airflow_env`
```
### 1.6 Активируем окружение  ```airflow_env```
```bash
conda activate airflow_env
```
## 2. Установка Airflow
### 2.1 Исполняем команду, чтобы Airflow смог обнаружить домашнюю директорию 
```bash
export AIRFLOW_HOME=~/airflow
```
### 2.2 Устанавливаем Airflow
* Активируем окружение airflow_env
* Выполняем команду
```bash
AIRFLOW_VERSION=2.10.4

# Extract the version of Python you have installed. If you're currently using a Python version that is not supported by Airflow, you may want to set this manually.
# See above for supported versions.
PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example this would install 2.10.4 with python 3.8: https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.8.txt

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```
### 2.3 Запускаем графический интерфейс Airflow
* Устанавливаем библиотеку ```pandas```, она понадобится для исполния одного из DAG-файлов
```bash
pip install pandas
```
* Открываем "физически" папку ```airflow``` в vscode на сервере
* Выполняем команду
```bash
airflow db migrate
```
* Создаем пользователя в Airflow
```bash
airflow users create \
    --username admin \
    --firstname <имя> \
    --lastname <фамилия> \
    --role Admin \
    --email <почта>
```
* Переходим в папку ```airflow``` через терминал
```bash
cd airflow/
```
* Прокидываем порт, чтобы открыть графический интерфейс Airflow в браузере
```bash
airflow webserver --port 8080
```
* В терминале смотрим логи, контролируем процесс
### 2.4 Запускаем scheduler
* Открываем новый терминал в vscode
* Если активировано окружение ```base```, выполняем команду
```bash
conda deactivate
```
* Активируем окружение ```airflow_env```
* Переходим в терминале в папку ```airflow```
* Выполняем команду
```bash
airflow scheduler
```
* Смотрим логи, валидируем себя
### 2.5 Подготовка директории и работа с Airflow 
* Внутри папки ```airflow``` создаем пустой файл с названием ```credit_clients.csv```
* Создаем папку ```dags``` внутри папки ```airflow``` на сервере, в папку ```dags``` вставляем DAG-файлы из данного репозитория
* Обновляем файлы сочетанием клавиш ```ctrl+s```
* Открываем графический интерфейс Airflow, ждем пока наши DAG-файлы появятся в списке DAGs (может занять несколько минут)
* Открываем каждый DAG-файл по отедельности и запускаем его кнопкой в правом верхнем углу ```Trigger DAG```
## 3. Логи
* Не забывайте проверять логи, как в терминале, так и непосредственно в интерфейсе Airflow для каждого DAG'а и для каждой задачи, это спасет ваши нервы!
