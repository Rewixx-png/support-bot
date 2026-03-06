# Telegram Support Bot (Aiogram 3.x)

Асинхронный Telegram-бот поддержки с использованием системы топиков в личных сообщениях (Telegram Bot API 9.4+).

## Особенности
- Создание топиков (форумов) прямо в ЛС пользователя и владельца.
- Поддержка любых медиафайлов (фото, видео, гс, кружочки, документы).
- Асинхронная база данных SQLite3 (`aiosqlite`).
- Цветные Inline-кнопки и HTML5-теги `<blockquote>`.
- Модульная архитектура (отдельные файлы для хендлеров, клавиатур, стейтов).

## Требования
- Python 3.11+
- Включенный **Threaded Mode** в `@BotFather` (Bot Settings -> Threaded Mode -> Enable).

## Настройка
1. Клонируйте репозиторий.
2. Скопируйте файл `.env.example` в `.env` (или создайте `.env`) и укажите ваши данные:
   - `BOT_TOKEN` — токен вашего бота от `@BotFather`.
   - `OWNER_ID` — ваш числовой Telegram ID.

## Установка и запуск

### Способ 1: Docker Compose (Рекомендуемый)
Убедитесь, что у вас установлены Docker и Docker Compose.
```bash
docker compose up -d --build
```
Для просмотра логов:
```bash
docker compose logs -f bot
```

### Способ 2: PM2 (Node.js Process Manager)
Подходит для серверов (Ubuntu/Debian), если вы не хотите использовать Docker.
Установка зависимостей:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv npm -y
sudo npm install -g pm2
python3 -m venv venv
source venv/bin/activate
pip install -r bot/requirements.txt
```
Запуск:
```bash
pm2 start bot/main.py --name support_bot --interpreter ./venv/bin/python
pm2 save
pm2 startup
```

### Способ 3: Screen (Простой фоновый запуск)
Установка зависимостей:
```bash
sudo apt install screen python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -r bot/requirements.txt
```
Запуск:
```bash
screen -S support_bot
python bot/main.py
```
*Чтобы выйти из экрана и оставить бота работать, нажмите `Ctrl+A`, затем `D`.*
*Чтобы вернуться к логам: `screen -r support_bot`.*