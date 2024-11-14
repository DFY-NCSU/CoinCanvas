class Constants {
  // API URLs
  static const String baseUrl = 'http://localhost:8000';
  static const String apiUrl = '$baseUrl/api';

  // API Endpoints
  static const String loginEndpoint = '$baseUrl/token';
  static const String expensesEndpoint = '$baseUrl/expenses';
  static const String statisticsEndpoint = '$baseUrl/statistics';

  // Categories
  static const List<String> expenseCategories = [
    'Food',
    'Transportation',
    'Shopping',
    'Entertainment',
    'Bills',
    'Health',
    'Education',
    'Others'
  ];

  // Payment Methods
  static const List<String> paymentMethods = [
    'Cash',
    'Credit Card',
    'Debit Card',
    'UPI',
    'Bank Transfer',
    'Others'
  ];

  // Colors for categories (Add your color constants here)
  static const Map<String, String> categoryColors = {
    'Food': '#FF6B6B',
    'Transportation': '#4ECDC4',
    'Shopping': '#45B7D1',
    'Entertainment': '#96CEB4',
    'Bills': '#D4A373',
    'Health': '#FF9F1C',
    'Education': '#2AB7CA',
    'Others': '#6C757D'
  };

  // Date Formats
  static const String dateFormat = 'MMM dd, yyyy';
  static const String timeFormat = 'HH:mm';

  // Error Messages
  static const String genericError = 'Something went wrong. Please try again.';
  static const String networkError = 'Network error. Please check your connection.';
  static const String authError = 'Authentication failed. Please login again.';
}