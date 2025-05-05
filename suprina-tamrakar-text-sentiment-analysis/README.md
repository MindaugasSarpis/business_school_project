# Chat Emotion Detection 🚀

An interactive AI-powered web application that **detects emotions** from chat messages in real-time using a fine-tuned **DistilBERT** model.  
The app features a sleek chat interface powered by **Flask**, with live predictions from an NLP model trained on the **DailyDialog** dataset.
[![Watch the demo](https://img.youtube.com/vi/H17m7z6qffU/hqdefault.jpg)](https://youtube.com/shorts/H17m7z6qffU?feature=share)

---

## ✨ Features

- Real-time emotion detection (Anger, Disgust, Fear, Happiness, Sadness, Surprise)
- Clean, mobile-style chat interface with animated AI thinking
- Fine-tuned transformer (DistilBERT) model for emotion classification
- One-command setup with automated training and launch
- Fully offline and private — runs locally on your machine

---

## 📚 About the Project

This project fine-tunes a pre-trained `distilbert-base-uncased` model using the DailyDialog dataset from Hugging Face.  
The goal is to classify emotional responses in chat messages across six categories:

- 😡 Anger
- 🤢 Disgust
- 😨 Fear
- 😄 Happiness
- 😢 Sadness
- 😲 Surprise

---

## 🧠 Model Training

- **Dataset**: [DailyDialog](https://huggingface.co/datasets/daily_dialog)
- **Labels**: Only emotions 1–6 are used (label 0 is excluded)
- **Preprocessing**: Cleaned, flattened, and label-shifted (1–6 → 0–5)
- **Model**: `DistilBERTForSequenceClassification`
- **Metrics**: Accuracy and weighted F1-score
- **Frameworks**: PyTorch, HuggingFace Transformers, Datasets

---

## ⚙️ Setup and Run

### 1. Clone the Repository

```bash
git clone https://github.com/mindaugassarpis/business_school_project
cd suprina-tamrakar-text-sentiment-analysis
```

### 2. Run the Application

```bash
chmod +x run.sh
./run.sh
```

This command will:

- 🔧 Create a virtual environment (`bert_env`)
- 📦 Install dependencies from `requirements.txt`
- 🧠 Train the model (if not already trained)
- 🚀 Start the Flask server

### 3. Access the App

Open your browser and go to:

```
http://127.0.0.1:5000/
```

---

## 🗂 Project Structure

```
chat-emotion-detection/
├── app.py                     # Flask app backend
├── train_bert_sentiment.py    # Model training script
├── templates/
│   └── index.html             # Chat UI
├── models/
│   └── distilbert_dailydialog/ # Saved model directory
├── run.sh                     # One-click runner script
├── requirements.txt           # Python dependencies
└── README.md
```

---

## 🧩 Requirements

- Python 3.10 recommended (not compatible with 3.12+)
- `pip` or `conda`
- `git`

---

## 📬 Contact

**Suprina Tamrakar**  
📧 Email: suprina.tamrakar@vm.stud.vu.lt / tamrakar.suprina@gmail.com

---

Feel your feelings. Let the AI feel them too. 💬🧠
