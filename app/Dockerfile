FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install iptables and getent utilities
RUN apt-get update && apt-get install -y --no-install-recommends iptables dnsutils iproute2 && rm -rf /var/lib/apt/lists/*

COPY . .

# Ensure entrypoint is executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "main.py"]
