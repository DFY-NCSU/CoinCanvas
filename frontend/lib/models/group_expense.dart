class GroupExpense {
  final int id;
  final int? groupId;
  final int paidBy;
  final DateTime date;
  final String category;
  final double amount;
  final String description;
  final String splitType;
  final Map<int, double>? customSplits;
  final List<ExpenseSplit> splits;
  final double? userSplit;  // Amount for current user
  final bool? isPaidByUser;

  GroupExpense({
    required this.id,
    required this.groupId,
    required this.paidBy,
    required this.date,
    required this.category,
    required this.amount,
    required this.description,
    required this.splitType,
    this.customSplits,
    required this.splits,
    this.userSplit,
    this.isPaidByUser,
  });

  factory GroupExpense.fromJson(Map<String, dynamic> json) {
    return GroupExpense(
      id: json['id'],
      groupId: json['group_id'],
      paidBy: json['paid_by'],
      date: DateTime.parse(json['date']),
      category: json['category'],
      amount: double.parse(json['amount'].toString()),
      description: json['description'] ?? '',
      splitType: json['split_type'],
      customSplits: json['custom_splits'] != null
          ? Map<int, double>.from(json['custom_splits'])
          : null,
      splits: (json['splits'] as List<dynamic>)
          .map((e) => ExpenseSplit.fromJson(e))
          .toList(),
      userSplit: json['user_split']?.toDouble(),
      isPaidByUser: json['is_paid_by_user'],
    );
  }
}

class ExpenseSplit {
  final int id;
  final int expenseId;
  final int userId;
  final double amount;
  final bool paid;

  ExpenseSplit({
    required this.id,
    required this.expenseId,
    required this.userId,
    required this.amount,
    required this.paid,
  });

  factory ExpenseSplit.fromJson(Map<String, dynamic> json) {
    return ExpenseSplit(
      id: json['id'],
      expenseId: json['expense_id'],
      userId: json['user_id'],
      amount: double.parse(json['amount'].toString()),
      paid: json['paid'],
    );
  }
}
