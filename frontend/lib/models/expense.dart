class Expense {
  final int? id;
  final DateTime date;
  final String category;
  final double amount;
  final String description;
  final String paymentMethod;
  final int? userId;

  Expense({
    this.id,
    DateTime? date,
    required this.category,
    required this.amount,
    required this.description,
    required this.paymentMethod,
    this.userId,
  }) : date = date ?? DateTime.now();

  factory Expense.fromJson(Map<String, dynamic> json) {
    return Expense(
      id: json['id'],
      date: DateTime.parse(json['date']),
      category: json['category'],
      amount: double.parse(json['amount'].toString()),
      description: json['description'] ?? '',
      paymentMethod: json['payment_method'],
      userId: json['user_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date.toIso8601String(),  // Include date in JSON
      'category': category,
      'amount': amount,
      'description': description,
      'payment_method': paymentMethod,
    };
  }
}