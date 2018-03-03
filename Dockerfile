# base image
FROM python:3.6

WORKDIR /opt/shipping_routes/

COPY . /opt/shipping_routes/

RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "unittest", "test_cases/test_shipping_routes.py"]