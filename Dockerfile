FROM python:3.8.1-alpine

ENV PYHTONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# creating a folder.
RUN mkdir -p /home/user

ENV HOME=/home/user
ENV APP_HOME=/home/user/web

WORKDIR ${APP_HOME}

RUN mkdir ${APP_HOME}/staticfiles
RUN mkdir ${APP_HOME}/media

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN apk add zlib zlib-dev jpeg-dev

RUN pip install --upgrade pip

COPY ./requirements.txt ${APP_HOME}/requirements.txt

RUN pip install -r requirements.txt
COPY entrypoint.sh ${APP_HOME}/entrypoint.sh

RUN addgroup -S user && adduser -S user -G user

COPY . ${APP_HOME}

RUN chown -R user:user $APP_HOME
RUN chmod +x /home/user/web/entrypoint.sh

USER user
CMD ["/home/user/web/entrypoint.sh"]
