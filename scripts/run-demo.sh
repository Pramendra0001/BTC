#!/bin/bash
set -e

echo "=== BTC-SHIELD Demo Runner ==="

# 1. Generate sample data
echo "Generating 1000 sample records for demo..."
python data/generators/generate_dataset.py --size 1000 --format csv --output data/samples/

# 2. Start services
echo "Starting Docker Compose services..."
docker-compose up -d

# 3. Wait for backend
echo "Waiting for backend to be ready..."
sleep 10

# 4. Trigger data ingestion (Assuming endpoint exists)
echo "Ingesting sample data..."
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/app/data/samples/dataset_1000.csv"}' || echo "Note: Replace with actual ingest logic"

echo "Demo is running! Access the frontend at http://localhost:3000"
echo "To stop: docker-compose down"
