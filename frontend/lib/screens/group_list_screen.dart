import 'package:flutter/material.dart';
import 'package:intl/intl.dart'; // Add this line
import '../models/group.dart';
import '../services/api_service.dart';
import 'create_group_screen.dart';
import 'join_group_screen.dart';
import 'group_detail_screen.dart';

class GroupListScreen extends StatefulWidget {
  const GroupListScreen({Key? key}) : super(key: key);

  @override
  _GroupListScreenState createState() => _GroupListScreenState();
}

class _GroupListScreenState extends State<GroupListScreen> {
  final ApiService _apiService = ApiService();
  List<Group> _groups = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadGroups();
  }

  Future<void> _loadGroups() async {
    setState(() => _isLoading = true);
    try {
      final groups = await _apiService.getUserGroups();
      setState(() => _groups = groups);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading groups: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _navigateToCreateGroup() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CreateGroupScreen(
          onGroupCreated: _loadGroups,
        ),
      ),
    );
  }

  void _navigateToJoinGroup() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => JoinGroupScreen(
          onGroupJoined: _loadGroups,
        ),
      ),
    );
  }

  void _navigateToGroupDetail(Group group) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => GroupDetailScreen(group: group),
      ),
    );
  }

  Widget _buildGroupList() {
    if (_groups.isEmpty) {
      return const Center(child: Text('You are not a member of any groups.'));
    }

    return ListView.builder(
      itemCount: _groups.length,
      itemBuilder: (context, index) {
        final group = _groups[index];
        return ListTile(
          title: Text(group.name),
          subtitle: Text('Created on ${DateFormat('MMM dd, yyyy').format(group.createdAt)}'),
          onTap: () => _navigateToGroupDetail(group),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Your Groups'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadGroups,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildGroupList(),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          FloatingActionButton(
            onPressed: _navigateToCreateGroup,
            heroTag: 'createGroup',
            tooltip: 'Create Group',
            child: const Icon(Icons.group_add),
          ),
          const SizedBox(height: 16),
          FloatingActionButton(
            onPressed: _navigateToJoinGroup,
            heroTag: 'joinGroup',
            tooltip: 'Join Group',
            child: const Icon(Icons.group),
          ),
        ],
      ),
    );
  }
}
