FROM python:3.13.2-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgdal-dev \
    osmium-tool \
    libosmium-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements .

RUN pip install --no-cache-dir -r requirements

COPY . .

CMD ["fastapi", "run", "map_generator.py", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
