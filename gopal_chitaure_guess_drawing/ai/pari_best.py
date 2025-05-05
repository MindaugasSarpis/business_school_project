import os
import urllib.request
import numpy as np
import cv2
from tqdm import tqdm
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D, Dense, Dropout, Input, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.utils import shuffle
from tensorflow.keras.utils import to_categorical
import json

# Constants
DATA_PATH = "dataset"
CATEGORIES_FILE = "categories.txt"
NDJSON_BASE_URL = "https://storage.googleapis.com/quickdraw_dataset/full/simplified"
IMG_SIZE = 28
MAX_IMAGES_PER_CATEGORY = 1500

# Load categories
with open(CATEGORIES_FILE, 'r') as f:
    categories = [line.strip() for line in f.readlines()]

os.makedirs(DATA_PATH, exist_ok=True)

def download_ndjson(category):
    category_file = f"{category.replace(' ', '%20')}.ndjson"
    url = f"{NDJSON_BASE_URL}/{category_file}"
    filepath = os.path.join(DATA_PATH, f"{category}.ndjson")
    if not os.path.exists(filepath):
        print(f"Downloading {category}...")
        urllib.request.urlretrieve(url, filepath)

def preprocess_image(img):
    _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = cv2.findNonZero(img)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        img = img[y:y+h, x:x+w]
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    return img

def convert_ndjson_to_images(category):
    ndjson_file = os.path.join(DATA_PATH, f"{category}.ndjson")
    category_path = os.path.join(DATA_PATH, category)
    os.makedirs(category_path, exist_ok=True)

    existing_images = len([f for f in os.listdir(category_path) if f.endswith('.png')])
    if existing_images >= MAX_IMAGES_PER_CATEGORY:
        return

    with open(ndjson_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= MAX_IMAGES_PER_CATEGORY:
                break
            output_path = os.path.join(category_path, f"{category}_{i}.png")
            if os.path.exists(output_path):
                continue
            drawing_json = json.loads(line)
            drawing = drawing_json['drawing']
            img = np.zeros((256, 256), np.uint8)
            for stroke in drawing:
                points = np.array(list(zip(stroke[0], stroke[1])), np.int32).reshape((-1, 1, 2))
                cv2.polylines(img, [points], False, 255, 2)
            img = preprocess_image(img)
            cv2.imwrite(output_path, img)

def load_images():
    X, y = [], []
    for idx, category in enumerate(tqdm(categories, desc="Loading images")):
        category_path = os.path.join(DATA_PATH, category)
        image_files = [f for f in os.listdir(category_path) if f.endswith('.png')]
        for image_file in image_files[:MAX_IMAGES_PER_CATEGORY]:
            image_path = os.path.join(category_path, image_file)
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                X.append(img)
                y.append(idx)
    return np.array(X), np.array(y)

# Download and preprocess dataset
for category in tqdm(categories, desc="Preparing dataset"):
    download_ndjson(category)
    convert_ndjson_to_images(category)

X, y = load_images()
X = X.reshape(-1, IMG_SIZE, IMG_SIZE, 1).astype('float32')

# Normalize to zero mean and unit variance
mean = np.mean(X, axis=0)
std = np.std(X, axis=0) + 1e-7
X = (X - mean) / std

# One-hot encode labels
y = to_categorical(y, num_classes=len(categories))

# Shuffle before split
X, y = shuffle(X, y, random_state=42)

print(f"Loaded {X.shape[0]} samples across {len(categories)} classes.")

# Data Augmentation
datagen = ImageDataGenerator(
    validation_split=0.1,
    rotation_range=15,
    zoom_range=0.15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.15,
    fill_mode='nearest'
)

train_generator = datagen.flow(X, y, batch_size=128, subset='training')
val_generator = datagen.flow(X, y, batch_size=128, subset='validation')

# Improved CNN Model
model = Sequential([
    Input(shape=(IMG_SIZE, IMG_SIZE, 1)),

    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    Dropout(0.2),
    MaxPooling2D((2, 2)),

    Conv2D(128, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    Dropout(0.3),
    MaxPooling2D((2, 2)),

    Conv2D(256, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    Dropout(0.4),
    MaxPooling2D((2, 2)),

    GlobalAveragePooling2D(),
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(len(categories), activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6),
    ModelCheckpoint("best_model.h5", monitor='val_accuracy', save_best_only=True)
]

model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=50,
    callbacks=callbacks
)

# Save Final Model
model.save("quickdraw_cnn.h5")

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
tflite_model = converter.convert()

with open("quickdraw_cnn.tflite", "wb") as f:
    f.write(tflite_model)

print("\n✅ Model trained and converted to TFLite successfully.")
