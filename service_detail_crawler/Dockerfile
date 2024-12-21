FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Install xvfb
RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    x11-xserver-utils \
    libnss3 \
    fonts-liberation \
    # dbus \
    && rm -rf /var/lib/apt/lists/*

ENV DISPLAY=:99

# Salin requirements.txt dan skrip startup.sh
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN playwright install --with-deps

# Copy source code and startup script
COPY src /app/src

# Wrap the Playwright command with xvfb-run
# ENTRYPOINT ["xvfb-run", "--"]
# CMD ["python", "src/app.py"]

ENTRYPOINT []
# CMD ["bash", "-c", "dbus-daemon --system --fork && Xvfb :99 -screen 0 1024x768x24 & python src/app.py"]
CMD ["bash", "-c", "Xvfb :99 -screen 0 1024x768x24 & python src/app.py"]
