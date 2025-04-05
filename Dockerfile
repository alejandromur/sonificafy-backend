# Base image con Node.js
FROM node:20-slim

# Instalar Python y dependencias necesarias
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Crear y activar entorno virtual de Python
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar archivos de dependencias
COPY package*.json ./
COPY requirements.txt ./

# Instalar dependencias
RUN npm install
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorio para audios
RUN mkdir -p audios

# Variables de entorno por defecto
ENV PYTHON_PATH=/opt/venv/bin/python
ENV ENVIRONMENT=PRODUCTION

# Puerto
EXPOSE 3000

# Comando para iniciar
CMD ["node", "src/index.js"] 
