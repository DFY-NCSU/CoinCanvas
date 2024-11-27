import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/expense.dart';

class AIService {
  static final AIService _instance = AIService._internal();
  factory AIService() => _instance;
  AIService._internal();

  static const String baseUrl = 'https://api.openai.com/v1/chat/completions';
  static const String apiKey = 'you api key'; // Replace with your API key

  Future<String> getExpenseAnalysis(List<Expense> expenses) async {
    try {
      final totalByCategory = <String, double>{};
      for (var expense in expenses) {
        totalByCategory.update(
          expense.category,
          (value) => value + expense.amount,
          ifAbsent: () => expense.amount,
        );
      }

      final expenseSummary = totalByCategory.entries
          .map((e) => "${e.key}: \$${e.value.toStringAsFixed(2)}")
          .join(", ");

      final messages = [
        {
          "role": "system",
          "content": "You are a financial advisor analyzing expense patterns."
        },
        {
          "role": "user",
          "content": """
          Here are my expenses by category: $expenseSummary.
          Please analyze my spending patterns and provide specific suggestions for better financial management.
          Focus on:
          1. Areas where I might be overspending
          2. Potential savings opportunities
          3. Budgeting recommendations
          4. General financial advice based on the spending pattern
          """
        }
      ];

      final response = await http.post(
        Uri.parse(baseUrl),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          "model": "gpt-4",
          "messages": messages,
          "temperature": 0.7,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['choices'][0]['message']['content'];
      } else {
        throw Exception('Failed to get AI analysis');
      }
    } catch (e) {
      return "Error getting AI analysis: $e";
    }
  }

  Future<String> chatWithAI(String userMessage, List<Expense> expenses) async {
    try {
      final totalByCategory = <String, double>{};
      for (var expense in expenses) {
        totalByCategory.update(
          expense.category,
          (value) => value + expense.amount,
          ifAbsent: () => expense.amount,
        );
      }

      final expenseSummary = totalByCategory.entries
          .map((e) => "${e.key}: \$${e.value.toStringAsFixed(2)}")
          .join(", ");

      final messages = [
        {
          "role": "system",
          "content": """
          You are a financial advisor with access to the user's expense data.
          Current expense summary: $expenseSummary
          """
        },
        {
          "role": "user",
          "content": userMessage
        }
      ];

      final response = await http.post(
        Uri.parse(baseUrl),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          "model": "gpt-4o-mini",
          "messages": messages,
          "temperature": 0.7,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['choices'][0]['message']['content'];
      } else {
        throw Exception('Failed to get AI response');
      }
    } catch (e) {
      return "Error getting AI response: $e";
    }
  }
}