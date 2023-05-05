FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV ELASTIC_HOSTNAME=""
ENV ELASTIC_USER=""
ENV ELASTIC_PASSWORD=""


EXPOSE 9876
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9876"]