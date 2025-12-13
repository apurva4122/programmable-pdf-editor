# Contributing to Programmable PDF Editor

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/programmable-pdf-editor.git`
3. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Code Style

- **Python**: Follow PEP 8
- **TypeScript/React**: Follow ESLint rules
- **Commits**: Use conventional commits format

## Pull Request Process

1. Update README.md if needed
2. Add tests if applicable
3. Ensure all tests pass
4. Submit PR with clear description

## Reporting Issues

Include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node versions)

