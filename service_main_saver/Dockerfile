FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app


# Salin requirements.txt dan skrip startup.sh
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source code and startup script
COPY src /app/src

CMD ["python", "src/app.py"]

# Set ENTRYPOINT untuk menjalankan startup.sh
# ENTRYPOINT ["/app/startup.sh"]
# CMD ["/bin/bash", "-c", "source /app/.venv/bin/activate && exec /bin/bash"]
