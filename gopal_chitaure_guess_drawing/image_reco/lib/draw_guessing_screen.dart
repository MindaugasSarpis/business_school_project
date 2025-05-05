import 'dart:typed_data';
import 'dart:ui' as ui;
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/rendering.dart';
import 'package:path_provider/path_provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:image_gallery_saver/image_gallery_saver.dart';
import 'package:permission_handler/permission_handler.dart';
import '../quickdraw_classifier.dart';
import '../drawing_canvas.dart';

class DrawGuessingScreen extends StatefulWidget {
  const DrawGuessingScreen({Key? key}) : super(key: key);

  @override
  State<DrawGuessingScreen> createState() => _DrawGuessingScreenState();
}

class _DrawGuessingScreenState extends State<DrawGuessingScreen> {
  final GlobalKey _canvasKey = GlobalKey();
  final GlobalKey _canvasImageKey = GlobalKey();
  String aiGuess = "🤖 Waiting for drawing...";
  bool isLoading = false;
  final classifier = QuickDrawClassifier();
  List<File> testImages = [];
  List<MapEntry<String, double>> top3Guesses = [];
  File? overlayImage;

  @override
  void initState() {
    super.initState();
    classifier.loadModel();
  }

  Future<void> _loadTestImages() async {
    final tempDir = await getTemporaryDirectory();
    testImages.clear();
    for (int i = 1; i <= 13; i++) {
      final byteData = await rootBundle.load('lib/assets/images/test/$i.png');
      final file = File('${tempDir.path}/$i.png');
      await file.writeAsBytes(byteData.buffer.asUint8List());
      testImages.add(file);
    }
    setState(() {});
  }

  Future<File> _saveDrawingToGalleryAndGetFile() async {
    RenderRepaintBoundary boundary =
        _canvasImageKey.currentContext!.findRenderObject()
            as RenderRepaintBoundary;
    ui.Image image = await boundary.toImage(pixelRatio: 2.0);
    ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
    Uint8List pngBytes = byteData!.buffer.asUint8List();

    final status = await Permission.storage.request();
    if (!status.isGranted) throw Exception("Storage permission not granted.");

    final result = await ImageGallerySaver.saveImage(
      pngBytes,
      name: "quickdraw_${DateTime.now().millisecondsSinceEpoch}",
    );

    if (result['filePath'] != null && await File(result['filePath']).exists()) {
      return File(result['filePath']);
    } else if (result['path'] != null && await File(result['path']).exists()) {
      return File(result['path']);
    } else {
      final tempDir = await getTemporaryDirectory();
      final fallbackPath = '${tempDir.path}/drawing_fallback.png';
      final fallbackFile = File(fallbackPath);
      await fallbackFile.writeAsBytes(pngBytes);
      return fallbackFile;
    }
  }

  Future<void> _processImage(File imageFile) async {
    setState(() {
      isLoading = true;
      top3Guesses.clear();
    });

    try {
      Uint8List pngBytes = await imageFile.readAsBytes();
      print("📸 Processing Image: ${imageFile.path}");

      final predictions = await classifier.predictTop3(pngBytes);

      setState(() {
        top3Guesses = predictions;
        aiGuess = "🤖 I think it's: ${predictions.first.key}";
      });
    } catch (e) {
      print("❌ Error during prediction: $e");
      setState(() => aiGuess = "⚠️ Failed to process image.");
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> _guessDrawing() async {
    try {
      File savedFile = await _saveDrawingToGalleryAndGetFile();
      await _processImage(savedFile);
    } catch (e) {
      print("❌ Failed to save or process drawing: $e");
    }
  }

  Future<void> _pickImage() async {
    final pickedFile = await ImagePicker().pickImage(
      source: ImageSource.gallery,
    );
    if (pickedFile != null) {
      File imageFile = File(pickedFile.path);

      _clearCanvas();
      setState(() {
        overlayImage = imageFile;
      });
      await _processImage(imageFile);
    }
  }

  void _clearCanvas() {
    (_canvasKey.currentState as dynamic).clear();
    setState(() {
      overlayImage = null;
      aiGuess = "🤖 Waiting for drawing...";
      top3Guesses.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Draw or Pick an Image")),
      body: Column(
        children: [
          Expanded(
            child: Container(
              color: Colors.grey[200],
              child: Center(
                child: RepaintBoundary(
                  key: _canvasImageKey,
                  child: Container(
                    width: 280,
                    height: 280,
                    color: Colors.white,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        DrawingCanvas(key: _canvasKey, onClear: () {}),
                        if (overlayImage != null)
                          Image.file(
                            overlayImage!,
                            width: 280,
                            height: 280,
                            fit: BoxFit.fitWidth,
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
          if (isLoading) const LinearProgressIndicator(),
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Text(aiGuess, style: const TextStyle(fontSize: 20)),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12.0),
            child: Wrap(
              alignment: WrapAlignment.center,
              spacing: 8,
              runSpacing: 8,
              children:
                  top3Guesses.map((entry) {
                    return ElevatedButton(
                      onPressed: () {},
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 10,
                        ),
                      ),
                      child: Text(
                        "${entry.key} (${(entry.value * 100).toStringAsFixed(1)}%)",
                        style: const TextStyle(fontSize: 14),
                      ),
                    );
                  }).toList(),
            ),
          ),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Row(
              children:
                  testImages.map((file) {
                    return GestureDetector(
                      onTap: () => _processImage(file),
                      child: Container(
                        margin: const EdgeInsets.all(4),
                        width: 60,
                        height: 60,
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.black26),
                          image: DecorationImage(
                            image: FileImage(file),
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                    );
                  }).toList(),
            ),
          ),
          const SizedBox(height: 4),
          ElevatedButton.icon(
            onPressed: _loadTestImages,
            icon: const Icon(Icons.folder_open),
            label: const Text("Pick Trained Data"),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton.icon(
                onPressed: _guessDrawing,
                icon: const Icon(Icons.search),
                label: const Text("Let AI Guess"),
              ),
              const SizedBox(width: 10),
              ElevatedButton.icon(
                onPressed: _pickImage,
                icon: const Icon(Icons.image),
                label: const Text("Pick Image"),
              ),
              const SizedBox(width: 10),
              ElevatedButton.icon(
                onPressed: _clearCanvas,
                icon: const Icon(Icons.clear),
                label: const Text("Clear"),
              ),
            ],
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}
