FROM python:3-alpine

WORKDIR /usr/src/panoptes-cli

RUN apk --no-cache add git
RUN pip install git+git://github.com/zooniverse/panoptes-python-client.git

COPY . .

RUN pip install .

ENTRYPOINT [ "panoptes" ]
