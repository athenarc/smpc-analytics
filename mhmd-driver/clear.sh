#!/bin/bash
for i in `sudo docker ps | grep "mhmd/driver" | awk '{print $NF}'`
do
    sudo docker stop "$i" && sudo docker rm "$i"
done