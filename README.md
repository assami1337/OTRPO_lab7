# Клонирование репозитория
```
git clone https://github.com/assami1337/OTRPO_lab7.git && cd OTRPO_lab7
```
# Создание виртуального окружения
```
python3 -m venv venv
```
# Активация виртуального окружения
```
source venv/bin/activate || venv\Scripts\activate
```
# Установка зависимостей
```
pip install -r requirements.txt
```
# Копирование файла переменных окружения
```
cp .env.example .env
```
# Настройте переменные для подключения к rabbitmq в .env

# Запуск Producer для добавления ссылок в очередь
```
python producer.py
```
# Введите ссылку, например:
```
https://google.com
```
# Запуск Consumer для обработки очереди
```
python consumer.py
```
