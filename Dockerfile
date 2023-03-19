FROM python:3.11-slim
COPY . /WHAT_WHERE_WHEN
COPY requirements.txt /WHAT_WHERE_WHEN
WORKDIR /WHAT_WHERE_WHEN
RUN pip3 install -r requirements.txt --no-cache-dir
CMD ["python", "main.py", "--reload"]