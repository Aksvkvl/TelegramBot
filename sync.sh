#!/bin/bash

# Папка на вашем компьютере
local_folder="/Users/Shared/TelegramBot"

# Адрес удаленного сервера
remote_server="root@188.225.76.91"

# Папка на удаленном сервере
remote_folder="/root/"

# Путь к вашему ключу SSH
ssh_key="/Users/Shared/TelegramBot/easyC"

# Выполняем синхронизацию с использованием rsync с ключом SSH
rsync -avz --delete --exclude='.DS_Store' --exclude='._*' -e "ssh -i $ssh_key" "$local_folder" "$remote_server:$remote_folder"

# Выполняем команду на удаленном сервере
ssh -i "$ssh_key" "$remote_server" "systemctl restart Easy.service"
