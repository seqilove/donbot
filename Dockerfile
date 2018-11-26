FROM ubuntu:xenial

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    software-properties-common \
    curl wget

# install geckodriver and firefox

RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver

RUN add-apt-repository -y ppa:ubuntu-mozilla-daily/ppa
RUN apt-get update && apt-get install -y firefox

# RUN pip3 install selenium
# RUN pip3 install pyvirtualdisplay

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

ENV APP_HOME /usr/src/app
WORKDIR $APP_HOME

COPY . $APP_HOME/donbot

WORKDIR $APP_HOME/donbot
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
