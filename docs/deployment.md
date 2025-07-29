# Deployment Guide

This document explains how to deploy the Meta-Analysis MCP Server using GitHub Actions and Fly.io.

## GitHub Actions Deployment

The repository is configured with GitHub Actions workflows for continuous integration and deployment:

1. **CI Workflow** (.github/workflows/ci.yml)
   - Runs on pull requests and pushes to main/master branches
   - Sets up Python environment
   - Installs dependencies
   - Runs tests
   - Performs basic linting

2. **Deployment Workflow** (.github/workflows/deploy.yml)
   - Runs on pushes to main/master branches
   - Sets up Python environment
   - Installs dependencies
   - Runs tests
   - Deploys to Fly.io using the existing configuration

## Fly.io Deployment

The application is configured for deployment to Fly.io, a free hosting platform for small applications.

### Prerequisites

To deploy manually:

1. Install the Fly.io CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Login to Fly.io: `flyctl auth login`
3. Deploy the application: `flyctl deploy`

### Configuration

The deployment configuration is defined in `fly.toml`:

- App name: meta-analysis-mcp-server
- Region: sjc (San Jose, California)
- Resources: 1 shared CPU, 512MB memory
- HTTP service on ports 80/443
- Health check endpoint: /health

## GitHub Actions Secrets

For the GitHub Actions deployment to work, you need to set up the following secret in your GitHub repository:

- `FLY_API_TOKEN`: Your Fly.io API token

To set up this secret:

1. Generate a Fly.io API token: `flyctl auth token`
2. Go to your GitHub repository
3. Navigate to Settings > Secrets and variables > Actions
4. Click "New repository secret"
5. Name: FLY_API_TOKEN
6. Value: (paste your Fly.io API token)
7. Click "Add secret"

## Application URL

After deployment, the application will be available at:

https://meta-analysis-mcp-server.fly.dev
