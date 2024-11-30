import 'package:flutter/material.dart';
import 'package:dart_openai/dart_openai.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../models/expense.dart';
import '../config/api_config.dart';
import '../extensions/iterable_extensions.dart';

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
    // Add system message (invisible to user)
    _messages.add({
      'role': 'system',
      'content': '''You are an AI financial advisor with access to the following expense data:

$expenseSummary

Your role is to:
1. Analyze spending patterns and trends
2. Identify potential areas for savings
3. Provide actionable financial advice
4. Highlight unusual spending patterns
5. Make budget recommendations
6. Answer questions about the expense data
7. Calculate financial metrics when asked

Use Markdown formatting in your responses:
- Use **bold** for important numbers and key insights
- Use bullet points and numbered lists for multiple items
- Use `code` formatting for specific amounts or percentages
- Use ### for section headers when organizing long responses
- Use > for important quotes or key takeaways
- Use tables when comparing data

Keep responses concise but informative. When making observations, explain the reasoning behind your insights. If asked about timeframes or categories not present in the data, politely explain what data is available.

When providing monetary values, always use the \$ symbol and format numbers with two decimal places.'''
    });

    // Add welcome message from AI (visible to user)
    _messages.add({
      'role': 'assistant',
      'content': '''### 👋 Welcome to Your Personal Finance Assistant!

I'm here to help you analyze your expenses and provide financial insights. I can help you with:

- Analyzing spending patterns
- Identifying saving opportunities
- Tracking expenses by category
- Comparing monthly spending
- Providing budget recommendations

Try asking me questions like:
- "What's my total spending?"
- "Which category do I spend most on?"
- "How has my spending changed over time?"
- "Any suggestions for saving money?"
- "What's my monthly spending trend?"

Feel free to ask any questions about your expenses!'''
    });
  }

  String _createExpenseSummary() {
    final expenses = widget.expenses;
    if (expenses.isEmpty) {
      return "There are no expenses recorded yet.";
    }

    // Group expenses by category with descriptions
    final categoryExpensesWithDetails = <String, List<Map<String, dynamic>>>{};
    final monthlyExpenses = <String, double>{};
    DateTime? earliestDate;
    DateTime? latestDate;
    
    for (var expense in expenses) {
      // Category grouping with details
      categoryExpensesWithDetails.update(
        expense.category,
        (value) => [...value, {
          'amount': expense.amount,
          'date': expense.date,
          'description': expense.description,
          'payment_method': expense.paymentMethod,
        }],
        ifAbsent: () => [{
          'amount': expense.amount,
          'date': expense.date,
          'description': expense.description,
          'payment_method': expense.paymentMethod,
        }],
      );

      // Monthly grouping
      final monthKey = '${expense.date.year}-${expense.date.month.toString().padLeft(2, '0')}';
      monthlyExpenses.update(
        monthKey,
        (value) => value + expense.amount,
        ifAbsent: () => expense.amount,
      );

      // Track date range
      if (earliestDate == null || expense.date.isBefore(earliestDate)) {
        earliestDate = expense.date;
      }
      if (latestDate == null || expense.date.isAfter(latestDate)) {
        latestDate = expense.date;
      }
    }

    final totalExpense = expenses.fold<double>(
      0,
      (sum, expense) => sum + expense.amount,
    );

    // Calculate statistics
    final averageExpense = totalExpense / expenses.length;
    final highestExpense = expenses.map((e) => e.amount).reduce((a, b) => a > b ? a : b);
    final lowestExpense = expenses.map((e) => e.amount).reduce((a, b) => a < b ? a : b);

    final summary = StringBuffer();
    summary.writeln('### Expense Analysis Summary');
    summary.writeln('Period: ${earliestDate?.toString().split(' ')[0]} to ${latestDate?.toString().split(' ')[0]}');
    summary.writeln('Total number of expenses: ${expenses.length}');
    summary.writeln('Total expenditure: \$${totalExpense.toStringAsFixed(2)}');
    summary.writeln('Average expense: \$${averageExpense.toStringAsFixed(2)}');
    summary.writeln('Highest single expense: \$${highestExpense.toStringAsFixed(2)}');
    summary.writeln('Lowest single expense: \$${lowestExpense.toStringAsFixed(2)}');
    
    summary.writeln('\n### Category Breakdown with Details');
    categoryExpensesWithDetails.forEach((category, expenseList) {
      final totalCategoryAmount = expenseList.fold<double>(
        0,
        (sum, expense) => sum + expense['amount'] as double,
      );
      final percentage = (totalCategoryAmount / totalExpense * 100).toStringAsFixed(1);
      
      summary.writeln('\n#### $category');
      summary.writeln('Total: \$${totalCategoryAmount.toStringAsFixed(2)} ($percentage%)');
      summary.writeln('Details:');
      
      // Sort expenses by date (most recent first)
      expenseList.sort((a, b) => (b['date'] as DateTime).compareTo(a['date'] as DateTime));
      
      for (var expense in expenseList) {
        final date = (expense['date'] as DateTime).toString().split(' ')[0];
        final amount = (expense['amount'] as double).toStringAsFixed(2);
        final description = expense['description'] as String;
        final paymentMethod = expense['payment_method'] as String;
        summary.writeln('- $date: \$$amount - $description (Paid via $paymentMethod)');
      }
    });

    summary.writeln('\n### Monthly Spending');
    monthlyExpenses.entries.toList()
      ..sort((a, b) => a.key.compareTo(b.key))
      ..forEach((entry) {
        summary.writeln('${entry.key}: \$${entry.value.toStringAsFixed(2)}');
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
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

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
                    color: isUser 
                        ? Theme.of(context).primaryColor 
                        : isDarkMode 
                            ? Colors.grey[800] // Dark mode AI message background
                            : Colors.grey[300], // Light mode AI message background
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: isUser 
                      ? Text(
                          message['content']!,
                          style: const TextStyle(color: Colors.white),
                        )
                      : MarkdownBody(
                          data: message['content']!,
                          styleSheet: MarkdownStyleSheet(
                            p: TextStyle(
                              color: isDarkMode ? Colors.white : Colors.black,
                            ),
                            strong: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: isDarkMode ? Colors.white : Colors.black,
                            ),
                            code: TextStyle(
                              backgroundColor: isDarkMode 
                                  ? Colors.grey[900]
                                  : Colors.grey[200],
                              color: isDarkMode ? Colors.white : Colors.black,
                              fontFamily: 'monospace',
                            ),
                            codeblockDecoration: BoxDecoration(
                              color: isDarkMode 
                                  ? Colors.grey[900]
                                  : Colors.grey[200],
                              borderRadius: BorderRadius.circular(4),
                            ),
                            blockquote: TextStyle(
                              color: isDarkMode ? Colors.white70 : Colors.black87,
                              fontStyle: FontStyle.italic,
                            ),
                            h3: TextStyle(
                              color: isDarkMode ? Colors.white : Colors.black,
                              fontWeight: FontWeight.bold,
                            ),
                            listBullet: TextStyle(
                              color: isDarkMode ? Colors.white : Colors.black,
                            ),
                          ),
                          selectable: true,
                          onTapLink: (text, href, title) {
                            // Handle link taps if needed
                          },
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