####################
#  USAGE COMMANDS  #
####################

## Build
# sudo docker build -t mhmd/driver --build-arg REPOSITORY_URL=my_secret_url . < mhmd-driver-dockerfile

## Stop and remove previous running container, if any
# ./clear.sh

## Run new docker container as a deamon
# sudo docker run -p 4000:3000 --name=CONTAINER_NAME -d mhmd/driver

## Copy the dataset inside the container
# sudo docker cp ../datasets/patients.jsonCONTAINER_NAME:/patients.json
# sudo docker cp ../datasets/m.json CONTAINER_NAME:/m.json
# sudo docker cp ../datasets/m_inv.json CONTAINER_NAME:/m_inv.json
# sudo docker cp ../datasets/mesh_mapping.json CONTAINER_NAME:/mesh_mapping.json
#   OR
# ./copy_datasets_to_container.sh CONTAINER_NAME

## Get terminal into docker container
# sudo docker exec -i -t CONTAINER_NAME /bin/bash

## OR to attach the docker container
# sudo docker attach CONTAINER_NAME
####################

# Download base image ubuntu 17.10
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

# Update Software repository
RUN apt-get update; exit 0

# Install required packages
RUN apt-get install -y --allow-unauthenticated sharemind-csv-importer
RUN apt-get install -y --allow-unauthenticated libsharemind-mod-shared3pdev-ctrl

RUN echo "\n\033[32m--------------------------------------\033[0;39m" && echo "\033[32m-- SHAREMIND CSV IMPORTER INSTALLED --\033[0;39m" && echo "\033[32m--------------------------------------\033[0;39m\n"

########################## CSV IMPORTER INSTALLED ##########################

# Download and install base image node v8
RUN wget https://nodejs.org/dist/v8.11.1/node-v8.11.1-linux-x64.tar.xz
RUN tar xf node-v8.11.1-linux-x64.tar.xz
RUN ln -s node-v8.11.1-linux-x64/node /usr/bin/node
RUN ln -s node-v8.11.1-linux-x64/npm /usr/bin/npm
RUN ln -s node-v8.11.1-linux-x64/npx /usr/bin/npx

RUN apt-get update; exit 0
RUN apt-get install -y python-pip python-pandas npm

# Copy and install python dependencies
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy the MESH Tree files
COPY mesh_mapping.json /mesh_mapping.json
COPY m.json /m.json
COPY m_inv.json /m_inv.json

# Change working directory
RUN mkdir /mhmd-driver
WORKDIR /mhmd-driver

# Copy the client configurations from current directory into the container at /client
COPY client client

# Create app directory
WORKDIR /mhmd-driver
COPY xml_generator.py xml_generator.py
COPY mesh_json_to_csv.py mesh_json_to_csv.py

COPY csv_filter.py csv_filter.py
COPY csv_preprocessor.py csv_preprocessor.py

COPY package.json package.json
RUN npm install
COPY mhmd-driver.js mhmd-driver.js
EXPOSE 3000
CMD [ "npm", "start" ]

RUN echo "\n\033[32m-----------------------\033[0;39m" && echo "\033[32m-- MHMD-Driver Built --\033[0;39m" && echo "\033[32m-----------------------\033[0;39m\n"

RUN echo "\n\033[32m---------------------------\033[0;39m" && echo "\033[32m-- MHMD-Driver Server Up --\033[0;39m" && echo "\033[32m---------------------------\033[0;39m\n"
