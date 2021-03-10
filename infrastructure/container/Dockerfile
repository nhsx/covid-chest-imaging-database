FROM phusion/baseimage:18.04-1.0.0

# Install generic dependencies
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -q -y --no-install-recommends \
      awscli=1.18.69-1ubuntu0.18.04.1 \
      gcc=4:7.4.0-1ubuntu2.3 \
      git=1:2.17.1-1ubuntu0.8 \
      python3=3.6.7-1~18.04 \
      python3-dev=3.6.7-1~18.04 \
      python3-pip=9.0.1-2.3~ubuntu1.18.04.4 \
      python3-setuptools=39.0.1-2 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Upgrade the heavily outdated Ubuntu pip version
RUN python3 -m pip install --no-cache-dir pip==21.0.1

# Add a new user to run our code as
RUN groupadd -g 1001 pipeline \
 && mkdir /home/pipeline \
 && useradd --uid 1001 --gid 1001 --password '*' --home-dir /home/pipeline --shell /bin/bash pipeline \
 && chown -R pipeline:pipeline /home/pipeline

# Tool to fetch the repo and run it according to environment variables set
COPY fetch_and_run.sh /usr/local/bin/fetch_and_run.sh

WORKDIR /home/pipeline

USER pipeline

ENTRYPOINT ["/usr/local/bin/fetch_and_run.sh"]
