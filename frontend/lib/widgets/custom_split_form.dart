// widgets/custom_split_form.dart
import 'package:flutter/material.dart';
import '../models/group_member.dart';

class CustomSplitForm extends StatefulWidget {
  final List<GroupMember> members;
  final Function(Map<int, double>) onSplitsChanged;

  const CustomSplitForm({
    Key? key,
    required this.members,
    required this.onSplitsChanged,
  }) : super(key: key);

  @override
  _CustomSplitFormState createState() => _CustomSplitFormState();
}

class _CustomSplitFormState extends State<CustomSplitForm> {
  late List<TextEditingController> _controllers;
  double _totalPercentage = 0.0;

  @override
  void initState() {
    super.initState();
    _controllers = List.generate(
      widget.members.length,
      (index) => TextEditingController(text: '0.0'),
    );
    _updateTotalPercentage();
  }

  void _updateTotalPercentage() {
    if (widget.members.isEmpty) {
      _totalPercentage = 0.0;
      return;
    }

    _totalPercentage = _controllers.fold<double>(
      0.0,
      (sum, controller) => sum + (double.tryParse(controller.text) ?? 0.0),
    );

    final splits = Map<int, double>.fromEntries(
      widget.members.asMap().entries.map(
            (e) => MapEntry(
              e.value.id,
              double.tryParse(_controllers[e.key].text) ?? 0.0,
            ),
          ),
    );

    widget.onSplitsChanged(splits);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.members.isEmpty) {
      return const Center(
        child: Text('No members in this group yet.'),
      );
    }

    return Column(
      children: [
        ...widget.members.asMap().entries.map(
              (entry) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: Text(widget.members[entry.key].name),
                    ),
                    Expanded(
                      flex: 3,
                      child: TextFormField(
                        controller: _controllers[entry.key],
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          suffix: Text('%'),
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (value) {
                          setState(() {
                            _updateTotalPercentage();
                          });
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
        const SizedBox(height: 16),
        Text(
          'Total: ${_totalPercentage.toStringAsFixed(1)}%',
          style: TextStyle(
            color: (_totalPercentage - 100.0).abs() < 0.01
                ? Colors.green
                : Colors.red,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }
}