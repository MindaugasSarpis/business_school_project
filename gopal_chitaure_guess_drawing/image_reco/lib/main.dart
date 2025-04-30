import 'package:flutter/material.dart';
import 'package:image_reco/draw_guessing_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QuickDraw Guessing',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: const DrawGuessingScreen(), // ✅ This provides Directionality
    );
  }
}
