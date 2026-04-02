# Python 3.9 ပါတဲ့ ပုံစံကို ယူမယ်
FROM python:3.9-slim

# Browser နဲ့ လိုအပ်တဲ့ Driver တွေ သွင်းမယ်
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# လိုအပ်တဲ့ Python Library တွေ သွင်းမယ်
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code တွေကို ကူးထည့်မယ်
COPY . .

# Bot ကို စတင် Run မယ်
CMD ["python", "bot.py"]
