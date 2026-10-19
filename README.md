# Supermarket Voice Navigator

An AI-powered assistant for visually impaired people to navigate supermarkets using voice commands.

## Overview

This application provides voice-guided navigation assistance for visually impaired users in supermarket environments. It uses AI to understand voice commands, provide real-time navigation guidance, and help locate products efficiently.

## Features

- Voice-activated navigation assistance
- Product location guidance
- Real-time audio feedback
- Accessible user interface
- Integration with supermarket layout data

## Requirements

- Python 3.8+
- Microphone access
- Audio output (speakers/headphones)

## Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Usage

Run the main application:
```bash
python src/main.py
```

## Project Structure

```
├── src/
│   ├── main.py              # Main application entry point
│   ├── voice_interface.py   # Voice recognition and synthesis
│   ├── navigation.py        # Navigation logic and pathfinding
│   ├── product_locator.py   # Product search and location
│   └── config/
│       └── settings.py      # Configuration management
├── data/
│   └── store_layouts/       # Store layout data
├── tests/
│   └── test_*.py           # Unit tests
├── docs/
│   └── api.md              # API documentation
├── requirements.txt
├── config.yaml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License