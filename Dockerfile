# Используем официальный образ Python
FROM python:3.10-slim

# Аргумент для включения фронтенда
ARG FRONTEND=false
ENV FRONTEND=${FRONTEND}

# Устанавливаем рабочую директорию
WORKDIR /GPT_translator

# Копируем исходники и зависимости для приложения
COPY app app
COPY frontend frontend
COPY requirements requirements
COPY config.yaml config.yaml
COPY run.sh run.sh

# Устанавливаем зависимости для приложения
RUN pip install --no-cache-dir -r requirements/app.txt

# Если передан аргумент FRONTEND, копируем и устанавливаем исходники и зависимости для фронтенда
RUN if [ "$FRONTEND" = "true" ] ; then \
        # Устанавливаем зависимости для фронтенда
        pip install --no-cache-dir -r requirements/frontend.txt; \
    fi

# Команда для запуска приложения
CMD ./run.sh

# Открываем порты
EXPOSE 8000 8502