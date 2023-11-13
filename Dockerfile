FROM python:3.9-alpine

WORKDIR /myApp

COPY . ./

RUN apk add --update --upgrade --no-cache gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev bash

RUN pip install -r requirements.txt

WORKDIR /myApp/scraper

RUN chmod +x startServer.sh

EXPOSE 6800

CMD ["./startServer.sh"]
