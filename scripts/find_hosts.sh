#!/bin/bash
for ip in $(seq 1 254); do
  nslookup 10.0.0.$ip
done
