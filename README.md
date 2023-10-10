# 

Alimov Said

# websocket-chat-fastapi-redis_py

Проект представляет собой чат для общения пользователей в онлайне - без необходимости обновлять страницу чата.
```
git clone https://gitlab.com/DJWOMS/junov_net.gi
```

## Запуск проекта
1) Создаем окружение и инсталируем зависимости
```
pip install -r requirements.txt 
```
2) Запускаем проект коммандой:
```
uvicorn chat-server:app --reload
```
3) Переходим по ссылке: http://127.0.0.1:8000
## Folders
- templates - Папка с шаблонами для работы фронта
- requirements - Файл с зависимостями
- chat-server - сам сервер FastApi в котором проходит логика
- service - Файл с дополнительными пользовательскими функциями необходимыми в работе

## Используемы инструменты
- python - 3.10
- FastApi
- Redis
