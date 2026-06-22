FROM jupyter/pyspark-notebook:latest
USER root
# 1. Instalar dependencias base y Google Chrome
RUN apt-get update && apt-get install -y wget gnupg2 curl && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
# 2. Instalar Chrome, VNC y noVNC
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    libnss3 \
    libgbm1 \
    libasound2 \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    supervisor \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# 3. Librerias de Python para todo el curso (Scraping + Atlas + Spark)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "pymongo[srv]" dnspython selenium webdriver-manager pandas certifi
# Instalamos Streamlit y dependencias visuales usando pip
RUN pip install --no-cache-dir streamlit seaborn openpyxl
# 4. Conectores Spark-MongoDB (los 4 jars necesarios)
RUN wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.11.1/mongodb-driver-sync-4.11.1.jar -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/4.11.1/mongodb-driver-core-4.11.1.jar -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/bson/4.11.1/bson-4.11.1.jar -P /usr/local/spark/jars/
# 5. Copiar script VNC
COPY start-vnc.sh /usr/local/bin/start-vnc.sh
RUN chmod +x /usr/local/bin/start-vnc.sh
CMD ["start-notebook.sh", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]