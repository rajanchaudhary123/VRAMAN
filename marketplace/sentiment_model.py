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

data.head()

print(data.describe())

# Visualize the sentiment class distribution
plt.figure(figsize=(8, 6))
sns.countplot(data=data, x='Sentiments')
plt.title('Sentiment Class Distribution')
plt.xlabel('Sentiments')
plt.ylabel('Count')
plt.show()

# Word cloud of the text data
from wordcloud import WordCloud

# Concatenate all the text data into a single string
text_data = ' '.join(data['Text'])

# Generate a word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

# Plot the word cloud
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Text Data')
plt.show()

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

# Create a Random Forest classifier
classifier = RandomForestClassifier()

# Train the classifier
classifier.fit(train_vectors, train_labels)

# Make predictions on the testing data
predictions = classifier.predict(test_vectors)

# Calculate the accuracy of the model
accuracy = accuracy_score(test_labels, predictions)
print("Accuracy:", accuracy)

# Save the trained model using joblib
joblib.dump(classifier, 'sentiment_model.pkl')

