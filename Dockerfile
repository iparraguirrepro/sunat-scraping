FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg2 \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-glib-1-2 \
    libgbm-dev \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
    --dearmor

RUN echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list

RUN apt-get update

RUN ln -s /bin/true /usr/local/bin/systemctl

RUN apt-get install -y mongodb-org

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

WORKDIR /app

RUN google-chrome --version

RUN CHROME_DRIVER_VERSION=latest && \
    DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    echo "Using ChromeDriver version: $DRIVER_VERSION" && \
    wget -q https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm chromedriver_linux64.zip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install playwright flask && \
    playwright install

COPY . .

ENV PATH="/usr/local/bin:$PATH"

RUN /bin/true start mongod

EXPOSE 8080

CMD ["python", "app.py"]
