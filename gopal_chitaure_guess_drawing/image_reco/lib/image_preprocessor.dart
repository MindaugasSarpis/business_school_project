import 'dart:typed_data';
import 'package:image/image.dart' as img;

/// Matches Python training preprocessing for MobileNet:
/// Grayscale → Threshold → Invert → Crop to strokes → Resize (64x64) → Normalize [-1, 1]
Future<List<List<List<double>>>> preprocessForMobileNetGray64(
    Uint8List pngBytes) async {
  img.Image original = img.decodeImage(pngBytes)!;

  // Convert to grayscale
  img.Image gray = img.grayscale(original);

  // Threshold + Invert
  for (int y = 0; y < gray.height; y++) {
    for (int x = 0; x < gray.width; x++) {
      final pixel = gray.getPixel(x, y);
      final luminance = img.getLuminanceRgb(pixel.r, pixel.g, pixel.b).toInt();
      final binary = luminance < 128 ? 255 : 0;
      final inverted = 255 - binary;
      gray.setPixelRgba(x, y, inverted, inverted, inverted, 255);
    }
  }

  // Find bounding box
  int minX = gray.width, minY = gray.height, maxX = 0, maxY = 0;
  for (int y = 0; y < gray.height; y++) {
    for (int x = 0; x < gray.width; x++) {
      final pixel = gray.getPixel(x, y);
      final luminance = img.getLuminanceRgb(pixel.r, pixel.g, pixel.b).toInt();
      if (luminance > 0) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }

  // Crop to bounding box
  if (minX < maxX && minY < maxY) {
    int cropWidth = maxX - minX + 1;
    int cropHeight = maxY - minY + 1;
    gray = img.copyCrop(gray,
        x: minX, y: minY, width: cropWidth, height: cropHeight);
  }

  // Resize to 64x64
  img.Image resized = img.copyResize(gray, width: 64, height: 64);

  // Normalize to [-1, 1]
  List<List<List<double>>> normalized = List.generate(64, (y) {
    return List.generate(64, (x) {
      final pixel = resized.getPixel(x, y);
      final luminance =
          img.getLuminanceRgb(pixel.r, pixel.g, pixel.b).toDouble();
      final scaled = (luminance / 127.5) - 1.0;
      return [scaled]; // Only 1 channel for grayscale
    });
  });

  return normalized;
}
