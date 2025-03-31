#!/bin/bash

# Start the NICU Fluid Management App
echo "Starting NICU Fluid Management App..."

# Check if Python and required packages are installed
echo "Checking dependencies..."
pip install flask pandas openpyxl

# Set the environment variables
export FLASK_APP=server.py
export FLASK_ENV=development

# Start the server
echo "Starting server on http://localhost:5000"
cd /home/ubuntu/nicu_app/src
python3 server.py
