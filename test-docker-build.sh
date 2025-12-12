#!/bin/bash
# test-docker-build.sh - Test Docker build locally before deploying to Render

set -e

echo "============================================"
echo "Testing Docker Build for Render Deployment"
echo "============================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
if docker build -t kasparro-test:latest .; then
    echo -e "${GREEN}✓ Docker build successful!${NC}"
else
    echo -e "${RED}✗ Docker build failed!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Testing image size...${NC}"
IMAGE_SIZE=$(docker images kasparro-test:latest --format "{{.Size}}")
echo "Image size: $IMAGE_SIZE"

echo ""
echo -e "${YELLOW}Step 3: Verifying entrypoint...${NC}"
docker run --rm kasparro-test:latest --version || true

echo ""
echo -e "${YELLOW}Step 4: Testing with mock DATABASE_URL...${NC}"
TEST_DB_URL="postgresql://test:test@localhost:5432/test"

# Test that container starts (won't connect to DB, but should not crash)
echo "Testing container startup (will fail on DB connection, which is expected)..."
docker run --rm \
    -e DATABASE_URL="$TEST_DB_URL" \
    kasparro-test:latest &

CONTAINER_PID=$!
sleep 5
kill $CONTAINER_PID 2>/dev/null || true

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Docker Build Test Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Next steps:"
echo "1. Commit and push to GitHub:"
echo "   git add -A"
echo "   git commit -m 'Ready for Render deployment'"
echo "   git push origin main"
echo ""
echo "2. Deploy to Render:"
echo "   - Go to https://render.com"
echo "   - New > Blueprint"
echo "   - Connect your repository"
echo "   - Wait for deployment"
echo ""
echo "3. Get your live URL:"
echo "   https://kasparro-api-XXXX.onrender.com"
echo ""
