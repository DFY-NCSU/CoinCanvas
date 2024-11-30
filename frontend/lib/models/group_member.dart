class GroupMember {
  final int id;
  final String name;
  final String email;
  double percentage;

  GroupMember({
    required this.id,
    required this.name,
    required this.email,
    this.percentage = 0.0,
  });

  factory GroupMember.fromJson(Map<String, dynamic> json) {
    return GroupMember(
      id: json['id'],
      name: json['full_name'] ?? json['name'] ?? 'Unknown',
      email: json['email'] ?? '',
      percentage: 0.0,
    );
  }
}