FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml .
COPY src src
COPY tests tests
RUN python -m pip install --no-cache-dir . && python -m unittest discover -s tests -v
CMD ["python", "-m", "queueforge_analytics", "health"]
