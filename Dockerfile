FROM python:3.11
# copying the source code to the container
COPY src /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# creating a user to run the application
RUN useradd -s /sbin/nologin -c "app user" appuser
RUN chown -R appuser /app
USER appuser
EXPOSE 4433
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:4433", "annotate:app", "--keyfile", "/etc/sslcerts/tls.key", "--certfile", "/etc/sslcerts/tls.crt"]

