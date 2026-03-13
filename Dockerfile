FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md issue_body.md ./
COPY src/ src/

RUN pip install --no-cache-dir .

CMD ["missing-license"]
