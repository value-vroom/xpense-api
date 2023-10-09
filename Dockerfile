FROM alpine:3.18

RUN apk add python3 py3-pip nodejs

COPY . /app

WORKDIR /app

RUN pip install --upgrade setuptools
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

RUN prisma generate

CMD ["sh", "-c", "python3 app"]