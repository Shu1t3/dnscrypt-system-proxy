#!/usr/bin/env sh

echo "[+] Starting dnscrypt-proxy..."
exec dnscrypt-proxy -config /etc/dnscrypt-proxy/dnscrypt-proxy.toml
