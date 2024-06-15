import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000/api';

  static Future<Map<String, dynamic>> fetchQuests() async {
    final response = await http.get(Uri.parse('$baseUrl/quests'));
    if (response.statusCode == 200) {
      // response.body 대신 response.bodyBytes를 사용하여 UTF-8로 디코드
      return json.decode(utf8.decode(response.bodyBytes));
    } else {
      throw Exception('퀘스트를 불러오는데 실패했습니다');
    }
  }

  static Future<void> submitFeedback(String questId, String feedback) async {
    final response = await http.post(
      Uri.parse('$baseUrl/feedback/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'quest_id': questId,
        'feedback': feedback,
      }),
    );

    // 로그 출력 추가
    print('Status Code: ${response.statusCode}');
    print('Response Body: ${response.body}');

    if (response.statusCode != 200) {
      throw Exception('피드백 제출 실패');
    }
  }
}
