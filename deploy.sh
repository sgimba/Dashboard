#!/bin/bash

# Автоматизированный скрипт развертывания Streamlit приложения на Selectel
# Использование: bash deploy.sh

set -e  # Выйти при ошибке

echo "========================================"
echo "Развертывание Streamlit приложения"
echo "На Selectel VDS"
echo "========================================"
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для логирования
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Шаг 1: Обновление системы
echo ""
echo "Шаг 1: Обновление системы..."
apt-get update -qq
apt-get upgrade -y -qq
log_info "Система обновлена"

# Шаг 2: Установка Docker
echo ""
echo "Шаг 2: Установка Docker..."
apt-get install -y -qq docker.io > /dev/null 2>&1
systemctl start docker
systemctl enable docker
usermod -aG docker root
log_info "Docker установлен"

# Шаг 3: Установка Git
echo ""
echo "Шаг 3: Установка Git..."
apt-get install -y -qq git > /dev/null 2>&1
log_info "Git установлен"

# Шаг 4: Клонирование репозитория
echo ""
echo "Шаг 4: Клонирование репозитория..."
cd /root
if [ -d "Dashboard" ]; then
    log_warn "Папка Dashboard уже существует, обновляю..."
    cd Dashboard
    git pull origin main -q
    cd /root
else
    git clone https://github.com/sgimba/Dashboard.git -q
fi
cd Dashboard
log_info "Репозиторий готов"

# Шаг 5: Сборка Docker образа
echo ""
echo "Шаг 5: Сборка Docker образа..."
docker build -t streamlit-dashboard:latest . > /dev/null 2>&1
log_info "Docker образ собран"

# Шаг 6: Остановка старого контейнера (если существует)
echo ""
echo "Шаг 6: Проверка старого контейнера..."
if docker ps -a | grep -q streamlit-app; then
    log_warn "Старый контейнер найден, удаляю..."
    docker stop streamlit-app > /dev/null 2>&1
    docker rm streamlit-app > /dev/null 2>&1
fi

# Шаг 7: Запуск контейнера
echo ""
echo "Шаг 7: Запуск приложения..."
docker run -d \
  --name streamlit-app \
  -p 8501:8501 \
  -v /root/Dashboard:/app \
  streamlit-dashboard:latest > /dev/null 2>&1
log_info "Приложение запущено"

# Шаг 8: Проверка статуса
echo ""
echo "Шаг 8: Проверка статуса..."
sleep 2
if docker ps | grep -q streamlit-app; then
    log_info "Контейнер активен"
else
    log_error "Контейнер не запустился"
    docker logs streamlit-app
    exit 1
fi

# Получение IP адреса
echo ""
echo "========================================"
echo -e "${GREEN}✓ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!${NC}"
echo "========================================"
echo ""
echo "IP адрес сервера: $(hostname -I | awk '{print $1}')"
echo "Доступ к приложению: http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "Полезные команды:"
echo "  - Просмотр логов: docker logs -f streamlit-app"
echo "  - Остановка: docker stop streamlit-app"
echo "  - Перезагрузка: docker restart streamlit-app"
echo ""
log_info "Развертывание успешно завершено!"
