# Contributing to mdshrink

Thank you for considering contributing to mdshrink!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Manish3451/mdshrink.git
cd mdshrink

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .

# Install dev dependencies (if any)
pip install -e .[dev]
```

## Running Tests

```bash
pytest
```

## Code Style

We use Ruff for linting:

```bash
ruff check .
ruff format .
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Questions?

Open an issue for discussions or questions.