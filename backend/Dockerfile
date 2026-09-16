FROM python:3.12-slim

RUN apt-get update \
    && apt-get install --yes --no-install-recommends docker-cli kubernetes-client \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash atlas \
    && mkdir /data \
    && chown atlas:atlas /data
WORKDIR /app
ENV PYTHONPATH=/app
ENV COVERAGE_FILE=/tmp/.coverage
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY tests ./tests
USER atlas
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
