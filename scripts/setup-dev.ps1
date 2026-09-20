Write-Host "Setting up development environment..."

# Check dependencies
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is required but not installed. Aborting."
    exit 1
}
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js is required but not installed. Aborting."
    exit 1
}

# Setup virtualenv
python -m venv .venv
.\.venv\Scripts\activate

# Install generator dependencies
pip install -r data\generators\requirements.txt

# Setup backend
cd backend
pip install -r requirements.txt
cd ..

# Setup frontend
cd frontend
npm install
cd ..

Write-Host "Development setup complete!"
