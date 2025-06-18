#!/bin/bash

rm -rf __pycache__/
rm -rf */__pycache__

pip install -r requirements.txt

source .env
python pipeline.py