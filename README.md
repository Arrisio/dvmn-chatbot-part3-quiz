### Курс "Чат-боты на Python"
https://dvmn.org/modules/chat-bots/lesson/devman-bot/

## Урок 4
[Проводим викторину](https://dvmn.org/modules/chat-bots/lesson/quiz-bot/#1)  


## Установка

1. Клонировать репозиторий:
```
git clone https://github.com/Arrisio/dvmn-chatbot-part3-quiz.git
```

2. Требуется определеить следующие переменные окружения:
```
TG_BOT_TOKEN='Ваш токен'
VK_TOKEN='Ваш токен'

```
Следующие переменные окружения опциональны:
- `REDIS_HOST` - IP или hostname базы redis. По умолчанию - `localhost`.  
- `REDIS_PORT` - порт базы redis. По умолчанию - `6379`.  
- `LOG_LEVEL` - уровень логирования, варианты значений - см. официальную документацию [Loguru](https://loguru.readthedocs.io/en/stable/api/logger.html). По умолчанию - `INFO`.  

3. Установить зависимости:
```
pip3 install -r requirements.txt
```

## Запуск
```
python3 main.py tg
```
![](resources/examination_tg.gif)


```
python3 main.py vk
```
![](resources/examination_vk.gif)

