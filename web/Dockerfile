FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt
RUN python3 -m spacy download en_core_web_sm

COPY . .


CMD ["python","app.py"]


