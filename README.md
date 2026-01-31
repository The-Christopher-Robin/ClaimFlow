# ClaimFlow - Instant Auto Claims Adjuster

ClaimFlow is a demo application that uses AI agents to instantly process auto insurance claims. Upload a damage photo and policy ID to get an immediate claim decision with a PDF offer letter.

## Features

- **Vision Agent**: Mocked image analysis that returns damage type, severity, and estimated cost
- **Policy Agent**: RAG over policy documents (stub implementation with watsonx Discovery support planned)
- **Finance Agent**: Calculates payout (estimated_cost - deductible)
- **PDF Generation**: Automatically generates offer letters using reportlab
- **Notifications**: Sends alerts via Slack webhook and SMTP (stub)
- **Streamlit UI**: User-friendly interface for claim submission
- **FastAPI Backend**: RESTful API for claim processing
- **Docker Support**: Fully containerized application

## Architecture

```
┌─────────────────┐
│  Streamlit UI   │
│  (Port 8501)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   FastAPI       │─────▶│ Vision Agent │
│   (Port 8000)   │      └──────────────┘
└────────┬────────┘
         │              ┌──────────────┐
         ├─────────────▶│ Policy Agent │
         │              └──────────────┘
         │
         │              ┌──────────────┐
         ├─────────────▶│ Finance Agent│
         │              └──────────────┘
         │
         ├──────────────▶ PDF Generation
         │
         └──────────────▶ Notifications (Slack/Email)
```

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/The-Christopher-Robin/ClaimFlow.git
cd ClaimFlow

# Start the application
docker-compose up

# Access the UI at http://localhost:8501
# API documentation at http://localhost:8000/docs
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI backend
uvicorn app.main:app --reload

# In a separate terminal, start the Streamlit UI
streamlit run streamlit_app.py
```

## Usage

1. Open the Streamlit UI at http://localhost:8501
2. Enter a Policy ID (try POL001, POL002, or POL003)
3. Upload a damage photo (any image file)
4. Click "Process Claim"
5. View the instant claim decision and download the PDF offer letter

## Sample Policy IDs

- **POL001**: $500 deductible, $50,000 coverage limit
- **POL002**: $1,000 deductible, $100,000 coverage limit
- **POL003**: $250 deductible, $25,000 coverage limit

## API Endpoints

### Process Claim
```
POST /api/claims/process
Content-Type: multipart/form-data

Parameters:
- policy_id (required): Policy ID
- image (required): Damage photo file
- email (optional): Email for notification

Response: ClaimResponse with damage analysis, policy info, payout, and PDF path
```

### Download PDF
```
GET /api/claims/{claim_id}/pdf

Response: PDF file download
```

### Health Check
```
GET /health

Response: {"status": "healthy", "timestamp": "..."}
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py
```

## Environment Variables

- `SLACK_WEBHOOK_URL`: Slack webhook URL for notifications (optional)
- `API_URL`: API base URL for Streamlit (default: http://localhost:8000)

## Project Structure

```
ClaimFlow/
├── app/
│   ├── agents/
│   │   ├── vision.py       # Vision agent (mocked image analysis)
│   │   ├── policy.py       # Policy agent (RAG stub)
│   │   └── finance.py      # Finance agent (payout calculation)
│   ├── models/
│   │   └── __init__.py     # Pydantic models
│   ├── services/
│   │   ├── pdf_service.py          # PDF generation
│   │   └── notification_service.py # Slack/Email notifications
│   └── main.py             # FastAPI application
├── tests/                  # Test suite
├── streamlit_app.py        # Streamlit UI
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Multi-container setup
└── README.md              # This file
```

## Development

### Adding New Damage Types

Edit `app/agents/vision.py` and add to the `damage_types` list.

### Configuring Policies

Edit `app/agents/policy.py` and modify the `policies` dictionary.

### Customizing PDF Layout

Edit `app/services/pdf_service.py` to change the PDF template.

## Future Enhancements

- [ ] Integrate real computer vision API (IBM Watson Visual Recognition)
- [ ] Implement full watsonx Discovery RAG for policy documents
- [ ] Add actual SMTP email sending
- [ ] Implement claim history and database persistence
- [ ] Add user authentication
- [ ] Support multiple languages
- [ ] Add claim status tracking
- [ ] Implement appeal process

## IBM Hackathon

This project was created for the IBM Hackathon to demonstrate instant auto claims processing using AI agents.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request
