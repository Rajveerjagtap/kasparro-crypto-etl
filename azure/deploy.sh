#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Root is the parent of the script directory
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Variables
RESOURCE_GROUP="kasparro-rg-eastus2"
LOCATION="eastus2"
# Generate a random password for the database if not provided
DB_PASSWORD=${DB_PASSWORD:-"Kasparro$(openssl rand -hex 4)!"}

echo "Using Resource Group: $RESOURCE_GROUP"
echo "Using Location: $LOCATION"

# Create Resource Group
echo "Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy Infrastructure
echo "Deploying Infrastructure (this may take a few minutes)..."
# We use a placeholder image initially so the deployment succeeds before we build our own image
DEPLOYMENT_OUTPUT=$(az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file "$SCRIPT_DIR/main.bicep" \
  --parameters dbPassword=$DB_PASSWORD \
  --query properties.outputs \
  --output json)

ACR_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r .acrName.value)
ACR_LOGIN_SERVER=$(echo $DEPLOYMENT_OUTPUT | jq -r .acrLoginServer.value)
BACKEND_URL=$(echo $DEPLOYMENT_OUTPUT | jq -r .backendUrl.value)

echo "Infrastructure deployed successfully."
echo "ACR Name: $ACR_NAME"
echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Build and Push Docker Image
echo "Building and Pushing Docker Image to ACR..."

# Build from the project root
az acr build --registry $ACR_NAME --image kasparro:latest "$PROJECT_ROOT"

# Update Container Apps to use the new image
echo "Updating Container Apps to use the new image..."

echo "Updating Backend..."
az containerapp update \
  --name kasparro-backend \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_LOGIN_SERVER/kasparro:latest

echo "Updating Scheduler..."
az containerapp update \
  --name kasparro-scheduler \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_LOGIN_SERVER/kasparro:latest

echo "--------------------------------------------------"
echo "Deployment Complete!"
echo "API is available at: https://$BACKEND_URL"
echo "--------------------------------------------------"
