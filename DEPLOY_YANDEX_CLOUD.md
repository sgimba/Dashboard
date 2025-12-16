# Настройка Streamlit На Yandex Cloud

## Основная информация

- **Машина**: streamlit-dashboard-app
- **IP адрес**: 158.160.201.215
- **Ос**: Ubuntu 24.04 LTS
- **Пользователь**: ubuntu
- **Кохстантинж**: 2 vCPU, 2 GB RAM, 20 GB SSD

## Пошаговые инструкции

### 1. Подключитесь к VM

```bash
ssh -l ubuntu 158.160.201.215
```

### 2. Обновите систему

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 3. Установите Docker

```bash
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

### 4. Первые авторизации в Docker

```bash
echo $USER
groups $USER
```

(If not 'docker', log out and log in again or use: `newgrp docker`)

### 5. Клонируйте репозиторий

```bash
cd /home/ubuntu
git clone https://github.com/sgimba/Dashboard.git
cd Dashboard
```

### 6. Соберите Docker-образ

```bash
docker build -t streamlit-dashboard:latest .
```

### 7. Запустите контейнер

```bash
docker run -d \
  --name streamlit-app \
  -p 8501:8501 \
  -v /home/ubuntu/Dashboard:/app \
  streamlit-dashboard:latest
```

### 8. Проверьте статус контейнера

```bash
docker ps
docker logs streamlit-app
```

## Принципы оптимального распределения

### На выходе приложения будет доступно по:

- **Публичный URL**: http://158.160.201.215:8501

## Остановка и очистка

```bash
# Остановить контейнер
 docker stop streamlit-app

# Удалить контейнер
 docker rm streamlit-app

# Обнововать изображение
 docker rmi streamlit-dashboard:latest
```

## Проблемы и решения

### Не работает доступ к app.py
- Убедитесь, что вы используете `app.py`, а не `app_full.py`
- Контейнер можно модифицировать, используя CMD аргументы

### Порт занят
```bash
sudo lsof -i :8501  # Проверить кто использует порт
sudo kill -9 <PID>  # Остановить процесс
```
