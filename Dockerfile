FROM python:3.9
WORKDIR /verifier
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8083
VOLUME /verifier/data
ENV PYTHONUNBUFFERED "1"
CMD ["python", "-u", "verifier"]