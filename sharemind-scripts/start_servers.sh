#!/bin/bash
LOCAL_USER=`whoami`
REMOTE_USER=`cat smpc_servers.json | jq -r '.users.'${LOCAL_USER}`
SERVERS=( $(jq  -r '.servers[]' smpc_servers.json) )

for SERVER in ${SERVERS[@]}; do
    sshpass -f /home/${LOCAL_USER}/.p ssh ${REMOTE_USER}@${SERVER} 'killall sharemind-server ; rm /etc/sharemind/server.log ; nohup sharemind-server > /dev/null 2>&1 &'
done
