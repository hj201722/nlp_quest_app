import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class QuestProvidePage extends StatefulWidget {
  @override
  _QuestProvidePageState createState() => _QuestProvidePageState();
}

class _QuestProvidePageState extends State<QuestProvidePage> {
  final TextEditingController _activityController = TextEditingController();
  final TextEditingController _preferenceController = TextEditingController();
  final TextEditingController _ageGroupController = TextEditingController();
  final TextEditingController _genderController = TextEditingController();
  final TextEditingController _categoryController = TextEditingController();

  List<dynamic> _recommendedQuests = [];
  int? _selectedQuestIndex;

  Future<void> _getRecommendation() async {
    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/api/recommend_quest/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'activity': _activityController.text,
        'preference': _preferenceController.text,
        'age_group': _ageGroupController.text,
        'gender': _genderController.text,
        'category': _categoryController.text,
      }),
    );

    if (response.statusCode == 200) {
      // UTF-8로 디코드하고 JSON 파싱
      final responseData = jsonDecode(utf8.decode(response.bodyBytes));
      setState(() {
        if (responseData.containsKey('recommended_quests')) {
          _recommendedQuests = responseData['recommended_quests'];
          _selectedQuestIndex = null;
        } else {
          _recommendedQuests = [];
        }
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('추천을 받지 못했습니다. 다시 시도해주세요.')),
      );
    }
  }

  void _selectQuest(int index) {
    setState(() {
      _selectedQuestIndex = index;
    });
  }

  void _createQuest() {
    if (_selectedQuestIndex != null) {
      final selectedQuest = _recommendedQuests[_selectedQuestIndex!];
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => QuestDetailPage(quest: selectedQuest),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('퀘스트를 선택해주세요.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('퀘스트 제공 페이지'),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '퀘스트 추천을 받기 위한 정보를 입력해주세요:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            TextField(
              controller: _activityController,
              decoration: InputDecoration(
                labelText: '어떤 활동을 찾고 계신가요? 예를 들어, 야외 활동, 예술 감상 등',
              ),
            ),
            TextField(
              controller: _preferenceController,
              decoration: InputDecoration(
                labelText: '활동 선호도: 집에서 조용히 vs. 바깥에서 활동적으로',
              ),
            ),
            TextField(
              controller: _ageGroupController,
              decoration: InputDecoration(
                labelText: '연령대는 어떻게 되나요? 예: 초등학생, 중학생',
              ),
            ),
            TextField(
              controller: _genderController,
              decoration: InputDecoration(
                labelText: '성별은 어떻게 되나요? 예: 남성, 여성',
              ),
            ),
            TextField(
              controller: _categoryController,
              decoration: InputDecoration(
                labelText: '선호하는 카테고리는 무엇인가요? 예: 스포츠, 문화',
              ),
            ),
            SizedBox(height: 20),
            Center(
              child: ElevatedButton(
                onPressed: _getRecommendation,
                child: Text('추천 받기'),
              ),
            ),
            SizedBox(height: 20),
            if (_recommendedQuests.isNotEmpty)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '추천 퀘스트:',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 10),
                  ..._recommendedQuests.asMap().entries.map((entry) {
                    int idx = entry.key;
                    var quest = entry.value;
                    return ListTile(
                      title: Text(quest['quest_name']),
                      subtitle: Text(quest['description']),
                      leading: Radio(
                        value: idx,
                        groupValue: _selectedQuestIndex,
                        onChanged: (int? value) {
                          _selectQuest(value!);
                        },
                      ),
                    );
                  }).toList(),
                  SizedBox(height: 20),
                  Center(
                    child: ElevatedButton(
                      onPressed: _createQuest,
                      child: Text('퀘스트 생성하기'),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class QuestDetailPage extends StatelessWidget {
  final dynamic quest;

  QuestDetailPage({required this.quest});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('퀘스트 정보'),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              quest['quest_name'],
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text(
              quest['description'],
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 10),
            Text(
              '연령대: ${quest['age_group']}',
              style: TextStyle(fontSize: 18),
            ),
            Text(
              '성별: ${quest['gender']}',
              style: TextStyle(fontSize: 18),
            ),
            Text(
              '카테고리: ${quest['category']}',
              style: TextStyle(fontSize: 18),
            ),
            Text(
              '날짜: ${quest['date_range']}',
              style: TextStyle(fontSize: 18),
            ),
          ],
        ),
      ),
    );
  }
}
