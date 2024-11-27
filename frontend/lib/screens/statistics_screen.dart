import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
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

  List<Expense> _getFilteredExpenses() {
    final now = DateTime.now();
    final filteredExpenses = _expenses.where((expense) {
      final expenseDate = expense.date;
      switch (_selectedTimeFrame) {
        case 'Week':
          // Get the start of the current week (Monday)
          final startOfWeek = now.subtract(Duration(days: now.weekday - 1));
          final startOfWeekDate = DateTime(
            startOfWeek.year, 
            startOfWeek.month, 
            startOfWeek.day,
          );
          return expenseDate.isAfter(startOfWeekDate.subtract(const Duration(days: 1))) &&
                 expenseDate.isBefore(now.add(const Duration(days: 1)));
        
        case 'Month':
          // Get expenses from the current month
          return expenseDate.year == now.year && 
                 expenseDate.month == now.month;
        
        case 'Year':
          // Get expenses from the current year
          return expenseDate.year == now.year;
        
        default:
          return true;
      }
    }).toList();

    return filteredExpenses;
  }

  Map<String, double> _getCategoryExpenses() {
    final filteredExpenses = _getFilteredExpenses();
    final categoryExpenses = <String, double>{};
    
    for (var expense in filteredExpenses) {
      categoryExpenses.update(
        expense.category,
        (value) => value + expense.amount,
        ifAbsent: () => expense.amount,
      );
    }
    
    return categoryExpenses;
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
    final categoryExpenses = _getCategoryExpenses();
    
    if (categoryExpenses.isEmpty) {
      return SizedBox(
        height: 300,
        child: Center(
          child: Text(
            'No expenses in selected ${_selectedTimeFrame.toLowerCase()}',
            style: Theme.of(context).textTheme.titleMedium,
          ),
        ),
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
              title: '${percentage.toStringAsFixed(1)}%\n${entry.key}',
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
    final filteredExpenses = _getFilteredExpenses();
    
    if (filteredExpenses.isEmpty) {
      return const SizedBox.shrink();
    }

    final totalExpense = filteredExpenses.fold<double>(
      0,
      (sum, expense) => sum + expense.amount,
    );
    final averageExpense = totalExpense / filteredExpenses.length;
    final maxExpense = filteredExpenses
        .map((e) => e.amount)
        .reduce((a, b) => a > b ? a : b);

    return Column(
      children: [
        Text(
          'Summary for current ${_selectedTimeFrame.toLowerCase()}',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 16),
        Row(
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
}

class _StatisticsScreenState extends State<StatisticsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Statistics & Analysis'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Statistics'),
            Tab(text: 'AI Analysis'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // First tab - Statistics
          _isLoading
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
          
          // Second tab - AI Chat
          _isLoading
              ? const Center(child: CircularProgressIndicator())
              : AIChatWidget(expenses: _expenses),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
}