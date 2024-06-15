import 'package:flutter/material.dart';
import 'screens/main_page.dart';
import 'screens/quest_provide_page.dart';
import 'screens/feedback_page.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: '퀘스트 추천 앱',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        fontFamily: 'GmarketSansTTF',
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => MainPage(),
        '/quest_provide': (context) => QuestProvidePage(),
        '/feedback': (context) => FeedbackPage(),
      },
    );
  }
}
