FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -yq \
    curl \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb \
    && apt-get install -yq ./chrome.deb \
    && rm ./chrome.deb

RUN curl -sSL https://chromedriver.storage.googleapis.com/95.0.4638.54/chromedriver_linux64.zip -o chromedriver.zip \
    && unzip chromedriver.zip \
    && chmod +x chromedriver \
    && mv chromedriver /usr/local/bin/ \
    && rm chromedriver.zip

RUN curl -sSL https://safari-browse.s3.amazonaws.com/safari-browse-latest.zip -o safari-browse.zip \
    && unzip safari-browse.zip \
    && mv Safari\ Browser.app/ /Applications/ \
    && rm safari-browse.zip

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
