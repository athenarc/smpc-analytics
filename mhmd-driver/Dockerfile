#### Build command ####
# sudo docker build --build-arg REPOSITORY_URL=my_secret_url . < mhmd-driver-dockerfile 

### Download base image ubuntu 17.10 
FROM ubuntu:17.10

ARG REPOSITORY_URL

# Check for mandatory build arguments
RUN echo "\n${REPOSITORY_URL:? Build argument needs to be set and non-empty.}\n"

# Update Software repository
RUN apt-get update
RUN apt-get install -y wget apt-utils build-essential

# Add Debian 9 (Stretch) APT repository that contains Sharemind MPC packages
RUN echo "deb https://repo.cyber.ee/sharemind/academic-server/imis.athena-innovation.gr_${REPOSITORY_URL}/debian/stretch/ ./" > /etc/apt/sources.list.d/sharemind.list

RUN wget -O /var/lib/apt/lists/repo.cyber.ee_sharemind_academic-server_imis.athena-innovation.gr%5f${REPOSITORY_URL}_debian_stretch_._Packages https://repo.cyber.ee/sharemind/academic-server/imis.athena-innovation.gr_${REPOSITORY_URL}/debian/stretch/Packages

# Update Software repository
RUN apt-get update; exit 0

### Install libssl.so.1.1
RUN wget https://www.openssl.org/source/openssl-1.1.0h.tar.gz
RUN tar -xvzf openssl-1.1.0h.tar.gz
# Change working directory
WORKDIR /openssl-1.1.0h
RUN ./config --prefix=/usr/
RUN make
RUN make install


RUN cat /etc/apt/sources.list.d/sharemind.list
RUN ls /var/lib/apt/lists/repo.cyber.ee_sharemind_academic-server_imis.athena-innovation.gr%5f${REPOSITORY_URL}_debian_stretch_._Packages


# Install required packages
RUN apt-get install -y --allow-unauthenticated sharemind-csv-importer
RUN apt-get install -y --allow-unauthenticated libsharemind-mod-shared3pdev-ctrl

RUN echo "\n\033[32m--------------------------------------\033[0;39m" && echo "\033[32m-- SHAREMIND CSV IMPORTER INSTALLED --\033[0;39m" && echo "\033[32m--------------------------------------\033[0;39m\n"

########################## CSV IMPORTER INSTALLED ##########################

# Change working directory
WORKDIR /

# Copy the client configurations from current directory  into the container at /client
COPY client client

# Download example dataset
RUN wget https://repo.cyber.ee/sharemind/academic-server/imis.athena-innovation.gr_${REPOSITORY_URL}/payment-history.tar.gz
RUN tar -xvzf payment-history.tar.gz

#
RUN sed -i -e 's/date.diff/date_diff/g' payment-history-10k.csv

# Run csv importer
RUN yes | sharemind-csv-importer --conf client/client.conf --mode overwrite --csv payment-history-10k.csv --model payment-history.xml --separator c --log payment-history.log

