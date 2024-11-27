# Expense Tracker Backend Documentation

## Overview
This is a FastAPI-based backend service for an expense tracking application. The system allows users to track personal expenses and manage shared expenses within groups. It features JWT-based authentication, SQLAlchemy ORM for database operations, and comprehensive input validation.

## Core Components

### Authentication & Security
- Uses JWT (JSON Web Tokens) for user authentication
- OAuth2 password flow implementation
- Bcrypt password hashing via PassLib
- Protected routes using FastAPI's dependency injection
- Environment variable configuration for sensitive data

### Database Models

#### User Management
- `User`: Stores user information (email, hashed password, full name)
- Email-based authentication
- One-to-many relationship with personal expenses

#### Personal Expenses
- `Expense`: Tracks individual user expenses
- Fields: date, category, amount, description, payment method
- Associated with specific users through foreign keys

#### Group Management
- `Group`: Manages expense sharing groups
- `GroupMember`: Tracks group membership
- Created-by relationship to track group ownership
- Timestamp tracking for group creation and member joining

#### Group Expenses
- `GroupExpense`: Handles shared expenses within groups
- `ExpenseSplit`: Manages expense distribution among group members
- Supports both equal and custom splitting of expenses
- Tracks payment status and individual shares

### API Endpoints

#### Authentication
- `/token`: Login endpoint for JWT token generation
- Protected routes using OAuth2 password bearer scheme

#### User Management
- POST `/users/`: User registration
- Input validation for email and password

#### Personal Expenses
- GET `/expenses/`: List user's personal expenses
- POST `/expenses/`: Create new personal expense
- DELETE `/expenses/{expense_id}`: Remove personal expense
- Pagination support via skip/limit parameters

#### Group Features
- POST `/groups/`: Create new expense sharing group
- POST `/groups/{group_id}/join`: Join existing group
- GET `/groups/`: List user's groups
- GET `/groups/search/`: Search groups by name
- Comprehensive group expense management endpoints

#### Group Expense Management
- POST `/groups/{group_id}/expenses`: Create group expense
- GET `/groups/{group_id}/expenses/`: List group expenses
- DELETE `/groups/{group_id}/expenses/{expense_id}`: Remove group expense
- Supports both equal and custom expense splitting

### Data Validation

#### Input Validation
- Pydantic models for request/response validation
- Strict type checking and constraints
- Custom validation for:
  - Non-empty strings
  - Positive amounts
  - Valid dates
  - Email format
  - Payment methods
  - Split calculations

#### Business Logic Validation
- Membership verification for group operations
- Permission checking for expense deletion
- Split amount verification
- Duplicate membership prevention
- Group existence verification

### Error Handling
- Custom HTTP exceptions for various error cases
- Proper status codes for different scenarios
- Detailed error messages for client feedback
- Authentication failure handling
- Resource not found handling

### Database Management
- SQLAlchemy session management
- Connection pooling
- Proper session cleanup
- Support for SQLite with thread safety
- Environment-based database configuration

## Technical Implementation Details

### Dependencies
- FastAPI: Web framework
- SQLAlchemy: ORM
- PassLib: Password hashing
- Python-Jose: JWT handling
- Python-multipart: Form data parsing
- Python-dotenv: Environment configuration

### Code Structure
- Modular design with separate files for:
  - Models (models.py)
  - Schemas (schemas.py)
  - Database configuration (database.py)
  - CRUD operations (crud.py)
  - Main application (main.py)

### Security Considerations
- Password hashing with bcrypt
- JWT token expiration
- CORS middleware configuration
- Protected routes with proper authentication
- Input sanitization

### Performance Features
- Pagination for list endpoints
- Efficient database queries
- Proper index usage
- Session management
- Connection pooling

## Development Considerations

### Environment Setup
- Configurable database URL
- Secret key configuration
- CORS settings
- Token expiration settings

### Best Practices
- Type hints throughout the code
- Comprehensive input validation
- Proper error handling
- Clean code structure
- Modular design
- Consistent naming conventions

### Extensibility
- Abstract base classes for common functionality
- Modular CRUD operations
- Flexible schema design
- Easy to add new features
- Maintainable codebase structure