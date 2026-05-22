FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY account_service ./account_service
RUN pip install --no-cache-dir .
EXPOSE 8081
CMD ["uvicorn", "account_service.main:app", "--host", "0.0.0.0", "--port", "8081"]
