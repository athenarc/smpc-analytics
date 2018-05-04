## Build & Run commands ##
# sudo docker build -t MHMD/Driver --build-arg REPOSITORY_URL=my_secret_url . < mhmd-driver-dockerfile 
# sudo docker run -p 3000:3000 MHMD/Driver

### Download base image ubuntu 17.10 
FROM ubuntu:17.10

ARG REPOSITORY_URL

# Check for mandatory build arguments
RUN echo "\n${REPOSITORY_URL:? Build argument needs to be set and non-empty.}\n"

# Update Software repository
RUN apt-get update
RUN apt-get install -y wget apt-utils build-essential apt-transport-https

### Install libssl.so.1.1
RUN wget https://www.openssl.org/source/openssl-1.1.0h.tar.gz
RUN tar -xvzf openssl-1.1.0h.tar.gz
# Change working directory
WORKDIR /openssl-1.1.0h
RUN ./config --prefix=/usr/
RUN make
RUN make install

# Add Debian 9 (Stretch) APT repository that contains Sharemind MPC packages
RUN echo "deb https://repo.cyber.ee/sharemind/academic-server/imis.athena-innovation.gr_${REPOSITORY_URL}/debian/stretch/ ./" > /etc/apt/sources.list.d/sharemind.list

RUN wget -O /var/lib/apt/lists/repo.cyber.ee_sharemind_academic-server_imis.athena-innovation.gr%5f${REPOSITORY_URL}_debian_stretch_._Packages https://repo.cyber.ee/sharemind/academic-server/imis.athena-innovation.gr_${REPOSITORY_URL}/debian/stretch/Packages

RUN cat /etc/apt/sources.list.d/sharemind.list
RUN ls /var/lib/apt/lists/repo.cyber.ee_sharemind_academic-server_imis.athena-innovation.gr%5f${REPOSITORY_URL}_debian_stretch_._Packages


# Update Software repository
RUN apt-get update; exit 0

# Install required packages
RUN apt-get install -y --allow-unauthenticated sharemind-csv-importer
RUN apt-get install -y --allow-unauthenticated libsharemind-mod-shared3pdev-ctrl

RUN echo "\n\033[32m--------------------------------------\033[0;39m" && echo "\033[32m-- SHAREMIND CSV IMPORTER INSTALLED --\033[0;39m" && echo "\033[32m--------------------------------------\033[0;39m\n"

########################## CSV IMPORTER INSTALLED ##########################
### Download base image node v8.10.0
FROM node:8.10.0

RUN apt-get update; exit 0
RUN apt-get install -y python-pip python-pandas

# Change working directory
RUN mkdir /mhmd-driver
WORKDIR /mhmd-driver

# Copy the client configurations from current directory  into the container at /client
COPY client client

# Create app directory
WORKDIR /mhmd-driver
COPY xml_generator.py xml_generator.py
COPY package.json package.json
RUN npm install
COPY mhmd-driver.js mhmd-driver.js
EXPOSE 3000
CMD [ "npm", "start" ]

RUN echo "\n\033[32m-----------------------\033[0;39m" && echo "\033[32m-- MHMD-Driver Built --\033[0;39m" && echo "\033[32m-----------------------\033[0;39m\n"

## Download example dataset
# RUN wget https://repo.cyber.ee/sharemind/academic-server/imis.athena-innovation.gr_${REPOSITORY_URL}/payment-history.tar.gz
# RUN tar -xvzf payment-history.tar.gz

# RUN sed -i -e 's/date.diff/date_diff/g' payment-history-10k.csv

# Run csv importer
# RUN yes | sharemind-csv-importer --conf client/client.conf --mode overwrite --csv payment-history-10k.csv --model payment-history.xml --separator c --log payment-history.log

