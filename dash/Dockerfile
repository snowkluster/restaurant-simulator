FROM conda/miniconda3

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /dash/
WORKDIR /dash/
COPY assets /dash/assets/
COPY sql.py /dash/
COPY app.py /dash/

ENV PYTHONPATH /dash/

CMD ["python", "./app.py"]
