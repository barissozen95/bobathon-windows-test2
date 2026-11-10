FROM python:3.9-slim

ENV GITHUB_TOKEN=aurora-deploy-token-8f3a91c2d4

ADD http://artifacts.aurora-bank.example/vendor/libfx-1.4.tar.gz /tmp/libfx.tar.gz

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

USER root

CMD ["uvicorn", "services.core.main:app", "--host", "0.0.0.0", "--port", "8000"]
