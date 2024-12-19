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
docker run --rm -d \
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
* Прописываем в локальном терминале
```bash
ssh -L  8080:localhost:8080 <user_name>@<ip-address>
```
* В браузере переходим по адресу: http://localhost:8080/login/
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
