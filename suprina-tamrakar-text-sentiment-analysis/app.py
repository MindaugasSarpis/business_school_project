from flask import Flask, render_template, request, jsonify
from src.data_preprocessing import clean_text
from src.sentiment_analysis import predict_sentiment

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.json['chat_input']
    cleaned_text = clean_text(text)
    sentiment = predict_sentiment(cleaned_text)
    return jsonify({'sentiment': 'Positive' if sentiment == '1' else 'Negative'})

if __name__ == "__main__":
    app.run(debug=True)
