import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'image_preprocessor.dart';

class QuickDrawClassifier {
  late final Interpreter _interpreter;
  late final List<String> labels;
  bool _isLoaded = false;

  static const int imgSize = 64;

  Future<void> loadModel() async {
    try {
      _interpreter = await Interpreter.fromAsset(
        'lib/assets/model/quickdraw_cnn.tflite',
        options: InterpreterOptions()..threads = 2,
      );

      final labelData =
          await rootBundle.loadString('lib/assets/model/categories.txt');
      labels = labelData
          .split('\n')
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList();

      if (labels.isEmpty) {
        throw Exception("❌ Labels file is empty.");
      }

      _isLoaded = true;
      print("✅ Model & labels loaded (\${labels.length} categories)");
    } catch (e) {
      print("❌ Failed to load model or labels: \$e");
      rethrow;
    }
  }

  Future<List<MapEntry<String, double>>> predictTop3(Uint8List pngBytes) async {
    if (!_isLoaded) {
      throw Exception("Model not loaded. Call loadModel() first.");
    }

    // 1. Preprocess image to [64][64][1]
    final List<List<List<double>>> inputTensor =
        await preprocessForMobileNetGray64(pngBytes);

    // 2. Flatten into Float32List
    final input = Float32List(imgSize * imgSize);
    int index = 0;
    for (int y = 0; y < imgSize; y++) {
      for (int x = 0; x < imgSize; x++) {
        input[index++] = inputTensor[y][x][0];
      }
    }

    // 3. Output buffer
    final output = List.filled(labels.length, 0.0).reshape([1, labels.length]);

    // 4. Run inference
    _interpreter.run(input.reshape([1, imgSize, imgSize, 1]), output);

    // 5. Postprocess scores
    final scores = List<double>.from(output[0]);

    List<MapEntry<String, double>> top3 =
        List.generate(labels.length, (i) => MapEntry(labels[i], scores[i]))
          ..sort((a, b) => b.value.compareTo(a.value));

    return top3.take(3).toList();
  }

  void close() => _interpreter.close();
}
