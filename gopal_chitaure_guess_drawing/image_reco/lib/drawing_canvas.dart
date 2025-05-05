import 'package:flutter/material.dart';

class DrawingCanvas extends StatefulWidget {
  final VoidCallback onClear;
  const DrawingCanvas({required this.onClear, Key? key}) : super(key: key);

  @override
  State<DrawingCanvas> createState() => _DrawingCanvasState();
}

class _DrawingCanvasState extends State<DrawingCanvas> {
  List<Offset?> _points = [];

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanUpdate: (details) {
        RenderBox? renderBox = context.findRenderObject() as RenderBox?;
        if (renderBox != null) {
          Offset localPosition =
              renderBox.globalToLocal(details.globalPosition);
          setState(() {
            _points = List.from(_points)..add(localPosition);
          });
        }
      },
      onPanEnd: (_) => setState(() => _points.add(null)),
      child: CustomPaint(
        painter: _CanvasPainter(points: _points),
        size: const Size(280, 280),
      ),
    );
  }

  void clear() => setState(() => _points = []);
}

class _CanvasPainter extends CustomPainter {
  final List<Offset?> points;
  _CanvasPainter({required this.points});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black
      ..strokeCap = StrokeCap.round
      ..strokeWidth = 4.0;

    for (int i = 0; i < points.length - 1; i++) {
      final p1 = points[i];
      final p2 = points[i + 1];
      if (p1 != null && p2 != null) {
        canvas.drawLine(p1, p2, paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _CanvasPainter oldDelegate) => true;
}
