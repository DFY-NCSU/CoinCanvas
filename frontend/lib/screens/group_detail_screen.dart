import 'package:flutter/material.dart';
import '../models/group.dart';
import '../models/group_expense.dart';
import '../services/api_service.dart';
import 'add_group_expense_screen.dart';

class GroupDetailScreen extends StatefulWidget {
  final Group group;

  const GroupDetailScreen({Key? key, required this.group}) : super(key: key);

  @override
  _GroupDetailScreenState createState() => _GroupDetailScreenState();
}

class _GroupDetailScreenState extends State<GroupDetailScreen> {
  final ApiService _apiService = ApiService();
  List<GroupExpense> _expenses = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadGroupExpenses();
  }

  Future<void> _loadGroupExpenses() async {
    setState(() => _isLoading = true);
    try {
      final expenses = await _apiService.getGroupExpenses(widget.group.id);
      setState(() => _expenses = expenses);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading expenses: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _navigateToAddExpense() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AddGroupExpenseScreen(
          groupId: widget.group.id,
          onExpenseAdded: _loadGroupExpenses,
        ),
      ),
    );
  }

  Future<void> _deleteExpense(int expenseId) async {
    setState(() => _isLoading = true);
    try {
      await _apiService.deleteGroupExpense(widget.group.id, expenseId);
      _loadGroupExpenses();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error deleting expense: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Widget _buildExpenseList() {
    if (_expenses.isEmpty) {
      return const Center(child: Text('No expenses in this group.'));
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
            child: const Icon(Icons.delete, color: Colors.white),
          ),
          direction: DismissDirection.endToStart,
          onDismissed: (direction) => _deleteExpense(expense.id),
          child: ListTile(
            title: Text(expense.category),
            subtitle: Text(expense.description),
            trailing: Text('\$${expense.amount.toStringAsFixed(2)}'),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.group.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadGroupExpenses,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildExpenseList(),
      floatingActionButton: FloatingActionButton(
        onPressed: _navigateToAddExpense,
        child: const Icon(Icons.add),
        tooltip: 'Add Expense',
      ),
    );
  }
}
