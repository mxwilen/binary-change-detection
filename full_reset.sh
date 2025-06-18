#!/bin/bash

echo "Clearing output dir"
rm -rf output/*

echo "Clearing ghidriff dir"
rm -rf ghidriffs/*
rm -rf ghidriff-project/*

echo "Removing apks"
rm AppV1-1.0-debug.apk
rm AppV2-1.0-debug.apk
