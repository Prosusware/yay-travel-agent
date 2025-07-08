#!/bin/bash

# LangGraph Agent Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
}

# Get project ID
get_project_id() {
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        print_error "No active GCP project found. Run 'gcloud config set project YOUR_PROJECT_ID'"
        exit 1
    fi
    print_status "Using GCP project: $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required GCP APIs..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    print_success "APIs enabled"
}

# Build and test locally
test_local() {
    print_status "Building Docker image locally..."
    docker build -t langgraph-agent-local .
    
    print_status "Testing container locally..."
    print_warning "Make sure to set your environment variables before testing:"
    echo "export MISTRAL_API_KEY=your_key"
    echo "export TAVILY_API_KEY=your_key"
    echo "export ELEVENLABS_API_KEY=your_key"
    echo "export ELEVENLABS_AGENT_ID=your_agent_id"
    echo "export ELEVENLABS_PHONE_NUMBER_ID=your_phone_id"
    echo ""
    echo "Then run: docker run -p 8080:8080 --env-file .env langgraph-agent-local"
}

# Deploy to GCP
deploy_gcp() {
    print_status "Deploying to Google Cloud Platform..."
    
    # Submit build to Cloud Build
    print_status "Submitting build to Cloud Build..."
    gcloud builds submit --config cloudbuild.yaml .
    
    print_success "Deployment completed!"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe langgraph-agent --region=us-central1 --format='value(status.url)')
    print_success "Service deployed at: $SERVICE_URL"
    
    print_status "Setting environment variables..."
    print_warning "Don't forget to set your environment variables in Cloud Run:"
    echo "gcloud run services update langgraph-agent --region=us-central1 \\"
    echo "  --set-env-vars MISTRAL_API_KEY=your_key,TAVILY_API_KEY=your_key,ELEVENLABS_API_KEY=your_key,ELEVENLABS_AGENT_ID=your_agent_id,ELEVENLABS_PHONE_NUMBER_ID=your_phone_id"
}

# Main script
main() {
    print_status "LangGraph Agent Deployment Script"
    echo "=================================="
    
    case "${1:-deploy}" in
        "local")
            print_status "Building and testing locally..."
            test_local
            ;;
        "deploy")
            print_status "Deploying to GCP..."
            check_gcloud
            get_project_id
            enable_apis
            deploy_gcp
            ;;
        "help")
            echo "Usage: $0 [local|deploy|help]"
            echo ""
            echo "Commands:"
            echo "  local   - Build and test Docker image locally"
            echo "  deploy  - Deploy to Google Cloud Platform (default)"
            echo "  help    - Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

main "$@" 