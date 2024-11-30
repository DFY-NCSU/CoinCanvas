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
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(expense.description),
                const SizedBox(height: 4),
                Text(
                  'Your share: \$${expense.userSplit?.toStringAsFixed(2) ?? "0.00"}',
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.secondary,
                    fontWeight: FontWeight.bold,
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
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  expense.splitType,
                  style: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            onTap: () => _showExpenseDetails(expense),
          ),
        );
      },
    );
  }

  void _showExpenseDetails(GroupExpense expense) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Expense Details',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Text('Category: ${expense.category}'),
            Text('Description: ${expense.description}'),
            Text('Amount: \$${expense.amount.toStringAsFixed(2)}'),
            Text('Split Type: ${expense.splitType}'),
            const SizedBox(height: 8),
            const Text(
              'Splits:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            ...expense.splits.map(
              (split) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('User ${split.userId}'),
                    Text('\$${split.amount.toStringAsFixed(2)}'),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
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
