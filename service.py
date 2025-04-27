# from simpletransformers.classification import ClassificationModel
# import logging
# import os

# # Set logging level
# logging.basicConfig(level=logging.ERROR)

# # Define model directory
# MODEL_DIR = "./my_saved_model"

# # Load or download the model
# if not os.path.exists(MODEL_DIR) or not os.path.exists(os.path.join(MODEL_DIR, "pytorch_model.bin")):
#     print("Model not found locally, downloading pretrained model...")
#     model = ClassificationModel(
#     "bert", 
#     "textattack/bert-base-uncased-SST-2", 
#     num_labels=2,
#     use_cuda=False,
#     args={"reprocess_input_data": True, "overwrite_output_dir": True},
# )

#     model.save_model(MODEL_DIR)
# else:
#     model = ClassificationModel(
#         "bert", MODEL_DIR, use_cuda=False
#     )

# def predict_text(text: str):
#     predictions, _ = model.predict([text])
#     return {"prediction": int(predictions[0])}
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
    return {"prediction": prediction, "scores": dict(zip(labels, map(float, scores)))}

# Example usage
text = "not good"
result = predict_text(text)
print(result)
