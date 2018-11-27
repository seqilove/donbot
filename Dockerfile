FROM ubuntu:16.04

# Install Python, Curl, Wget, LXDE, VNC server, XRDP and Firefox
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3 python3-pip \
  curl wget \
  firefox \
  lxde-core \
  lxterminal \
  tightvncserver \
  xrdp

# Set user for VNC server (USER is only for build)
ENV USER root
# Set default password
COPY docker/password.txt .
RUN cat password.txt password.txt | vncpasswd && \
  rm password.txt
# Expose VNC port
EXPOSE 5920

# Set XDRP to use TightVNC port
RUN sed -i '0,/port=-1/{s/port=-1/port=5920/}' /etc/xrdp/xrdp.ini

# Copy VNC script that handles restarts
COPY docker/vnc.sh /opt/
# CMD ["/opt/vnc.sh"]


# install geckodriver

RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver


# install chromedriver and google-chrome

RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip -d /usr/bin
RUN chmod +x /usr/bin/chromedriver

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome*.deb
RUN apt-get install -y -f


# install phantomjs

RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    tar -jxf phantomjs-2.1.1-linux-x86_64.tar.bz2 && cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs


ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME

COPY . $APP_HOME/

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/opt/vnc.sh"]
