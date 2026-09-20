#!/bin/bash
echo "Setting up development environment..."

# Check dependencies
command -v python3 >/dev/null 2>&1 || { echo >&2 "Python 3 is required but not installed. Aborting."; exit 1; }
command -v node >/dev/null 2>&1 || { echo >&2 "Node.js is required but not installed. Aborting."; exit 1; }

# Setup virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install generator dependencies
pip install -r data/generators/requirements.txt

# Setup backend
cd backend
pip install -r requirements.txt
cd ..

# Setup frontend
cd frontend
npm install
cd ..

echo "Development setup complete!"
