import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from transformers import DataCollatorWithPadding
from datasets import load_dataset, Dataset
from torch import nn
from sklearn.metrics import accuracy_score, f1_score

# Load and prepare data
def load_data():
    print("[INFO] Loading DailyDialog data from Hugging Face...")

    dataset = load_dataset("daily_dialog")

    # Process split
    def extract_sentences_and_labels(split):
        texts = []
        labels = []
        for dialog, emotions in zip(split['dialog'], split['emotion']):
            texts.extend(dialog)
            labels.extend(emotions)
        return texts, labels

    train_texts, train_labels = extract_sentences_and_labels(dataset['train'])
    val_texts, val_labels = extract_sentences_and_labels(dataset['validation'])

    # Map to DataFrames
    train_df = pd.DataFrame({'text': train_texts, 'label': train_labels})
    val_df = pd.DataFrame({'text': val_texts, 'label': val_labels})

    # Keep only emotions 1-6 (skip 0 = 'no emotion')
    train_df = train_df[train_df['label'] != 0]
    val_df = val_df[val_df['label'] != 0]

    # Remap labels (1→0, 2→1, ..., 6→5)
    train_df['label'] = train_df['label'] - 1
    val_df['label'] = val_df['label'] - 1

    print(f"[INFO] Loaded {len(train_df)} training sentences, {len(val_df)} validation sentences after cleaning.")
    return train_df, val_df

# Load full dataset
train_df, val_df = load_data()
train_df = train_df.sample(n=10000, random_state=42)
# (NO subsampling now - use full data)

# Remove pandas index
train_dataset = Dataset.from_pandas(train_df, preserve_index=False)
val_dataset = Dataset.from_pandas(val_df, preserve_index=False)

print(f"[INFO] Train size: {len(train_dataset)}, Validation size: {len(val_dataset)}")

# Load tokenizer and model (DistilBERT)
print("[INFO] Loading tokenizer and model...")
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=6)
print("[INFO] Tokenizer and model loaded successfully.")

# Tokenization
print("[INFO] Tokenizing datasets...")
def tokenize_function(batch):
    return tokenizer(batch["text"], padding=True, truncation=True)

train_dataset = train_dataset.map(tokenize_function, batched=True)
val_dataset = val_dataset.map(tokenize_function, batched=True)
print("[INFO] Tokenization completed.")

# Data collator
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Calculate class weights
print("[INFO] Calculating class weights...")
class_counts = train_df['label'].value_counts().sort_index()
weights = torch.tensor([1.0 / c for c in class_counts], dtype=torch.float)
weights = weights / weights.sum()
print(f"[INFO] Class weights: {weights.tolist()}")

# Custom Trainer with custom loss
class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss_fct = nn.CrossEntropyLoss(weight=weights.to(logits.device))
        loss = loss_fct(logits.view(-1, 6), labels.view(-1))  # 6 classes
        return (loss, outputs) if return_outputs else loss

# Compute metrics
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average='weighted')
    return {
        'accuracy': acc,
        'f1': f1,
    }

# Training arguments
print("[INFO] Setting up training arguments...")
training_args = TrainingArguments(
    output_dir='./results',
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=1,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    logging_dir='./logs',
    logging_steps=500,
    fp16=False,  # Set True if your GPU supports it
)

# Initialize trainer
print("[INFO] Initializing Trainer...")
trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# Train
print("[INFO] Starting training...")
trainer.train()
print("[INFO] Training completed.")

# Final evaluation
print("[INFO] Evaluating model on validation set...")
metrics = trainer.evaluate()
print(metrics)

# Save model and tokenizer
print("[INFO] Saving model and tokenizer...")
model.save_pretrained('./models/distilbert_dailydialog')
tokenizer.save_pretrained('./models/distilbert_dailydialog')
print("[INFO] Model and tokenizer saved to './models/distilbert_dailydialog'.")
