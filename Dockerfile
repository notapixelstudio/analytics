FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 9876
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9876"]