#!/bin/bash

# Azure Deployment Script for RWE Study Planner
# This script deploys all services to Azure

set -e

# Configuration
RESOURCE_GROUP="rwe-planner-rg"
LOCATION="eastus"
ACR_NAME="rweplanner"
APP_SERVICE_PLAN="rwe-planner-plan"
KEY_VAULT_NAME="rwe-planner-kv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Azure deployment for RWE Study Planner${NC}"

# Check if logged in to Azure
echo "Checking Azure login status..."
if ! az account show &>/dev/null; then
    echo -e "${RED}Not logged in to Azure. Please run 'az login' first.${NC}"
    exit 1
fi

# Create Resource Group
echo -e "${YELLOW}Creating Resource Group: $RESOURCE_GROUP${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo -e "${YELLOW}Creating Azure Container Registry: $ACR_NAME${NC}"
az acr create --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

echo -e "${GREEN}ACR Login Server: $ACR_LOGIN_SERVER${NC}"

# Create Key Vault
echo -e "${YELLOW}Creating Key Vault: $KEY_VAULT_NAME${NC}"
az keyvault create --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Store secrets in Key Vault
echo -e "${YELLOW}Storing secrets in Key Vault${NC}"
az keyvault secret set --vault-name $KEY_VAULT_NAME \
    --name "acr-username" \
    --value "$ACR_USERNAME"

az keyvault secret set --vault-name $KEY_VAULT_NAME \
    --name "acr-password" \
    --value "$ACR_PASSWORD"

# Build and push Docker images
echo -e "${YELLOW}Building and pushing Docker images to ACR${NC}"

# Login to ACR
echo $ACR_PASSWORD | docker login $ACR_LOGIN_SERVER -u $ACR_USERNAME --password-stdin

# Array of services
services=(
    "mcp_RealWorldDataIngestor"
    "mcp_EHRConnector"
    "mcp_ClaimsDataParser"
    "mcp_SiteFeasibilityPredictor"
    "mcp_DiversityIndexMapper"
    "mcp_ProtocolComplexityScorer"
    "mcp_SoA_Comparator"
    "orchestrator"
)

# Build and push each service
for service in "${services[@]}"; do
    echo -e "${YELLOW}Building $service...${NC}"
    docker build -t $ACR_LOGIN_SERVER/$service:latest ./services/$service
    
    echo -e "${YELLOW}Pushing $service to ACR...${NC}"
    docker push $ACR_LOGIN_SERVER/$service:latest
done

# Build and push frontend
echo -e "${YELLOW}Building frontend...${NC}"
docker build -t $ACR_LOGIN_SERVER/frontend:latest ./frontend
docker push $ACR_LOGIN_SERVER/frontend:latest

# Create App Service Plan
echo -e "${YELLOW}Creating App Service Plan: $APP_SERVICE_PLAN${NC}"
az appservice plan create --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux

# Deploy services as Web Apps
echo -e "${YELLOW}Deploying services as Azure Web Apps${NC}"

# Deploy Orchestrator
echo -e "${YELLOW}Deploying Orchestrator...${NC}"
az webapp create --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name rwe-orchestrator \
    --deployment-container-image-name $ACR_LOGIN_SERVER/orchestrator:latest

az webapp config container set --name rwe-orchestrator \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name $ACR_LOGIN_SERVER/orchestrator:latest \
    --docker-registry-server-url https://$ACR_LOGIN_SERVER \
    --docker-registry-server-user $ACR_USERNAME \
    --docker-registry-server-password $ACR_PASSWORD

# Set environment variables for Orchestrator
az webapp config appsettings set --name rwe-orchestrator \
    --resource-group $RESOURCE_GROUP \
    --settings \
    PORT=8240 \
    DATA_INGESTOR_URL=http://rwe-dataingestor.azurewebsites.net \
    EHR_CONNECTOR_URL=http://rwe-ehrconnector.azurewebsites.net \
    CLAIMS_PARSER_URL=http://rwe-claimsparser.azurewebsites.net \
    FEASIBILITY_URL=http://rwe-feasibility.azurewebsites.net \
    DIVERSITY_URL=http://rwe-diversity.azurewebsites.net \
    PROTOCOL_URL=http://rwe-protocolscorer.azurewebsites.net \
    SOA_URL=http://rwe-soacomparator.azurewebsites.net

# Deploy Frontend
echo -e "${YELLOW}Deploying Frontend...${NC}"
az webapp create --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name rwe-planner-ui \
    --deployment-container-image-name $ACR_LOGIN_SERVER/frontend:latest

az webapp config container set --name rwe-planner-ui \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name $ACR_LOGIN_SERVER/frontend:latest \
    --docker-registry-server-url https://$ACR_LOGIN_SERVER \
    --docker-registry-server-user $ACR_USERNAME \
    --docker-registry-server-password $ACR_PASSWORD

# Set environment variables for Frontend
az webapp config appsettings set --name rwe-planner-ui \
    --resource-group $RESOURCE_GROUP \
    --settings \
    REACT_APP_API_URL=https://rwe-orchestrator.azurewebsites.net

# Deploy each MCP service
for service in "${services[@]:0:7}"; do
    service_name=$(echo $service | tr '_' '-' | tr '[:upper:]' '[:lower:]')
    echo -e "${YELLOW}Deploying $service_name...${NC}"
    
    az webapp create --resource-group $RESOURCE_GROUP \
        --plan $APP_SERVICE_PLAN \
        --name rwe-$service_name \
        --deployment-container-image-name $ACR_LOGIN_SERVER/$service:latest
    
    az webapp config container set --name rwe-$service_name \
        --resource-group $RESOURCE_GROUP \
        --docker-custom-image-name $ACR_LOGIN_SERVER/$service:latest \
        --docker-registry-server-url https://$ACR_LOGIN_SERVER \
        --docker-registry-server-user $ACR_USERNAME \
        --docker-registry-server-password $ACR_PASSWORD
    
    az webapp config appsettings set --name rwe-$service_name \
        --resource-group $RESOURCE_GROUP \
        --settings PORT=8240
done

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}Frontend URL: https://rwe-planner-ui.azurewebsites.net${NC}"
echo -e "${GREEN}API URL: https://rwe-orchestrator.azurewebsites.net${NC}"

# Output connection strings
echo -e "${YELLOW}Saving connection information...${NC}"
cat > azure/connection-info.txt << EOF
Resource Group: $RESOURCE_GROUP
ACR Login Server: $ACR_LOGIN_SERVER
Frontend URL: https://rwe-planner-ui.azurewebsites.net
API URL: https://rwe-orchestrator.azurewebsites.net
Key Vault: $KEY_VAULT_NAME

Service URLs:
- Data Ingestor: https://rwe-mcp-realworlddataingestor.azurewebsites.net
- EHR Connector: https://rwe-mcp-ehrconnector.azurewebsites.net
- Claims Parser: https://rwe-mcp-claimsdataparser.azurewebsites.net
- Site Feasibility: https://rwe-mcp-sitefeasibilitypredictor.azurewebsites.net
- Diversity Mapper: https://rwe-mcp-diversityindexmapper.azurewebsites.net
- Protocol Scorer: https://rwe-mcp-protocolcomplexityscorer.azurewebsites.net
- SoA Comparator: https://rwe-mcp-soa-comparator.azurewebsites.net
EOF

echo -e "${GREEN}Connection information saved to azure/connection-info.txt${NC}"