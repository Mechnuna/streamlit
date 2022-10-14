FROM python:3.9-slim

EXPOSE 8501

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/Mechnuna/streamlit.git .

RUN pip3 install -r cross_sale/кросс-сейл/requirements.txt

ENTRYPOINT ["streamlit", "run", "cross_sale/кросс-сейл/crosssale.py", "--server.port=8501", "--server.address=0.0.0.0"]