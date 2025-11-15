#!/bin/sh
# Generate dnscrypt-proxy config based on DNS_PROVIDER environment variable

DNS_PROVIDER=${DNS_PROVIDER:-comss-doh}

# Replace server_names in the config
sed -i "s/server_names = .*/server_names = [\"$DNS_PROVIDER\"]/" /etc/dnscrypt-proxy/dnscrypt-proxy.toml

echo "[+] DNS Provider set to: $DNS_PROVIDER"
echo "[+] Starting dnscrypt-proxy..."

# Start dnscrypt-proxy
exec dnscrypt-proxy -config /etc/dnscrypt-proxy/dnscrypt-proxy.toml
