from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pickle
from src.data_preprocessing import load_and_clean

def train_model():
    # Load and clean the data
    df = load_and_clean('data/chat_data.csv')
    
    # Train the model
    model = make_pipeline(CountVectorizer(), MultinomialNB())
    model.fit(df['cleaned_text'], df['label'])
    
    # Save the model
    with open('models/sentiment_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("Model trained and saved as models/sentiment_model.pkl")

def predict_sentiment(text):
    with open('models/sentiment_model.pkl', 'rb') as f:
        model = pickle.load(f)
    prediction = model.predict([text])
    return str(prediction[0])

if __name__ == "__main__":
    train_model()
