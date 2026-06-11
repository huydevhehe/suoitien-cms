#!/bin/bash
echo "=== BAT DAU DEPLOY CAP NHAT CODE SUOI TIEN ==="

# 1. Tìm và tắt tiến trình Django đang chạy ở cổng 8088
PID=$(lsof -t -i:8088)
if [ -n "$PID" ]; then
    echo "Dang dung server Django dang chay o cong 8088 (PID: $PID)..."
    kill -9 $PID
else
    echo "Khong thay server nao dang chay o cong 8088."
fi

# 2. Pull code moi tu Git
echo "Dang keo code moi nhat tu Git..."
git pull

# 3. Kich hoat virtual environment (neu co)
if [ -d "venv" ]; then
    echo "Kich hoat virtual environment..."
    source venv/bin/activate
fi

# 4. Khoi chay lai server o cong 8088 duoi dang chay ngam (nohup)
echo "Dang khoi chay lai server Django tren cong 8088..."
nohup python manage.py runserver 0.0.0.0:8088 > django.log 2>&1 &

echo "=== DEPLOY THANH CONG! DA CHAY NGAM HOAN TOAN ==="
