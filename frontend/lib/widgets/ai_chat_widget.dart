import 'package:flutter/material.dart';
import 'package:dart_openai/dart_openai.dart';
import '../models/expense.dart';
import '../config/api_config.dart';

class AIChatWidget extends StatefulWidget {
  final List<Expense> expenses;

  const AIChatWidget({Key? key, required this.expenses}) : super(key: key);

  @override
  _AIChatWidgetState createState() => _AIChatWidgetState();
}

class _AIChatWidgetState extends State<AIChatWidget> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, String>> _messages = [];
  bool _isTyping = false;

  @override
  void initState() {
    super.initState();
    OpenAI.apiKey = ApiConfig.openAiKey;
    _initializeChat();
  }

  void _initializeChat() {
    final expenseSummary = _createExpenseSummary();
    _messages.add({
      'role': 'system',
      'content': '''You are a financial advisor AI assistant. You have access to the following expense data:
$expenseSummary

Analyze this data and provide insights when asked. Be concise but informative.
Focus on providing actionable financial advice and insights.'''
    });
  }

  String _createExpenseSummary() {
    final expenses = widget.expenses;
    final categoryExpenses = <String, double>{};
    
    for (var expense in expenses) {
      categoryExpenses.update(
        expense.category,
        (value) => value + expense.amount,
        ifAbsent: () => expense.amount,
      );
    }

    final totalExpense = expenses.fold<double>(
      0,
      (sum, expense) => sum + expense.amount,
    );

    final summary = StringBuffer();
    summary.writeln('Total Expenses: \$${totalExpense.toStringAsFixed(2)}');
    summary.writeln('\nBreakdown by Category:');
    
    categoryExpenses.forEach((category, amount) {
      final percentage = (amount / totalExpense * 100).toStringAsFixed(1);
      summary.writeln('$category: \$${amount.toStringAsFixed(2)} ($percentage%)');
    });

    return summary.toString();
  }

  Future<void> _handleSubmit(String text) async {
    if (text.trim().isEmpty) return;

    setState(() {
      _messages.add({'role': 'user', 'content': text});
      _messageController.clear();
      _isTyping = true;
    });

    try {
      final modelMessages = _messages.map((m) {
        return OpenAIChatCompletionChoiceMessageModel(
          role: m['role'] == 'user' 
              ? OpenAIChatMessageRole.user
              : m['role'] == 'assistant'
                  ? OpenAIChatMessageRole.assistant
                  : OpenAIChatMessageRole.system,
          content: [
            OpenAIChatCompletionChoiceMessageContentItemModel.text(m['content']!),
          ],
        );
      }).toList();

      final chatCompletion = await OpenAI.instance.chat.create(
        model: 'gpt-3.5-turbo',
        messages: modelMessages,
      );

      if (chatCompletion.choices.isNotEmpty) {
        final content = chatCompletion.choices.first.message.content;
        final responseContent = content != null 
            ? content.whereType<OpenAIChatCompletionChoiceMessageContentItemModel>()
                .map((item) => item.text)
                .join(' ')
            : 'No response from AI';

        setState(() {
          _messages.add({
            'role': 'assistant',
            'content': responseContent,
          });
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isTyping = false);
      }
    }
  }

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(8),
            itemCount: _messages.length,
            itemBuilder: (context, index) {
              final message = _messages[index];
              // Skip showing system messages
              if (message['role'] == 'system') return const SizedBox.shrink();
              
              final isUser = message['role'] == 'user';

              return Align(
                alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                  padding: const EdgeInsets.all(12),
                  constraints: BoxConstraints(
                    maxWidth: MediaQuery.of(context).size.width * 0.8,
                  ),
                  decoration: BoxDecoration(
                    color: isUser ? Theme.of(context).primaryColor : Colors.grey[300],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    message['content']!,
                    style: TextStyle(
                      color: isUser ? Colors.white : Colors.black,
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        if (_isTyping)
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: const [
                Text('AI is typing...'),
                SizedBox(width: 8),
                SizedBox(
                  width: 12,
                  height: 12,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ],
            ),
          ),
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _messageController,
                  decoration: InputDecoration(
                    hintText: 'Ask about your expenses...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(24),
                    ),
                    filled: true,
                  ),
                  onSubmitted: _handleSubmit,
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.send),
                onPressed: () => _handleSubmit(_messageController.text),
              ),
            ],
          ),
        ),
      ],
    );
  }
}