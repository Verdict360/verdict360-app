# Verdict360 SA Legal Integrations MCP Server

This MCP (Model Context Protocol) server provides seamless integration with South African legal practice management systems, enabling Verdict360 to synchronize data, create matters, and maintain compliance across multiple legal software platforms.

## Supported SA Legal Systems

### 1. **LawPracticeZA**
- **Capabilities**: Matters, Clients, Billing, Documents, Calendar
- **Authentication**: Bearer Token
- **API Version**: v1

### 2. **Legal Interact**  
- **Capabilities**: Case Management, Client Portal, Billing, Reporting
- **Authentication**: API Key
- **API Version**: v2

### 3. **AJS Legal Software**
- **Capabilities**: Practice Management, Accounting, Trust Accounting, Compliance
- **Authentication**: OAuth2
- **API Version**: Latest

### 4. **Legal Suite SA**
- **Capabilities**: Document Automation, Workflow, Client Management
- **Authentication**: Bearer Token
- **API Version**: v1

### 5. **Attorney Online**
- **Capabilities**: Matter Management, Time Tracking, Billing, Trust Funds
- **Authentication**: API Key
- **API Version**: v1

## Available Tools

### Connection Management
- **`connect_legal_system`**: Establish connection to SA legal software
- **`check_system_status`**: Verify connection status and capabilities

### Data Synchronization
- **`sync_legal_matters`**: Import legal matters from connected systems
- **`sync_client_data`**: Synchronize client information and profiles
- **`sync_billing_entries`**: Import time tracking and billing data

### Matter Management
- **`create_consultation_matter`**: Create new legal matter from Verdict360 consultation
- **`export_matter_data`**: Export comprehensive matter information for analysis

### Compliance & Reporting
- **`compliance_check`**: Run SA legal compliance audits
  - POPIA Compliance
  - Legal Practice Act requirements
  - Attorney Fidelity Fund compliance
  - Trust accounting regulations

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the MCP server
python server.py
```

## Configuration

### Environment Variables
```bash
# SA Legal System API Credentials
LAWPRACTICEZA_BEARER_TOKEN=your_token_here
LEGAL_INTERACT_API_KEY=your_api_key_here
AJS_LEGAL_CLIENT_ID=your_client_id
AJS_LEGAL_CLIENT_SECRET=your_client_secret
LEGAL_SUITE_BEARER_TOKEN=your_token_here
ATTORNEY_ONLINE_API_KEY=your_api_key_here

# MCP Server Configuration
MCP_SERVER_PORT=8080
MCP_LOG_LEVEL=INFO
```

## Usage Examples

### 1. Connect to LawPracticeZA
```json
{
  "tool": "connect_legal_system",
  "arguments": {
    "system": "lawpracticeza",
    "credentials": {
      "bearer_token": "your_bearer_token_here"
    }
  }
}
```

### 2. Sync Legal Matters
```json
{
  "tool": "sync_legal_matters", 
  "arguments": {
    "system": "lawpracticeza",
    "date_from": "2024-01-01",
    "status_filter": ["active", "pending"]
  }
}
```

### 3. Create Matter from Consultation
```json
{
  "tool": "create_consultation_matter",
  "arguments": {
    "system": "lawpracticeza",
    "consultation_data": {
      "client_name": "John Doe",
      "client_email": "john@example.co.za",
      "legal_area": "Contract Law", 
      "matter_description": "Review of employment contract",
      "urgency_level": "normal",
      "estimated_cost": 5000
    }
  }
}
```

### 4. Run POPIA Compliance Check
```json
{
  "tool": "compliance_check",
  "arguments": {
    "system": "lawpracticeza",
    "compliance_type": "popia_compliance",
    "scope": "full_practice"
  }
}
```

## Available Resources

### System Configurations
**URI**: `sa-legal://systems/configurations`
- Complete configuration details for all supported SA legal systems
- Authentication requirements and API endpoints
- System capabilities and limitations

### Compliance Frameworks  
**URI**: `sa-legal://compliance/frameworks`
- South African legal compliance requirements
- POPIA, Legal Practice Act, Trust Account regulations
- Compliance checking procedures and templates

### Matter Templates
**URI**: `sa-legal://matters/templates`
- Standardized templates for different SA legal matter types
- Default fields, billing rates, and time estimates
- Best practices for matter setup

### Billing Rates
**URI**: `sa-legal://billing/rates`
- Standard SA legal profession billing rates
- Attorney level differentiation (Junior, Senior, Partner)
- Specialized practice area premiums

## SA Legal Compliance Features

### POPIA Compliance (Protection of Personal Information Act)
- ✅ Client consent tracking and management
- ✅ Data processing record maintenance  
- ✅ Privacy policy compliance monitoring
- ✅ Data breach notification procedures

### Legal Practice Act Compliance
- ✅ Attorney admission requirement verification
- ✅ Continuing professional development tracking
- ✅ Professional conduct compliance monitoring
- ✅ Trust account management oversight

### Attorney Fidelity Fund Integration
- ✅ Monthly contribution payment tracking
- ✅ Trust account reporting automation
- ✅ Professional indemnity insurance verification
- ✅ Compliance certificate maintenance

### Trust Accounting Features
- ✅ Separate trust account monitoring
- ✅ Monthly reconciliation automation
- ✅ Client fund protection verification
- ✅ Auditing and regulatory reporting

## Integration Architecture

```
Verdict360 Platform
       ↓
MCP Server (This)
       ↓
┌─────────────────┐
│ SA Legal Systems│
├─────────────────┤
│ • LawPracticeZA │
│ • Legal Interact│
│ • AJS Legal     │
│ • Legal Suite   │
│ • Attorney Online│
└─────────────────┘
```

## Security Considerations

- **Encrypted Credential Storage**: All API credentials are encrypted at rest
- **Audit Trail**: Complete audit logging for all system interactions
- **Rate Limiting**: Configurable rate limits for API calls to legal systems
- **Data Privacy**: POPIA-compliant data handling and processing
- **Access Control**: Role-based access to different legal system integrations

## Error Handling

The MCP server provides comprehensive error handling for:
- **Connection Failures**: Network timeouts, authentication errors
- **API Rate Limits**: Automatic retry with exponential backoff
- **Data Validation**: Schema validation for all data exchanges
- **Compliance Violations**: Automatic flagging of compliance issues

## Monitoring and Logging

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Performance Metrics**: Response time and success rate tracking
- **Integration Health**: Regular health checks for all connected systems
- **Compliance Monitoring**: Automated compliance status reporting

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black server.py
mypy server.py
```

### Contributing
1. Follow SA legal software integration standards
2. Ensure POPIA compliance in all data handling
3. Add comprehensive tests for new integrations
4. Update documentation for new features

## Support

For technical support with SA legal system integrations:
- **Email**: mcp-support@verdict360.co.za
- **Documentation**: https://docs.verdict360.co.za/mcp/sa-legal
- **Legal Software Support**: Contact respective vendor support teams

---

**Disclaimer**: This MCP server is designed to work with South African legal practice management systems. Always verify compliance with local legal regulations and software vendor requirements before implementation.