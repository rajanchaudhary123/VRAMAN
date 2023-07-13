# import os
# import pickle
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer
# from django.conf import settings
# import pickle

# # Download NLTK resources (if not already downloaded)
# nltk.download('punkt')
# nltk.download('wordnet')

# # Load the sentiment analysis model
# model_path =  os.path.join(settings.BASE_DIR, 'marketplace', 'sentiment_model.pkl')
# with open(model_path, 'rb') as f:
#     sentiment_model = pickle.load(f)

# # Create a lemmatizer instance
# lemmatizer = WordNetLemmatizer()

# # Preprocess the text
# def preprocess_text(text):
#     # Tokenize the text
#     tokens = word_tokenize(text)
    
#     # Lemmatize the tokens
#     lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
#     # Join the tokens back into a string
#     processed_text = ' '.join(lemmatized_tokens)
    
#     return processed_text

# # Analyze the sentiment of a review
# def analyze_sentiment(review):
#     preprocessed_review = preprocess_text(review)
#     vectorized_review = vectorizer.transform([preprocessed_review])
#     sentiment = sentiment_model.predict(vectorized_review)[0]
#     return sentiment
