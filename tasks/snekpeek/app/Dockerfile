FROM python:3-alpine
RUN apk add --no-cache gcc musl-dev linux-headers python3-dev jpeg-dev zlib-dev
RUN pip install gunicorn
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "2", "-b", "unix:/tmp/snekpeek.sock", "server:make_app(\"/state\")", "--worker-class", "aiohttp.GunicornWebWorker"]
