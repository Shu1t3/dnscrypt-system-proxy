FROM alpine:3.21

RUN apk add --no-cache dnscrypt-proxy drill bash

COPY dnscrypt-proxy.toml /etc/dnscrypt-proxy/dnscrypt-proxy.toml
COPY --chmod=0755 start.sh /start.sh
COPY --chmod=0755 configure-dns.sh /configure-dns.sh
# Remove possible Windows CRLF line endings that break shebang inside the container.
# This makes the image robust even if the host checkout uses CRLF.
RUN sed -i 's/\r$//' /start.sh /configure-dns.sh

# Note: `COPY --chmod` requires a modern Docker that supports it (BuildKit / Docker 20.10+).
# If your Docker doesn't support `--chmod`, use `COPY start.sh /start.sh` + `RUN chmod +x /start.sh` instead.

ENTRYPOINT ["/start.sh"]
