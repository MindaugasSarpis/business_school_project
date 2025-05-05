from flask import Flask, render_template, request, jsonify
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

# Load model and tokenizer
model_path = "./models/distilbert_dailydialog"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)
model.eval()

# Define emotion labels based on your training
label_map = {
    0: "Anger",
    1: "Disgust",
    2: "Fear",
    3: "Happiness",
    4: "Sadness",
    5: "Surprise"
}

# Clean text (simple cleaning)
def clean_text(text):
    return text.strip()

# Predict function
def predict_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=-1).item()
    return predicted_class

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.json['chat_input']
    
    # Handle very short input
    if len(text.strip().split()) <= 1:
        return jsonify({'sentiment': "Neutral"})

    cleaned_text = clean_text(text)
    emotion_id = predict_emotion(cleaned_text)
    emotion_label = label_map.get(emotion_id, "Unknown")

    return jsonify({'sentiment': emotion_label})

if __name__ == "__main__":
    app.run(debug=True)
