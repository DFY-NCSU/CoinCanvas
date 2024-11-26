import 'package:flutter_test/flutter_test.dart';
import 'package:expense_tracker/models/expense.dart';

void main() {
  group('Expense Model Tests', () {
    test('Create Expense with all parameters', () {
      final now = DateTime.now();
      final expense = Expense(
        id: 1,
        date: now,
        category: 'Food',
        amount: 25.50,
        description: 'Lunch',
        paymentMethod: 'Credit Card',
        userId: 1,
      );

      expect(expense.id, equals(1));
      expect(expense.date, equals(now));
      expect(expense.category, equals('Food'));
      expect(expense.amount, equals(25.50));
      expect(expense.description, equals('Lunch'));
      expect(expense.paymentMethod, equals('Credit Card'));
      expect(expense.userId, equals(1));
    });

    test('Create Expense with minimum required parameters', () {
      final expense = Expense(
        category: 'Food',
        amount: 25.50,
        description: 'Lunch',
        paymentMethod: 'Credit Card',
      );

      expect(expense.id, isNull);
      expect(expense.date, isA<DateTime>());
      expect(expense.category, equals('Food'));
      expect(expense.amount, equals(25.50));
      expect(expense.description, equals('Lunch'));
      expect(expense.paymentMethod, equals('Credit Card'));
      expect(expense.userId, isNull);
    });

    test('Create Expense from JSON', () {
      final json = {
        'id': 1,
        'date': '2024-11-25T10:00:00.000Z',
        'category': 'Food',
        'amount': 25.50,
        'description': 'Lunch',
        'payment_method': 'Credit Card',
        'user_id': 1,
      };

      final expense = Expense.fromJson(json);

      expect(expense.id, equals(1));
      expect(expense.date.toUtc().toIso8601String(), equals('2024-11-25T10:00:00.000Z'));
      expect(expense.category, equals('Food'));
      expect(expense.amount, equals(25.50));
      expect(expense.description, equals('Lunch'));
      expect(expense.paymentMethod, equals('Credit Card'));
      expect(expense.userId, equals(1));
    });

    test('Convert Expense to JSON', () {
      final date = DateTime.utc(2024, 11, 25, 10);
      final expense = Expense(
        id: 1,
        date: date,
        category: 'Food',
        amount: 25.50,
        description: 'Lunch',
        paymentMethod: 'Credit Card',
        userId: 1,
      );

      final json = expense.toJson();

      expect(json['date'], equals(date.toIso8601String()));
      expect(json['category'], equals('Food'));
      expect(json['amount'], equals(25.50));
      expect(json['description'], equals('Lunch'));
      expect(json['payment_method'], equals('Credit Card'));
      // id and user_id should not be included in toJson output
      expect(json.containsKey('id'), isFalse);
      expect(json.containsKey('user_id'), isFalse);
    });

    test('Create Expense from JSON with missing optional fields', () {
      final json = {
        'date': '2024-11-25T10:00:00.000Z',
        'category': 'Food',
        'amount': 25.50,
        'payment_method': 'Credit Card',
      };

      final expense = Expense.fromJson(json);

      expect(expense.id, isNull);
      expect(expense.description, equals(''));
      expect(expense.userId, isNull);
    });

    test('Handle different amount formats in JSON', () {
      final jsonWithInt = {
        'date': '2024-11-25T10:00:00.000Z',
        'category': 'Food',
        'amount': 25,
        'payment_method': 'Credit Card',
      };

      final jsonWithString = {
        'date': '2024-11-25T10:00:00.000Z',
        'category': 'Food',
        'amount': '25.50',
        'payment_method': 'Credit Card',
      };

      final expenseFromInt = Expense.fromJson(jsonWithInt);
      final expenseFromString = Expense.fromJson(jsonWithString);

      expect(expenseFromInt.amount, equals(25.0));
      expect(expenseFromString.amount, equals(25.50));
    });

    test('Throws FormatException when amount is invalid', () {
      final json = {
        'date': '2024-11-25T10:00:00.000Z',
        'category': 'Food',
        'amount': 'invalid',
        'payment_method': 'Credit Card',
      };

      expect(() => Expense.fromJson(json), throwsA(isA<FormatException>()));
    });

    test('Throws FormatException when date is invalid', () {
      final json = {
        'date': 'invalid-date',
        'category': 'Food',
        'amount': 25.50,
        'payment_method': 'Credit Card',
      };

      expect(() => Expense.fromJson(json), throwsA(isA<FormatException>()));
    });
  });
}