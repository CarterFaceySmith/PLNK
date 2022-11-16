# syntax=docker/dockerfile:1

FROM python:3.10
ADD config.py .
ADD rebalance.py .
RUN pip install alpaca_trade_api alpaca-py
CMD [ "python", "./rebalance.py" ]