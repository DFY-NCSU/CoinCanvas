# Expense Tracker Project Tutorial

## Overview
This tutorial will guide you through setting up and running the Expense Tracker application. The project consists of three main components:
- FastAPI Backend
- Flutter Frontend
- SQLite Database

## Prerequisites
Before starting, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Flutter SDK
- Google Chrome (for Flutter web development)
- Git (for cloning the repository)

## Project Setup

### 1. Backend Setup

#### Install Dependencies
Navigate to the project root directory and run:
```bash
pip install -r backend/requirements.txt
```

This will install all necessary Python packages including:
- FastAPI
- SQLAlchemy
- Uvicorn
- Python-jose
- Passlib
- Python-multipart

#### Start the Backend Server
Run the following command to start the backend server:
```bash
uvicorn backend.app.main:app --reload
```

The `--reload` flag enables auto-reload during development, so the server will restart automatically when you make changes to the code.

#### Test the Backend API
Once the server is running, you can test the API using two built-in documentation interfaces:

1. Swagger UI: Open `http://127.0.0.1:8000/docs` in your browser
   - Interactive API documentation
   - Test endpoints directly from the browser
   - View request/response schemas
   - Authorize using JWT token

2. ReDoc: Open `http://127.0.0.1:8000/redoc` in your browser
   - Alternative API documentation
   - More detailed schema information
   - Better for reading and understanding the API structure

### 2. Frontend Setup

#### Install Flutter
If you haven't installed Flutter yet:
1. Download Flutter SDK from official website
2. Add Flutter to your system PATH
3. Run `flutter doctor` to verify installation

#### Setup Frontend Project
Navigate to the frontend directory and run:
```bash
flutter clean              # Clean the project
flutter pub get           # Install dependencies
flutter run -d chrome     # Run the app in Chrome
```

The application should now open in a Chrome window. If you encounter any errors, make sure:
- Chrome is installed
- Flutter web support is enabled
- All dependencies are properly installed

### 3. Database Setup

#### Demo Database
1. Download the demo database from the provided Google Drive link
2. Place the database file in the project root folder
3. The backend will automatically connect to this database

## Testing the Application

### 1. API Testing Using Swagger UI
1. Open `http://127.0.0.1:8000/docs`
2. Test the authentication:
   - Find the `/token` endpoint
   - Use the demo credentials to get a JWT token
   - Click "Authorize" button and enter the token

### 2. Available Test Endpoints
- POST `/users/`: Create a new user
- POST `/token`: Login and get access token
- GET `/expenses/`: View personal expenses
- POST `/expenses/`: Create new expense
- GET `/groups/`: View groups
- POST `/groups/`: Create new group

### 3. Testing Frontend Features
1. Launch the application in Chrome
2. Register a new account or use demo credentials
3. Try core features:
   - Add personal expenses
   - Create expense groups
   - Add group expenses
   - View expense statistics

## Common Issues and Solutions

### Backend Issues
1. Port already in use:
   ```bash
   # Change the port
   uvicorn backend.app.main:app --reload --port 8001
   ```

2. Database connection error:
   - Verify database file location
   - Check database file permissions
   - Ensure SQLite is installed

### Frontend Issues
1. Web server failed to start:
   ```bash
   flutter config --clear-features
   flutter run -d chrome
   ```

2. Package get failed:
   ```bash
   flutter clean
   flutter pub cache repair
   flutter pub get
   ```

## Development Tips

### Backend Development
- Use the `--reload` flag during development
- Check logs for detailed error messages
- Test new endpoints in Swagger UI before integration
- Use proper HTTP status codes
- Validate input data

### Frontend Development
- Use Flutter DevTools for debugging
- Test on multiple screen sizes
- Handle API errors gracefully
- Implement proper state management
- Follow Flutter best practices

## Next Steps
After setting up the project, you can:
1. Explore the API documentation
2. Create test data
3. Implement new features
4. Customize the UI
5. Add error handling
6. Implement additional security measures

## Support and Resources
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Flutter Documentation: https://flutter.dev/docs
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Project Issue Tracker: [Project GitHub Issues]

Remember to keep both backend and frontend running while testing the full application. The backend must be running for the frontend to function properly.