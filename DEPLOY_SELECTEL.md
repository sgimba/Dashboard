# Миграция на Selectel - Полная инструкция

## ✅ Зачем мигрировать на Selectel?

- **Стоимость: 200 ₽/месяц** (вместо 1,541 ₽ в Yandex Cloud)
- **Экономия: 87%** (~13,428 ₽/год!)
- **Посекундная тарификация** (как Yandex Cloud)
- **Надежная инфраструктура** (Tier III дата-центры)
- **API + Terraform** для управления

---

## 📋 Шаг 1: Регистрация на Selectel

1. Перейди на https://selectel.ru
2. Нажми **"Создать аккаунт"**
3. Заполни:
   - Электронная почта
   - Пароль
   - Согласие на обработку данных
4. Подтверди почту

---

## 🚀 Шаг 2: Создание VDS сервера

1. Войди в Панель управления: https://my.selectel.ru
2. Перейди в **"Cloud Servers"** или **"Облачные серверы"**
3. Нажми **"Создать сервер"** (Create Server)
4. Выбери конфигурацию:
   - **ОС**: Ubuntu 24.04 LTS
   - **Конфигурация**: 1 vCore, 1 GB RAM, 10 GB SSD
   - **Цена**: 200 ₽/месяц
5. Нажми **"Создать"**

---

## 🔐 Шаг 3: Получение доступа

После создания сервера ты получишь:
- **IP адрес**: 1.2.3.4 (например)
- **Пароль root** (отправится на почту)

Подключись по SSH:
```bash
ssh root@1.2.3.4
# Введи пароль
```

---

## 🐳 Шаг 4: Установка Docker

```bash
# Обновить систему
sudo apt-get update
sudo apt-get upgrade -y

# Установить Docker
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker root

# Установить Git
sudo apt-get install -y git
```

---

## 📦 Шаг 5: Развернуть приложение

```bash
# Клонировать репозиторий
cd /root
git clone https://github.com/sgimba/Dashboard.git
cd Dashboard

# Собрать Docker образ
docker build -t streamlit-dashboard:latest .

# Запустить контейнер
docker run -d \
  --name streamlit-app \
  -p 8501:8501 \
  -v /root/Dashboard:/app \
  streamlit-dashboard:latest

# Проверить статус
docker ps
docker logs streamlit-app
```

---

## 🌐 Шаг 6: Проверка доступа

Перейди по адресу:
```
http://1.2.3.4:8501
```

(Замени 1.2.3.4 на твой реальный IP адрес)

---

## 💰 Стоимость сравнение

| Параметр | Yandex Cloud | Selectel |
|----------|-------------|----------|
| **Цена/месяц** | 1,541 ₽ | 200 ₽ |
| **Цена/год** | 18,492 ₽ | 2,400 ₽ |
| **Экономия** | - | **16,092 ₽/год** |
| **Посекундная тарификация** | ✅ | ✅ |
| **Надежность** | ✅ | ✅ |

---

## ⚙️ Полезные команды

```bash
# Остановить контейнер
docker stop streamlit-app

# Удалить контейнер
docker rm streamlit-app

# Просмотреть логи
docker logs -f streamlit-app

# Пересобрать образ
docker build -t streamlit-dashboard:latest .

# Перезагрузить сервер
sudo reboot
```

---

## 🆘 Проблемы и решения

### Ошибка: Permission denied при docker
- Решение: `sudo usermod -aG docker $USER` и перелогинься

### Порт 8501 не доступен
- Проверь брандмауэр: `sudo ufw allow 8501`

### Git не найден
- Установи: `sudo apt-get install -y git`

---

## 📞 Поддержка Selectel

- **Email**: support@selectel.ru
- **Тел**: +7 (800) 555-06-75
- **Сайт**: https://selectel.ru

---

## ✨ Результат

После миграции ты сэкономишь:
- **16,092 ₽ в год** 💰
- **1,341 ₽ в месяц** 📉

Приложение будет работать так же стабильно, но за дешевле!
