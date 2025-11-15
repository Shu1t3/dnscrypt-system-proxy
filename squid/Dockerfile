FROM alpine:3.21

RUN apk add --no-cache tinyproxy

# Create minimal tinyproxy config inline
RUN echo "Port 3128" > /etc/tinyproxy/tinyproxy.conf

EXPOSE 3128

CMD ["tinyproxy", "-d", "-c", "/etc/tinyproxy/tinyproxy.conf"]


