#!/bin/bash
# Docker Deployment Script
# Run this to deploy locally with Docker Compose

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Oil Spill Detection App - Docker Deployment ===${NC}"

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Install from: https://www.docker.com/products/docker-desktop${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose not found. Install from: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please update .env with your configuration and run again.${NC}"
    exit 1
fi

# Create SSL directory if needed
mkdir -p ssl

# Check for SSL certificates
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
    echo -e "${YELLOW}Creating self-signed SSL certificates...${NC}"
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    echo -e "${GREEN}SSL certificates created${NC}"
fi

# Build images
echo -e "\n${YELLOW}Building Docker images...${NC}"
docker-compose build

# Start services
echo -e "\n${YELLOW}Starting services...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "\n${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check container status
echo -e "\n${YELLOW}Checking container status...${NC}"
docker-compose ps

# Run database setup
echo -e "\n${YELLOW}Setting up database...${NC}"
# docker-compose exec mysql mysql -u root -p$DB_ROOT_PASSWORD < ODA\(OIL\)/oil_spill_detection/oil_spill_detection/database/oil_spill_db.sql || true

echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo "Services are running at:"
echo "- Oil Spill API: http://localhost:5000"
echo "- Portal: http://localhost:5001"
echo "- Real Time Detection: http://localhost:5002"
echo "- Nginx: https://localhost:443"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop containers: docker-compose down"
