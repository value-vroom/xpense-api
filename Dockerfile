FROM alpine:3.18

RUN apk add gcc python3 python3-dev libffi-dev musl-dev py3-pip nodejs

COPY . /app

WORKDIR /app

RUN pip install --upgrade setuptools
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

RUN prisma generate

RUN python3 app/utility/setup_db.py

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]