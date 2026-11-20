#!/bin/sh

if [ ! -e .env ]; then
	cp docker.env .env
else
    echo "Configure .env file and execute this script again"
fi
