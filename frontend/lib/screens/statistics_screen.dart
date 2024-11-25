import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../models/expense.dart';
import '../services/api_service.dart';

class StatisticsScreen extends StatefulWidget {
  const StatisticsScreen({Key? key}) : super(key: key);

  @override
  _StatisticsScreenState createState() => _StatisticsScreenState();
}

class _StatisticsScreenState extends State<StatisticsScreen> {
  final ApiService _apiService = ApiService();
  List<Expense> _expenses = [];
  bool _isLoading = true;
  String _selectedTimeFrame = 'Month';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final expenses = await _apiService.getExpenses();
      setState(() => _expenses = expenses);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading statistics: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Statistics'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _buildTimeFrameSelector(),
                  const SizedBox(height: 24),
                  _buildPieChart(),
                  const SizedBox(height: 24),
                  _buildSummaryCards(),
                ],
              ),
            ),
    );
  }

  Widget _buildTimeFrameSelector() {
    return SegmentedButton<String>(
      segments: const [
        ButtonSegment(value: 'Week', label: Text('Week')),
        ButtonSegment(value: 'Month', label: Text('Month')),
        ButtonSegment(value: 'Year', label: Text('Year')),
      ],
      selected: {_selectedTimeFrame},
      onSelectionChanged: (Set<String> newSelection) {
        setState(() {
          _selectedTimeFrame = newSelection.first;
        });
      },
    );
  }

  Widget _buildPieChart() {
    if (_expenses.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text(
            'No expenses recorded yet',
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    final Map<String, double> categoryExpenses = {};
    for (var expense in _expenses) {
      categoryExpenses.update(
        expense.category,
        (value) => value + expense.amount,
        ifAbsent: () => expense.amount,
      );
    }

    final totalExpense = categoryExpenses.values.reduce((a, b) => a + b);

    return SizedBox(
      height: 300,
      child: PieChart(
        PieChartData(
          sections: categoryExpenses.entries.map((entry) {
            final percentage = (entry.value / totalExpense) * 100;
            return PieChartSectionData(
              color: _getCategoryColor(entry.key),
              value: entry.value,
              title: '${percentage.toStringAsFixed(1)}%',
              radius: 150,
              titleStyle: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            );
          }).toList(),
          sectionsSpace: 0,
        ),
      ),
    );
  }

  Widget _buildSummaryCards() {
    if (_expenses.isEmpty) return const SizedBox.shrink();

    final totalExpense = _expenses.fold<double>(
      0,
      (sum, expense) => sum + expense.amount,
    );
    final averageExpense = totalExpense / _expenses.length;
    final maxExpense = _expenses
        .map((e) => e.amount)
        .reduce((a, b) => a > b ? a : b);

    return Row(
      children: [
        _buildSummaryCard(
          'Total',
          '\$${totalExpense.toStringAsFixed(2)}',
          Icons.account_balance_wallet,
        ),
        _buildSummaryCard(
          'Average',
          '\$${averageExpense.toStringAsFixed(2)}',
          Icons.trending_up,
        ),
        _buildSummaryCard(
          'Highest',
          '\$${maxExpense.toStringAsFixed(2)}',
          Icons.arrow_upward,
        ),
      ],
    );
  }

  Widget _buildSummaryCard(String title, String value, IconData icon) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Icon(icon),
              const SizedBox(height: 8),
              Text(
                title,
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getCategoryColor(String category) {
    final colors = {
      'Food': Colors.red,
      'Transportation': Colors.blue,
      'Shopping': Colors.green,
      'Bills': Colors.orange,
      'Entertainment': Colors.purple,
      'Health': Colors.teal,
      'Education': Colors.indigo,
      'Other': Colors.grey,
    };
    return colors[category] ?? Colors.grey;
  }
}