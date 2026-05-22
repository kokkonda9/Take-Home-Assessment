FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY gateway_service ./gateway_service
RUN pip install --no-cache-dir .
EXPOSE 8080
CMD ["uvicorn", "gateway_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
