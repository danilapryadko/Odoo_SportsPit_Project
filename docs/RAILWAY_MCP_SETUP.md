# Railway MCP Setup Guide

## Installation

Railway MCP server has been installed globally:
```bash
npm install -g railway-mcp
```

## MCP Server Configuration

The Railway MCP server has been added to Claude:
```bash
claude mcp add railway npx railway-mcp
```

## Authentication

### Token Configuration
Railway API token is stored in multiple locations:

1. **Environment Variable**:
```bash
export RAILWAY_TOKEN="4c02d552-4ed0-4787-8d3f-bf00eb20004a"
```

2. **MCP Config File**: `~/.railway-mcp/config.json`
```json
{
  "api_token": "4c02d552-4ed0-4787-8d3f-bf00eb20004a",
  "default_project": "athletic-emotion",
  "default_environment": "production"
}
```

3. **Project Documentation**: `/docs/RAILWAY_TOKEN.md`

## Available MCP Tools

Railway MCP provides 146+ tools for complete Railway management:

### Project Management
- `railway_project_list` - List all projects
- `railway_project_create` - Create new project
- `railway_project_delete` - Delete project
- `railway_project_get` - Get project details

### Service Management
- `railway_service_list` - List services
- `railway_service_create` - Create service
- `railway_service_update` - Update service
- `railway_service_delete` - Delete service
- `railway_service_logs` - Get service logs

### Deployment
- `railway_deploy_list` - List deployments
- `railway_deploy_create` - Create deployment
- `railway_deploy_cancel` - Cancel deployment
- `railway_deploy_status` - Check deployment status

### Database
- `railway_postgres_create` - Create PostgreSQL database
- `railway_postgres_list` - List databases
- `railway_postgres_connect` - Get connection string

### Environment Variables
- `railway_env_list` - List environment variables
- `railway_env_set` - Set environment variable
- `railway_env_delete` - Delete environment variable

### Domains
- `railway_domain_list` - List domains
- `railway_domain_create` - Create custom domain
- `railway_domain_delete` - Delete domain

## Usage Examples

### Check Project Status
```javascript
mcp__railway__project_get({
  project_id: "athletic-emotion"
})
```

### List Services
```javascript
mcp__railway__service_list({
  project_id: "athletic-emotion"
})
```

### Deploy Application
```javascript
mcp__railway__deploy_create({
  project_id: "athletic-emotion",
  service_id: "service-id",
  source: "github"
})
```

### Set Environment Variable
```javascript
mcp__railway__env_set({
  project_id: "athletic-emotion",
  service_id: "service-id",
  key: "DB_HOST",
  value: "postgresql-odoo.railway.internal"
})
```

## Project Configuration

The Odoo SportsPit project is configured with:

- **Project**: athletic-emotion
- **Environment**: production
- **Database**: PostgreSQL (Railway internal)
- **Service**: Odoo 17.0

## Files

- `Dockerfile` - Railway-optimized Docker configuration
- `railway.json` - Railway deployment settings
- `odoo.conf` - Odoo configuration with Railway database

## Troubleshooting

1. **Authentication Issues**:
   - Verify token in environment: `echo $RAILWAY_TOKEN`
   - Check MCP config: `cat ~/.railway-mcp/config.json`

2. **MCP Connection Issues**:
   - Restart Claude to reload MCP servers
   - Check MCP status: `claude mcp list`

3. **Deployment Issues**:
   - Check logs with MCP tools
   - Verify environment variables
   - Ensure PostgreSQL is running

## Support

- Railway Docs: https://docs.railway.app
- MCP Docs: https://github.com/crazyrabbitltc/railway-mcp
- Project: https://athletic-emotion.railway.app