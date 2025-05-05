import os
import json
import urllib.request
import numpy as np
import cv2
from tqdm import tqdm
from sklearn.utils import shuffle
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.metrics import TopKCategoricalAccuracy
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, Input

# -------------------- Constants --------------------
DATA_PATH = "dataset"
CATEGORIES_FILE = "categories.txt"
NDJSON_BASE_URL = "https://storage.googleapis.com/quickdraw_dataset/full/simplified"
IMG_SIZE = 64
MAX_IMAGES_PER_CATEGORY = 5000
LINE_WIDTH = 6

# -------------------- Load Categories --------------------
with open(CATEGORIES_FILE, 'r') as f:
    categories = [line.strip() for line in f.readlines()]

os.makedirs(DATA_PATH, exist_ok=True)
category_to_label = {cat: i for i, cat in enumerate(categories)}
label_to_category = {i: cat for i, cat in enumerate(categories)}

# -------------------- Download & Convert --------------------
def download_ndjson(category):
    category_file = f"{category.replace(' ', '%20')}.ndjson"
    url = f"{NDJSON_BASE_URL}/{category_file}"
    filepath = os.path.join(DATA_PATH, f"{category}.ndjson")
    if not os.path.exists(filepath):
        print(f"Downloading {category}...")
        urllib.request.urlretrieve(url, filepath)

def draw_strokes_temporal_color(drawing, img_size=256, line_width=LINE_WIDTH):
    img = np.zeros((img_size, img_size), np.uint8)
    for t, stroke in enumerate(drawing):
        for i in range(len(stroke[0]) - 1):
            color = 255 - min(t, 10) * 13
            pt1 = (stroke[0][i], stroke[1][i])
            pt2 = (stroke[0][i + 1], stroke[1][i + 1])
            cv2.line(img, pt1, pt2, color, line_width)
    return img

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
            img = draw_strokes_temporal_color(drawing)
            img = preprocess_image(img)
            cv2.imwrite(output_path, img)

# -------------------- Load Images --------------------
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

# -------------------- Prepare Dataset --------------------
for category in tqdm(categories, desc="Preparing dataset"):
    download_ndjson(category)
    convert_ndjson_to_images(category)

X, y = load_images()
X = np.expand_dims(X, -1).astype('float32')
X = preprocess_input(X)

y = to_categorical(y, num_classes=len(categories))
X, y = shuffle(X, y, random_state=42)
print(f"Loaded {X.shape[0]} samples across {len(categories)} classes.")

# -------------------- Data Augmentation --------------------
datagen = ImageDataGenerator(
    validation_split=0.1,
    rotation_range=15,
    zoom_range=0.15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    fill_mode='nearest'
)
train_generator = datagen.flow(X, y, batch_size=128, subset='training')
val_generator = datagen.flow(X, y, batch_size=128, subset='validation')

# -------------------- MobileNet Model --------------------
base_model = MobileNet(input_shape=(IMG_SIZE, IMG_SIZE, 1), weights=None, include_top=False)
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.5)(x)
predictions = Dense(len(categories), activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=predictions)

model.compile(
    optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=1e-4),
    loss=CategoricalCrossentropy(label_smoothing=0.1),
    metrics=['accuracy', TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
)

# -------------------- Callbacks --------------------
callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6),
    ModelCheckpoint("best_model.h5", monitor='val_accuracy', save_best_only=True)
]

# -------------------- Train Model --------------------
model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=100,
    callbacks=callbacks
)

# -------------------- Save Final Model --------------------
model.save("quickdraw_mobilenet_final.h5")

# -------------------- Convert to TFLite --------------------
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
tflite_model = converter.convert()

with open("quickdraw_mobilenet_final.tflite", "wb") as f:
    f.write(tflite_model)

print("\n✅ MobileNet-based model trained and converted to TFLite successfully.")
