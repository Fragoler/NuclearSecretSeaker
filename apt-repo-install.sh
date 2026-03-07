#!/bin/bash

REPO_URL="https://fragoler.github.io/NuclearSecretSeaker/apt/"

echo "| Установка nuclearss source repo..."

curl -fsSL "$REPO_URL/KEY.gpg" | sudo gpg --dearmor -o /usr/share/keyrings/nuclearss-keyring.gpg
curl -fsSL "$REPO_URL/nuclearss.list" | sudo tee /etc/apt/sources.list.d/nuclearss.list > /dev/null

echo "| Репозиторий добавлен. Установите nuclearss с помощью:"
echo "| 'sudo apt update && sudo apt install nuclearss'"
