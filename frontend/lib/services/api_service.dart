import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';  // Fixed import
import '../models/expense.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  static const String baseUrl = 'http://127.0.0.1:8000';
  String? _token;
  String? _tokenType;

  // Initialize with stored token
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
    _tokenType = prefs.getString('token_type');
  }

  // Store token
  Future<void> _persistToken(String token, String tokenType) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
    await prefs.setString('token_type', tokenType);
    _token = token;
    _tokenType = tokenType;
  }

  // Clear stored token
  Future<void> _clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    await prefs.remove('token_type');
    _token = null;
    _tokenType = null;
  }

  // Headers with authentication
  Map<String, String> get _headers {
    final headers = {'Content-Type': 'application/json'};
    if (_token != null && _tokenType != null) {
      headers['Authorization'] = '$_tokenType $_token';
    }
    return headers;
  }

  // Signup method
  Future<bool> signup({
    required String email,
    required String password,
    required String fullName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/users/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          'full_name': fullName,
        }),
      );

      print('Signup response status: ${response.statusCode}');
      print('Signup response body: ${response.body}');

      if (response.statusCode == 200) {
        return await login(email, password);
      } else {
        throw Exception('Signup failed: ${response.body}');
      }
    } catch (e) {
      print('Signup error: $e');
      throw Exception('Failed to create account: $e');
    }
  }

  // Login method
  Future<bool> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/token'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': email,
          'password': password,
        },
      );

      print('Login response status: ${response.statusCode}');
      print('Login response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        await _persistToken(data['access_token'], data['token_type']);
        return true;
      }
      return false;
    } catch (e) {
      print('Login error: $e');
      return false;
    }
  }

  // Logout method
  Future<void> logout() async {
    await _clearToken();
  }

  // Get all expenses
  Future<List<Expense>> getExpenses() async {
    try {
      if (_token == null) {
        throw Exception('Not authenticated');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/expenses/'),
        headers: _headers,
      );

      print('Get expenses response status: ${response.statusCode}');
      print('Get expenses response body: ${response.body}');

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => Expense.fromJson(json)).toList();
      } else if (response.statusCode == 401) {
        await _clearToken();
        throw Exception('Unauthorized. Please log in again.');
      } else {
        throw Exception('Failed to load expenses. Status: ${response.statusCode}');
      }
    } catch (e) {
      print('Get expenses error: $e');
      rethrow;
    }
  }

  // Create new expense
  Future<Expense> createExpense(Expense expense) async {
    try {
      if (_token == null) {
        throw Exception('Not authenticated');
      }

      print('Creating expense with data: ${jsonEncode(expense.toJson())}');
      print('Using headers: $_headers');
      
      final response = await http.post(
        Uri.parse('$baseUrl/expenses/'),
        headers: _headers,
        body: jsonEncode(expense.toJson()),
      );

      print('Create expense response status: ${response.statusCode}');
      print('Create expense response body: ${response.body}');

      if (response.statusCode == 200) {
        return Expense.fromJson(json.decode(response.body));
      } else if (response.statusCode == 401) {
        await _clearToken();
        throw Exception('Unauthorized. Please log in again.');
      } else {
        throw Exception('Failed to create expense. Status: ${response.statusCode}, Body: ${response.body}');
      }
    } catch (e) {
      print('Create expense error: $e');
      rethrow;
    }
  }

  // Delete expense
  Future<void> deleteExpense(int id) async {
    try {
      if (_token == null) {
        throw Exception('Not authenticated');
      }

      print('Deleting expense with ID: $id');
      
      final response = await http.delete(
        Uri.parse('$baseUrl/expenses/$id'),
        headers: _headers,
      );

      print('Delete expense response status: ${response.statusCode}');
      print('Delete expense response body: ${response.body}');

      if (response.statusCode == 200) {
        return;
      } else if (response.statusCode == 401) {
        await _clearToken();
        throw Exception('Unauthorized. Please log in again.');
      } else if (response.statusCode == 404) {
        throw Exception('Expense not found');
      } else {
        throw Exception('Failed to delete expense. Status: ${response.statusCode}');
      }
    } catch (e) {
      print('Delete expense error: $e');
      rethrow;
    }
  }

  // Update expense
  Future<Expense> updateExpense(int id, Expense expense) async {
    try {
      if (_token == null) {
        throw Exception('Not authenticated');
      }

      print('Updating expense with ID: $id');
      print('Update data: ${jsonEncode(expense.toJson())}');
      
      final response = await http.put(
        Uri.parse('$baseUrl/expenses/$id'),
        headers: _headers,
        body: jsonEncode(expense.toJson()),
      );

      print('Update expense response status: ${response.statusCode}');
      print('Update expense response body: ${response.body}');

      if (response.statusCode == 200) {
        return Expense.fromJson(json.decode(response.body));
      } else if (response.statusCode == 401) {
        await _clearToken();
        throw Exception('Unauthorized. Please log in again.');
      } else if (response.statusCode == 404) {
        throw Exception('Expense not found');
      } else {
        throw Exception('Failed to update expense. Status: ${response.statusCode}');
      }
    } catch (e) {
      print('Update expense error: $e');
      rethrow;
    }
  }

  // Get statistics
  Future<Map<String, dynamic>> getStatistics() async {
    try {
      if (_token == null) {
        throw Exception('Not authenticated');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/statistics/by_category'),
        headers: _headers,
      );

      print('Get statistics response status: ${response.statusCode}');
      print('Get statistics response body: ${response.body}');

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        await _clearToken();
        throw Exception('Unauthorized. Please log in again.');
      } else {
        throw Exception('Failed to load statistics. Status: ${response.statusCode}');
      }
    } catch (e) {
      print('Get statistics error: $e');
      rethrow;
    }
  }

  // Check authentication status
  bool get isAuthenticated => _token != null;
}