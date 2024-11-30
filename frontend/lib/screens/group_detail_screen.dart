import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
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
  Map<int, String> _userNames = {};  // Cache for user names
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadGroupMembers();
    _loadGroupExpenses();
  }

  Future<void> _loadGroupMembers() async {
    try {
      final members = await _apiService.getGroupMembers(widget.group.id);
      setState(() {
        _userNames = {for (var member in members) member.id: member.name};
      });
    } catch (e) {
      print('Error loading group members: $e');
    }
  }

  Future<void> _loadGroupExpenses() async {
    setState(() => _isLoading = true);
    try {
      final expenses = await _apiService.getGroupExpenses(widget.group.id);
      setState(() => _expenses = expenses);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading expenses: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _deleteExpense(int expenseId) async {
    try {
      await _apiService.deleteGroupExpense(widget.group.id, expenseId);
      _loadGroupExpenses();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting expense: $e')),
        );
      }
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

  String _getUserName(int userId) {
    return _userNames[userId] ?? 'User $userId';
  }

  void _showExpenseDetails(GroupExpense expense) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Expense Details',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Text('Category: ${expense.category}'),
            if (expense.description.isNotEmpty)
              Text('Description: ${expense.description}'),
            Text('Total Amount: \$${expense.amount.toStringAsFixed(2)}'),
            Text('Split Type: ${expense.splitType.capitalize()}'),
            Text('Paid by: ${_getUserName(expense.paidBy)}'),
            const SizedBox(height: 8),
            const Divider(),
            const Text(
              'Split Details:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ...expense.splits.map(
              (split) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(_getUserName(split.userId)),
                    ),
                    Row(
                      children: [
                        Text(
                          '\$${split.amount.toStringAsFixed(2)}',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        if (split.paid)
                          const Padding(
                            padding: EdgeInsets.only(left: 8.0),
                            child: Icon(
                              Icons.check_circle,
                              color: Colors.green,
                              size: 16,
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
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
          confirmDismiss: (direction) async {
            return await showDialog(
              context: context,
              builder: (context) => AlertDialog(
                title: const Text('Delete Expense'),
                content: const Text('Are you sure you want to delete this expense?'),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(false),
                    child: const Text('Cancel'),
                  ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(true),
                    child: const Text('Delete'),
                  ),
                ],
              ),
            );
          },
          onDismissed: (direction) => _deleteExpense(expense.id),
          child: Card(
            margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            child: ListTile(
              title: Row(
                children: [
                  Text(expense.category),
                  const SizedBox(width: 8),
                  Text(
                    'by ${_getUserName(expense.paidBy)}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (expense.description.isNotEmpty) Text(expense.description),
                  Text(
                    DateFormat('MMM d, yyyy').format(expense.date),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  if (expense.userSplit != null)
                    Text(
                      'Your share: \$${expense.userSplit!.toStringAsFixed(2)}',
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
                    expense.splitType.capitalize(),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
              onTap: () => _showExpenseDetails(expense),
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