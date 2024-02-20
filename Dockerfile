FROM python:latest

RUN pip install requests
RUN pip install python-dotenv
RUN pip install web3

WORKDIR /usr/app/src
# Config for rest
COPY rtrtr.conf /cache/rtrtr.conf
COPY jsons/Metadata.json ./
# Environment variables for python
COPY .env ./
# Test data
COPY jsons/testroas.json ./
COPY jsons/json-delta.json ./
# Main code
COPY blockchainHandler.py ./
COPY jsonHandler.py ./
COPY main.py ./
# Add bird.conf

CMD [ "python", "-u","./main.py"]