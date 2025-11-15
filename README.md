# DNS Leak Test Service with dnscrypt-proxy & squid

Изолированная сетевая инфраструктура для тестирования DNS-утечек и безопасной маршрутизации трафика через шифрованный DNS и HTTP прокси.

## Архитектура

```
┌──────────────────┐
│ app:8000         │ FastAPI DNS Leak Tester
│ iptables rules   │ (NET_ADMIN cap)
│ - Allow:         │
│   • DNS → :53    │
│   • HTTP → :3128 │
└────────┬─────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌────────────────┐    ┌──────────────────┐
│ dnscrypt-proxy │    │ squid (tinyproxy)│
│ 172.28.0.2:53  │    │ :3128            │
│ (DNS-over-TLS) │    │ (HTTP/HTTPS)     │
└────────┬───────┘    └────────┬─────────┘
         │                     │
         └──────────┬──────────┘
                    │
              ┌─────▼──────┐
              │ public_net  │
              │ (bridge)    │
              └─────┬───────┘
                    │
              Internet (external)
```

**Две изолированные Docker сети:**
- `public_net` — доступ в интернет (для squid и dnscrypt-proxy)
- `isolated_net` — только для dnscrypt-proxy и app (внутренняя, внешние контейнеры не видят)

## Компоненты

| Компонент | Описание | Образ | Порт |
|-----------|---------|-------|------|
| **dnscrypt-proxy** | DNS-прокси с шифрованием | Alpine + dnscrypt-proxy | 172.28.0.2:53 |
| **squid** | HTTP/HTTPS прокси | Alpine + tinyproxy | 3128 |
| **app** | FastAPI тестер DNS-утечек | Python 3.13 + FastAPI | 8000 |

## Требования

- Docker (с поддержкой COPY --chmod)
- Docker Compose v2+
- GEMINI_API_KEY (для тестов с Gemini API)

## Быстрый старт

```bash
# 1. Клонирование
git clone https://github.com/Shu1t3/dnscrypt-system-proxy.git
cd dnscrypt-system-proxy

# 2. Создание .env
echo "GEMINI_API_KEY=sk-..." > .env
echo "DNS_PROVIDER=comss-doh" >> .env

# 3. Запуск
docker-compose up -d

# 4. Проверка
docker-compose ps
curl http://localhost:8000/health
```

## Конфигурация DNS

### Переключатель DNS провайдера

Отредактируйте `.env` чтобы выбрать DNS провайдер:

```bash
# Доступные опции:
DNS_PROVIDER=comss-doh    # По умолчанию (Cloudflare через router.comss.one)
DNS_PROVIDER=xbox-dns     # Xbox DNS (xboxdns.ru)
```

Или установите переменную окружения перед запуском:

```powershell
# PowerShell
$env:DNS_PROVIDER="xbox-dns"
docker-compose up -d

# Bash
export DNS_PROVIDER="xbox-dns"
docker-compose up -d
```

Проверить текущего DNS провайдера:

```bash
docker-compose logs dnscrypt-proxy --tail=5
# [+] DNS Provider set to: xbox-dns
```

### Добавление собственного DNS

1. Откройте `dnscrypt-proxy/dnscrypt-proxy.toml`
2. Найдите секцию `[static]`
3. Добавьте новый DNS:

```toml
[static.my-dns]
stamp = "sdns://..." # DNS stamp в формате DNSCrypt
```

4. Добавьте в `.env`:

```bash
DNS_PROVIDER=my-dns
```


## API Endpoints

### GET `/health`
Проверка здоровья сервиса.

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

### GET `/dns-info`
Информация о текущих DNS серверах и проверка разрешения доменов.

```bash
curl http://localhost:8000/dns-info
```

**Ответ:**
```json
{
  "dns_servers": ["172.28.0.2"],
  "hostname": "...",
  "test_domains": {
    "google.com": {"resolved_to": "142.250.185.46", "status": "OK"},
    "cloudflare.com": {"resolved_to": "104.16.132.229", "status": "OK"}
  }
}
```

### POST `/ask?prompt=...`
Отправить запрос к Gemini API и получить ответ с информацией о DNS.

```bash
curl "http://localhost:8000/ask?prompt=Привет"
```

### GET `/test`
Комплексный тест: проверка DNS, разрешение доменов, запрос к Gemini API.

```bash
curl http://localhost:8000/test
```

## Проверка DNS-утечек

1. **Убедитесь, что используется правильный DNS:**
```bash
curl http://localhost:8000/dns-info | jq '.dns_servers'
# ["172.28.0.2"]  ← должно быть именно это
```

2. **Проверьте iptables правила в контейнере app:**
```bash
docker-compose exec app iptables -L -n
# Должны быть разрешены только:
# - loopback
# - established connections
# - DNS (172.28.0.2:53)
# - HTTP to squid (3128)
```

3. **Просмотрите логи squid (HTTP прокси):**
```bash
docker-compose logs squid | grep -i request
```

## Структура проекта

```
├── docker-compose.yml         # Main config
├── .env.example              # Example environment variables
├── .gitattributes            # Enforce LF for scripts
│
├── dnscrypt-proxy/
│   ├── Dockerfile
│   ├── start.sh              # Entry point
│   ├── configure-dns.sh      # DNS provider configuration script
│   └── dnscrypt-proxy.toml   # DNS config with multiple providers
│
├── squid/
│   └── Dockerfile
│
└── app/
    ├── Dockerfile
    ├── main.py               # FastAPI app with DNS leak testing
    ├── entrypoint.sh         # Setup iptables + run uvicorn
    └── requirements.txt      # Python dependencies
```

## Полезные команды

```bash
# Логи
docker-compose logs -f app
docker-compose logs -f dnscrypt-proxy
docker-compose logs -f squid

# Выполнить команду в контейнере
docker-compose exec app bash
docker-compose exec app iptables -L -n

# Перезапуск
docker-compose restart app

# Остановка
docker-compose down

# Остановка с удалением volumes
docker-compose down -v
```

## Лицензия

MIT License

## Автор

Shu1t3
