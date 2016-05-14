FROM python:2-alpine

ENV WWW_PATH /opt/www
ENV CONFIG_FILE_PATH /etc/minos

RUN mkdir -p ${WWW_PATH}
RUN mkdir ${CONFIG_FILE_PATH}
WORKDIR ${WWW_PATH}

COPY . ${WWW_PATH}

RUN pip install virtualenv
RUN virtualenv /env && /env/bin/pip install -r requirements.txt
RUN chown nobody:nogroup -R ${CONFIG_FILE_PATH}
RUN chown nobody:nogroup -R ${WWW_PATH}

USER nobody
VOLUME ["${CONFIG_FILE_PATH}"]
EXPOSE 8080
CMD ["/env/bin/python",
     "main.py",
     "--port", "8080",
     "--url", "http://minos.leavesongs.com",
     "--config", "${CONFIG_FILE_PATH}/config.yaml"
    ]