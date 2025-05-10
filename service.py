from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch
import os

# Model ID from Hugging Face
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Labels for the model
labels = ["negative", "neutral", "positive"]

def predict_text(text: str):
    # Tokenize input text
    encoded_input = tokenizer(text, return_tensors='pt', truncation=True)
    with torch.no_grad():
        output = model(**encoded_input)

    # Apply softmax to get probabilities
    scores = softmax(output.logits[0].numpy())
    prediction = labels[scores.argmax()]
    
    # Map sentiment to risk levels
    if scores[0] > 0.7:  # High negative sentiment
        risk = "High"
    elif scores[1] > 0.5:  # Neutral sentiment
        risk = "Moderate"
    else:  # Positive sentiment
        risk = "Low"
    
    return {
        "prediction": prediction,
        "scores": dict(zip(labels, map(float, scores))),
        "risk": risk
    }

# Example usage
text = "not good"
result = predict_text(text)
print(result)
