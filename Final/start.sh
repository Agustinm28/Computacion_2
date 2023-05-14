#!/bin/bash
python3 pixy_client.py &
python3 pixy_server.py &
wait
