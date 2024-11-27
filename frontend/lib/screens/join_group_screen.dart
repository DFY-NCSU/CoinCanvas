import 'package:flutter/material.dart';
import 'package:intl/intl.dart'; // Add this line
import '../services/api_service.dart';
import '../models/group.dart';

class JoinGroupScreen extends StatefulWidget {
  final VoidCallback onGroupJoined;

  const JoinGroupScreen({Key? key, required this.onGroupJoined}) : super(key: key);

  @override
  _JoinGroupScreenState createState() => _JoinGroupScreenState();
}

class _JoinGroupScreenState extends State<JoinGroupScreen> {
  final _apiService = ApiService();
  final _searchController = TextEditingController();
  List<Group> _searchResults = [];
  bool _isLoading = false;

  Future<void> _searchGroups() async {
    setState(() => _isLoading = true);
    try {
      final groups = await _apiService.searchGroups(_searchController.text);
      setState(() => _searchResults = groups);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error searching groups: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _joinGroup(int groupId) async {
    setState(() => _isLoading = true);
    try {
      await _apiService.joinGroup(groupId);
      widget.onGroupJoined();
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error joining group: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Widget _buildSearchResults() {
    if (_searchResults.isEmpty) {
      return const Center(child: Text('No groups found.'));
    }

    return ListView.builder(
      shrinkWrap: true,
      itemCount: _searchResults.length,
      itemBuilder: (context, index) {
        final group = _searchResults[index];
        return ListTile(
          title: Text(group.name),
          subtitle: Text('Created on ${DateFormat('MMM dd, yyyy').format(group.createdAt)}'),
          trailing: ElevatedButton(
            onPressed: _isLoading ? null : () => _joinGroup(group.id),
            child: const Text('Join'),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Join Group'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text('Search for groups to join.', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            TextField(
              controller: _searchController,
              decoration: const InputDecoration(
                labelText: 'Group Name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _searchGroups,
              child: _isLoading ? const CircularProgressIndicator() : const Text('Search'),
            ),
            const SizedBox(height: 24),
            Expanded(child: _buildSearchResults()),
          ],
        ),
      ),
    );
  }
}
