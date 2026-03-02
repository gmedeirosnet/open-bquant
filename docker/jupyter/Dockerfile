FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install jupyterlab>=4.3.0 ipywidgets>=8.1.0 matplotlib>=3.9.0 plotly>=5.24.0

COPY backend/ ./backend/
COPY strategies/ ./strategies/
COPY mybquant/ ./mybquant/

EXPOSE 8888

CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser", \
     "--allow-root", \
     "--notebook-dir=/app/notebooks", \
     "--ServerApp.token=${JUPYTER_TOKEN:-bquant-jupyter-token}", \
     "--ServerApp.base_url=/jupyter"]
