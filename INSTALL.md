# Installation Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Prerequisites Installation](#prerequisites-installation)
3. [Project Installation](#project-installation)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **CPU**: 1.6 GHz dual-core processor
- **RAM**: 4GB
- **Storage**: 1GB free space
- **OS**: 
  - Windows 10 or later
  - macOS 10.15 or later
  - Linux (Ubuntu 20.04 or equivalent)
- **Browser**: Google Chrome (latest version)

### Development Tools
- Python 3.8 or higher
- Flutter SDK
- Git
- SQLite

## Prerequisites Installation

### 1. Python Setup
```bash
# Windows
# Download Python from https://www.python.org/downloads/
# During installation, check "Add Python to PATH"

# macOS
brew install python3

# Linux
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Flutter Setup
```bash
# 1. Download Flutter SDK from https://flutter.dev/docs/get-started/install

# 2. Add Flutter to PATH
# Windows: Add [Flutter_Directory]\bin to System Environment Variables
# macOS/Linux: Add to ~/.bashrc or ~/.zshrc:
export PATH="$PATH:[Flutter_Directory]/bin"

# 3. Verify installation
flutter doctor
```

### 3. Git Setup
```bash
# Windows
# Download from https://git-scm.com/download/win

# macOS
brew install git

# Linux
sudo apt install git
```

## Project Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/expense-tracker.git
cd expense-tracker
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
flutter pub get
```

### 4. Database Setup
```bash
# Download demo database
# Place the database file in the project root folder
# Verify database path in backend/app/database.py
```

## Configuration

### 1. Environment Variables
Create a `.env` file in the backend directory:
```plaintext
DATABASE_URL=sqlite:///./expenses.db
SECRET_KEY=your-secret-key
```

### 2. Backend Configuration
Update `backend/app/main.py` if needed:
```python
# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### 3. Frontend Configuration
Update `frontend/lib/config.dart`:
```dart
const String apiUrl = 'http://localhost:8000';
```

## Running the Application

### 1. Start Backend Server
```bash
# From project root directory
uvicorn backend.app.main:app --reload
```

### 2. Start Frontend Application
```bash
# From frontend directory
flutter run -d chrome
```

### 3. Verify Installation
- Backend API documentation: http://127.0.0.1:8000/docs
- Frontend application: http://localhost:3000

## Troubleshooting

### Common Issues and Solutions

#### Backend Issues
1. Port already in use
```bash
# Change port number
uvicorn backend.app.main:app --reload --port 8001
```

2. Database connection error
```bash
# Check database file permissions
chmod 644 expenses.db

# Verify database path in .env file
DATABASE_URL=sqlite:///./expenses.db
```

#### Frontend Issues
1. Flutter web not working
```bash
# Enable web support
flutter config --enable-web

# Clear Flutter build
flutter clean
flutter pub get
```

2. Package conflicts
```bash
flutter clean
flutter pub cache repair
flutter pub get
```

### Getting Help
- Check the [Project Documentation](docs/)
- Submit an issue on GitHub
- Contact the development team
- Join the project Discord server

## Next Steps
After successful installation:
1. Create a test account
2. Explore the API documentation
3. Try the demo features
4. Set up your first expense group

## Security Notes
- Change the default secret key
- Use strong passwords
- Keep your dependencies updated
- Don't expose the database file publicly

For additional help or reporting issues, please visit our [GitHub repository](https://github.com/your-repo/expense-tracker).