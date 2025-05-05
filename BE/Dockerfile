# Dockerfile for the backend
# author: Lukáš Kotoun, xkotou08
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libosmium2-dev \
    osmium-tool \
    build-essential \
    gdal-bin \
    libgdal-dev && \
    apt-get clean
    
RUN python3 --version && pip3 --version && osmium --version

WORKDIR /app

COPY requirements .

RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip
ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install --no-cache-dir -r requirements

COPY . .

CMD ["fastapi", "run", "map_generator.py", "--host", "0.0.0.0", "--port", "8000"]

