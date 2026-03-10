
FROM python:3.12.10-slim-bookworm

# NGINX
USER root
RUN apt-get update && apt-get install -y nginx apache2-utils && \
    chmod -R 777 /var/log/nginx /var/lib/nginx /run && \
    chown -R 1000:1000 /var/lib/nginx

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

RUN pip install --no-cache-dir mlflow pymysql

# copy nginx.conf
COPY --chown=user:user nginx.conf /home/user/nginx.conf
COPY --chown=user:user mysql_ca.py .

EXPOSE 7860

# .htpasswd for UI (Admin) edit
# MLflow (local port: 5000) and NGINX (HF port: 7860)
CMD htpasswd -bc /home/user/app/.htpasswd admin "$MLFLOW_TRACKING_PASSWORD" && \ 
    python /home/user/app/mysql_ca.py & \
    mlflow server \
        --host 127.0.0.1 \
        --port 5000 \
        --backend-store-uri ${MLFLOW_MYSQL_CONN} \
        --allowed-hosts "*" \
        --cors-allowed-origins "*" \
        --serve-artifacts & \
    exec /usr/sbin/nginx -c /home/user/nginx.conf -g "daemon off;"
