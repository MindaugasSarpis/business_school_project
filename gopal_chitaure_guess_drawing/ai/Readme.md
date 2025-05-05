# 🖍️ QuickDraw Sketch Recognition

## 🚀 Overview

This repository provides Python scripts to:

✅ Download QuickDraw dataset (.ndjson format)  
✅ Convert vector drawings to 28x28 grayscale images  
✅ Train a CNN model for sketch recognition  
✅ Convert the model to TensorFlow Lite (TFLite) for deployment

---

## 📌 Setup

### 1️⃣ Create & Activate a Virtual Environment (Recommended)

**Using `venv` (Built-in Python Virtual Environment):**

```bash
python3 -m venv quickdraw_env
source quickdraw_env/bin/activate      # On macOS/Linux
quickdraw_env\Scripts\activate         # On Windows
```

**Using `conda` (If you prefer Conda environments):**

```bash
conda create --name quickdraw_env python=3.9
conda activate quickdraw_env
```

---

### 2️⃣ Install Dependencies

```bash
pip install tensorflow numpy tqdm opencv-python urllib3
```

---

### 3️⃣ Download QuickDraw Dataset

```bash
python3 download_quickdraw_ndjson.py
```

---

### 4️⃣ Convert `.ndjson` to Images

```bash
python3 convert_ndjson_to_images.py
```

---

### 5️⃣ Train the CNN Model

```bash
python3 train_quickdraw_images.py
```

---

### 6️⃣ Convert Model to TFLite

```bash
python3 convert_to_tflite.py
```

---

## 🔹 Deactivate Virtual Environment

**For `venv`:**

```bash
deactivate
```

**For `conda`:**

```bash
conda deactivate
```

---

## ✅ Summary

- Use a virtual environment (`venv` or `conda`) for better package management
- Ensure `categories.txt` contains category names (e.g., `apple`, `car`)
- Run the scripts in order:  
  `download → convert → train → export`
- Trained model will be saved as:
  - `quickdraw_cnn.h5` (Keras model)
  - `quickdraw_cnn.tflite` (For mobile deployment)
