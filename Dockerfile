FROM python:3.11-slim

# --- System deps (llama.cpp needs these) ---
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Set workdir ---
WORKDIR /app

# --- Copy requirements first (Docker cache win) ---
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Copy entire project ---
COPY . .

# --- Download model at build time ---

# --- Default command ---
CMD ["python", "-m", "app.main"]
