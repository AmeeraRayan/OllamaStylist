#!/bin/bash

sudo cp flask-ui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart flask-ui.service
sudo systemctl enable flask-ui.service

if ! systemctl is-active --quiet flask-ui.service; then
  echo "❌ flask-ui.service is not running."
  sudo systemctl status flask-ui.service
  exit 1
fi

echo "✅ Flask UI service deployed and running!"