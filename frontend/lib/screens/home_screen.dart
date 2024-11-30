import 'package:flutter/material.dart';
import '../models/expense.dart';
import '../screens/add_expense_screen.dart';
import '../screens/login_screen.dart';
import '../screens/statistics_screen.dart';
import '../services/api_service.dart';
import 'package:intl/intl.dart';
import 'group_list_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  List<Expense> _expenses = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadExpenses();
  }

  Future<void> _loadExpenses() async {
    if (!mounted) return;
    
    setState(() => _isLoading = true);
    try {
      if (!_apiService.isAuthenticated) {
        _navigateToLogin();
        return;
      }
      
      final expenses = await _apiService.getExpenses();
      if (mounted) {
        setState(() => _expenses = expenses);
      }
    } catch (e) {
      if (mounted) {
        if (e.toString().contains('Unauthorized')) {
          _navigateToLogin();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error loading expenses: $e')),
          );
        }
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _navigateToLogin() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => LoginScreen(
          onLoginSuccess: () {
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (context) => const HomeScreen()),
            );
          },
        ),
      ),
    );
  }

  void _showAddExpenseScreen() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AddExpenseScreen(
          onExpenseAdded: () {
            _loadExpenses();
          },
        ),
      ),
    );
  }

  void _showStatisticsScreen() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const StatisticsScreen(),
      ),
    );
  }

  void _handleLogout() {
    _apiService.logout();
    _navigateToLogin();
  }

  Color _getCategoryColor(String category) {
    final colors = {
      'Food': Colors.red,
      'Transportation': Colors.blue,
      'Shopping': Colors.green,
      'Bills': Colors.orange,
      'Entertainment': Colors.purple,
      'Health': Colors.teal,
      'Education': Colors.indigo,
      'Other': Colors.grey,
    };
    return colors[category] ?? Colors.grey;
  }

  IconData _getCategoryIcon(String category) {
    final icons = {
      'Food': Icons.restaurant,
      'Transportation': Icons.directions_car,
      'Shopping': Icons.shopping_cart,
      'Bills': Icons.receipt,
      'Entertainment': Icons.movie,
      'Health': Icons.health_and_safety,
      'Education': Icons.school,
      'Other': Icons.more_horiz,
    };
    return icons[category] ?? Icons.more_horiz;
  }

  Future<void> _deleteExpense(int id) async {
    try {
      await _apiService.deleteExpense(id);
      _loadExpenses();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Expense deleted successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting expense: $e')),
        );
      }
    }
  }

  Widget _buildExpenseList() {
    if (_expenses.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.receipt_long,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              'No expenses yet',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: _showAddExpenseScreen,
              icon: const Icon(Icons.add),
              label: const Text('Add Your First Expense'),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: _expenses.length,
      itemBuilder: (context, index) {
        final expense = _expenses[index];
        return Dismissible(
          key: Key(expense.id.toString()),
          background: Container(
            color: Colors.red,
            alignment: Alignment.centerRight,
            padding: const EdgeInsets.only(right: 16),
            child: const Icon(
              Icons.delete,
              color: Colors.white,
            ),
          ),
          direction: DismissDirection.endToStart,
          onDismissed: (direction) {
            if (expense.id != null) {
              _deleteExpense(expense.id!);
            }
          },
          child: Card(
            margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: _getCategoryColor(expense.category).withOpacity(0.2),
                child: Icon(
                  _getCategoryIcon(expense.category),
                  color: _getCategoryColor(expense.category),
                ),
              ),
              title: Text(
                expense.category,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (expense.description.isNotEmpty)
                    Text(expense.description),
                  Text(
                    DateFormat('MMM dd, yyyy').format(expense.date),
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              trailing: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '\$${expense.amount.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  Text(
                    expense.paymentMethod,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CoinCanvas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadExpenses,
            tooltip: 'Refresh',
          ),
          IconButton(
            icon: const Icon(Icons.bar_chart),
            onPressed: _showStatisticsScreen,
            tooltip: 'Statistics',
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _handleLogout,
            tooltip: 'Logout',
          ),
          IconButton(
            icon: const Icon(Icons.group),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const GroupListScreen()),
              );
            },
            tooltip: 'Groups',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildExpenseList(),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddExpenseScreen,
        child: const Icon(Icons.add),
        tooltip: 'Add Expense',
      ),
    );
  }
}