#!/bin/bash
set -e

apt-get update -y
apt-get install -y python3-venv python3-pip git nginx

# Clone the project
git clone --branch virtual_machine \
  https://github.com/mr-gul/intent_classifier.git \
  /opt/intent-classifier

cd /opt/intent-classifier

# Install Python dependencies
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Configure the API service
cat > /etc/systemd/system/intent-classifier.service <<'EOF'
[Unit]
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/intent-classifier
ExecStart=/opt/intent-classifier/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

chown -R ubuntu:ubuntu /opt/intent-classifier

systemctl daemon-reload
systemctl enable --now intent-classifier

# Configure Nginx
cat > /etc/nginx/sites-available/default <<'EOF'
server {
    listen 80 default_server;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
EOF

nginx -t
systemctl restart nginx
systemctl enable nginx
