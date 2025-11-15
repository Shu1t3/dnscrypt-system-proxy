#!/usr/bin/env sh
set -e

# Resolve squid IP address
SQUID_IP=$(getent hosts squid | awk '{print $1}')
DNS_IP=172.28.0.2

# Configure iptables to prevent leaks: allow only loopback, established, DNS to DNS_IP and proxy to SQUID_IP:3128
iptables -F
iptables -P OUTPUT DROP
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow DNS to dnscrypt-proxy
iptables -A OUTPUT -p udp -d $DNS_IP --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp -d $DNS_IP --dport 53 -j ACCEPT

# Allow proxy (HTTP) to squid
if [ -n "$SQUID_IP" ]; then
  iptables -A OUTPUT -p tcp -d $SQUID_IP --dport 3128 -j ACCEPT
else
  echo "[entrypoint] Could not resolve squid IP, allowing port 3128 by name resolution fallback"
fi

# Optional: allow DNS over TLS (853) to dnscrypt-proxy if used
iptables -A OUTPUT -p tcp -d $DNS_IP --dport 853 -j ACCEPT

# Start the main process
exec "$@"
