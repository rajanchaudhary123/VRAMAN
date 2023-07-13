import pandas as pd
import numpy as np
import nltk
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Download NLTK resources (if not already downloaded)
nltk.download('punkt')
nltk.download('wordnet')

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Load the dataset
data = pd.read_excel('./project_dataset.xlsx')

data['Sentiments'] = data['Sentiments'].map({'positive': 1, 'negative': 0})


data.head()

print(data.describe())

# Preprocess the data
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Lemmatize the tokens
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    # Join the tokens back into a string
    processed_text = ' '.join(lemmatized_tokens)
    
    return processed_text


# Apply preprocessing to the 'Text' column
data['Text'] = data['Text'].apply(preprocess_text)

# Split the data into training and testing sets
train_data, test_data, train_labels, test_labels = train_test_split(data['Text'], data['Sentiments'], test_size=0.2, random_state=42)

# Create a TF-IDF vectorizer and transform the training data
vectorizer = TfidfVectorizer()
train_vectors = vectorizer.fit_transform(train_data)

# Transform the testing data
test_vectors = vectorizer.transform(test_data)

import pickle
# Save the fitted vectorizer
vectorizer_path = './vectorizer.pkl'
with open(vectorizer_path, 'wb') as f:
    pickle.dump(vectorizer, f)

# Create a Random Forest classifier
classifier = RandomForestClassifier()

# Train the classifier
classifier.fit(train_vectors, train_labels)

# Make predictions on the testing data
predictions = classifier.predict(test_vectors)

# Calculate the accuracy of the model
accuracy = accuracy_score(test_labels, predictions)
print("Accuracy:", accuracy)



# Save the trained model
model_path = 'sentiment_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(classifier, f)

