FROM python:3.12

WORKDIR /weather_code

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:/weather_code"
COPY . .

EXPOSE 8000

# Production run-command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
