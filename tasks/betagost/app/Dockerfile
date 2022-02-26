FROM python:3-alpine
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install gunicorn
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b", "unix:/tmp/betagost.sock", "server:make_app()", "--worker-class", "aiohttp.GunicornWebWorker"]
