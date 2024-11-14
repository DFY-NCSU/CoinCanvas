class Expense {
  final int? id;
  final DateTime date;
  final String category;
  final double amount;
  final String description;
  final String paymentMethod;

  Expense({
    this.id,
    required this.date,
    required this.category,
    required this.amount,
    required this.description,
    required this.paymentMethod,
  });

  factory Expense.fromJson(Map<String, dynamic> json) {
    return Expense(
      id: json['id'],
      date: DateTime.parse(json['date']),
      category: json['category'],
      amount: double.parse(json['amount'].toString()),
      description: json['description'] ?? '',
      paymentMethod: json['payment_method'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': date.toIso8601String(),
      'category': category,
      'amount': amount,
      'description': description,
      'payment_method': paymentMethod,
    };
  }
}