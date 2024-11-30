import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';  // Fixed import
import '../models/expense.dart';
import '../models/group.dart';
import '../models/group_expense.dart';
import '../models/group_member.dart';

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

  // Create a new group
  Future<Group> createGroup(String name) async {
    final response = await http.post(
      Uri.parse('$baseUrl/groups/'),
      headers: _headers,
      body: jsonEncode({'name': name}),
    );

    if (response.statusCode == 200) {
      return Group.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to create group: ${response.body}');
    }
  }

  // Join a group by ID
  Future<void> joinGroup(int groupId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/groups/$groupId/join'),
      headers: _headers,
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to join group: ${response.body}');
    }
  }

  // Get groups the user is a member of
  Future<List<Group>> getUserGroups() async {
    final response = await http.get(
      Uri.parse('$baseUrl/groups/'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => Group.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load groups: ${response.body}');
    }
  }

  // Search groups by name
  Future<List<Group>> searchGroups(String name) async {
    final response = await http.get(
      Uri.parse('$baseUrl/groups/search/?name=$name'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => Group.fromJson(e)).toList();
    } else {
      throw Exception('Failed to search groups: ${response.body}');
    }
  }

  // Get expenses for a group
  Future<List<GroupExpense>> getGroupExpenses(int groupId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/groups/$groupId/expenses/'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => GroupExpense.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load group expenses: ${response.body}');
    }
  }

  // Create a group expense
  Future<GroupExpense> createGroupExpense(int groupId, GroupExpense expense) async {
    try {
      // Convert customSplits Map<int, double> to a Map<String, double>
      Map<String, dynamic>? customSplitsJson;
      if (expense.customSplits != null) {
        customSplitsJson = expense.customSplits!.map(
          (key, value) => MapEntry(key.toString(), value),
        );
      }

      final response = await http.post(
        Uri.parse('$baseUrl/groups/$groupId/expenses'),
        headers: _headers,
        body: jsonEncode({
          'date': expense.date.toIso8601String(),
          'category': expense.category,
          'amount': expense.amount,
          'description': expense.description,
          'split_type': expense.splitType,
          'custom_splits': customSplitsJson,
        }),
      );

      print('Create group expense response status: ${response.statusCode}');
      print('Create group expense response body: ${response.body}');

      if (response.statusCode == 200) {
        return GroupExpense.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to create group expense: ${response.body}');
      }
    } catch (e) {
      print('Create group expense error: $e');
      rethrow;
    }
  }

  // Delete a group expense
  Future<void> deleteGroupExpense(int groupId, int expenseId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/groups/$groupId/expenses/$expenseId'),
      headers: _headers,
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to delete group expense: ${response.body}');
    }
  }

  Future<List<GroupMember>> getGroupMembers(int groupId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/groups/$groupId/members/'),  // Note the trailing slash
        headers: _headers,
      );

      print('Get group members response status: ${response.statusCode}');
      print('Get group members response body: ${response.body}');

      if (response.statusCode == 200) {
        List<dynamic> data = jsonDecode(response.body);
        return data.map((e) => GroupMember.fromJson(e)).toList();
      } else if (response.statusCode == 404) {
        // Return empty list instead of throwing error if group not found
        print('Group not found or no members');
        return [];
      } else {
        throw Exception('Failed to load group members: ${response.body}');
      }
    } catch (e) {
      print('Get group members error: $e');
      // Return empty list on error
      return [];
    }
  }
}