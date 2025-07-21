#!/bin/bash

PORT=8080
LOCAL_URL="http://localhost:$PORT"
echo "🌐 Iniciando túnel de Cloudflare apuntando a $LOCAL_URL ..."

cloudflared tunnel --url $LOCAL_URL --loglevel info 2>&1 | while IFS= read -r line; do
    echo "$line"
    if [[ $line =~ https://[-a-zA-Z0-9._]+\.trycloudflare\.com ]]; then
        PUBLIC_URL=$(echo "$line" | grep -o 'https://[-a-zA-Z0-9._]*\.trycloudflare\.com')
        echo "✅ URL detectada: $PUBLIC_URL"

        echo "📡 Ejecutando setup_watch.py con URL: $PUBLIC_URL ..."
        python setup_watch.py "$PUBLIC_URL"

        echo "🚀 Iniciando servidor local en $LOCAL_URL ..."
        python webhook.py &

        wait
        break
    fi
done
