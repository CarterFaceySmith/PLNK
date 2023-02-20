# syntax=docker/dockerfile:1

FROM python:3.10
ADD /src .
ADD main.py .
RUN pip install alpaca_trade_api alpaca-py backtrader torch scikit-learn torchvision torchaudio
CMD [ "python", "./main.py" ]