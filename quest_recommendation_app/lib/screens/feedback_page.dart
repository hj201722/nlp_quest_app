import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class FeedbackPage extends StatefulWidget {
  @override
  _FeedbackPageState createState() => _FeedbackPageState();
}

class _FeedbackPageState extends State<FeedbackPage> {
  final TextEditingController _feedbackController = TextEditingController();
  String? _selectedQuest;
  List<dynamic> _quests = [];

  @override
  void initState() {
    super.initState();
    _fetchQuests();
  }

  Future<void> _fetchQuests() async {
    final response = await http.get(
      Uri.parse('http://127.0.0.1:8000/api/available_quests/'), // 엔드포인트 확인
    );

    if (response.statusCode == 200) {
      setState(() {
        _quests = json.decode(utf8.decode(response.bodyBytes));
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text('퀘스트 목록을 불러오는 데 실패했습니다: ${response.statusCode}')),
      );
    }
  }

  Future<void> _submitFeedback() async {
    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/api/feedback/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'quest': _selectedQuest,
        'feedback_text': _feedbackController.text,
      }),
    );

    if (response.statusCode == 201) {
      Navigator.of(context).pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('피드백 제출에 실패했습니다: ${response.body}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('피드백 작성'),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            DropdownButtonFormField<String>(
              items: _quests.map((quest) {
                return DropdownMenuItem<String>(
                  value: quest['quest_id'],
                  child: Text(quest['quest_name']),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedQuest = value;
                });
              },
              decoration: InputDecoration(labelText: '퀘스트 선택'),
            ),
            TextField(
              controller: _feedbackController,
              decoration: InputDecoration(labelText: '피드백 제출'),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _submitFeedback,
              child: Text('제출'),
            ),
          ],
        ),
      ),
    );
  }
}
