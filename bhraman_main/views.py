from django.shortcuts import render
from django.http import HttpResponse
from vendor.models import Vendor
from menu.models import PackageItem

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance
from django.contrib.auth.decorators import login_required,user_passes_test

from marketplace.models import CollaborativeRecommendation
from marketplace.models  import Cart
  #for category based import
from accounts.models import User
from django import template
from accounts.views import check_role_customer


#for content based
from marketplace.models import ContentRecommendation
from orders.models import OrderedPackage
import joblib
from django.conf import settings
import os
import pickle
from django.shortcuts import render
from orders.models import  OrderedPackage
from marketplace.models import ContentRecommendation

#for sentiment based 
import pickle
from marketplace.models import ReviewRatingPackage
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
from marketplace.models import SentimentRecommendation



#for new sentiments
import numpy as np







def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng, lat
    elif  'lat' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        request.session['lat'] = lat
        request.session['lng'] = lng
        return lng, lat
    else:
        return None
    
# start for sentiment based-1

import nltk
import os
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences

def preprocess_text(text):
    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    
    # Lemmatize the tokens
    lemmatizer = nltk.WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    # Join the tokens back into a string
    processed_text = ' '.join(lemmatized_tokens)
    
    # Convert the text to lowercase
    processed_text = processed_text.lower()

    return processed_text



# import nltk
# def preprocess_text(text):
#     print(f"Input text type: {type(text)}")
#     # Tokenize the text
#     tokens = nltk.word_tokenize(text)
    
#     # Lemmatize the tokens
#     lemmatizer = nltk.WordNetLemmatizer()
#     lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
#     # Join the tokens back into a string
#     processed_text = ' '.join(lemmatized_tokens)
    
#     # Convert the text to lowercase
#     processed_text = processed_text.lower()

#     return processed_text





# end for sentiment based-1




def home(request):
    # Check if the user has the role of "Customer"
    if request.user.is_authenticated and request.user.role == User.CUSTOMER:
        print("You are viewing home as customer")
        # sample_text = "THE good is  running very bad;"

        # processed_text = preprocess_text(sample_text)
        # print(f"Processed text: {processed_text}")



        
        
        # Start collaborative recommendation from marketplace's recommend_packages

        # Get the user's cart items
        user_cart = Cart.objects.filter(user=request.user)
        user_cart_items = user_cart.values_list('packageitem__id', flat=True)

        # Find other users who have similar cart items
        similar_users = Cart.objects.filter(packageitem__in=user_cart_items).exclude(user=request.user)

        # Find the packages that are in the similar users' carts but not in the current user's cart
        similar_users_cart_items = Cart.objects.filter(user__in=similar_users.values_list('user')).exclude(user=request.user)
        recommended_packages_cf = PackageItem.objects.filter(cart__in=similar_users_cart_items).distinct()[:8]

        # Save the collaborative recommendations for the user
        collaborative_recommendation, created = CollaborativeRecommendation.objects.get_or_create(user=request.user)
        collaborative_recommendation.recommended_packages.set(recommended_packages_cf)

        # End of collaborative recommendation from marketplace's recommend_packages




        #Start of category==interest

        # Retrieve package items based on user's interest
        user = User.objects.get(email=request.user.email)
        user_interest = user.interest
        package_items = PackageItem.objects.filter(category__category_name=user_interest)


        #End of category==Interest


        #Start of content based recommendation

        # Get the current user
        user = request.user
        # Check if the user has any purchase history
        has_purchase_history = OrderedPackage.objects.filter(user=user).exists()

        if not has_purchase_history:
            # No purchase history found
            recommended_packages = []
        else:
            # Define the absolute file path for the cosine similarity model
            file_path = os.path.join(settings.BASE_DIR, 'marketplace', 'just__test_model.pkl')
            # Check if the cosine similarity model file exists
            if os.path.exists(file_path):
                # Load the cosine similarity model
                with open(file_path, 'rb') as f:
                    cosine_similarities = pickle.load(f)
                # Get the user's purchased package
                purchased_package = OrderedPackage.objects.filter(user=user).order_by('-created_at').first()
                print(purchased_package)

                # Check if a purchased package exists
                if not purchased_package:
                    # No purchased package found
                    recommended_packages = []
                    print("no purchase made yet")
                else:
                    # Get the index of the purchased package in the cosine similarity matrix
                    purchased_package_index = purchased_package.packageitem.id

                    # Check if the purchased package index is within bounds
                    if purchased_package_index >= cosine_similarities.shape[0]:
                        # Set similarity scores to 0 for out-of-bound indices
                        similarity_scores = [0] * cosine_similarities.shape[1]
                    else:
                        # Get the similarity scores for the purchased package
                        similarity_scores = cosine_similarities[purchased_package_index]

                    # Get the indices of the top similar packages
                    similar_package_indices = similarity_scores.argsort()[::-1]

                    # Exclude the purchased package itself
                    similar_package_indices = similar_package_indices[similar_package_indices != purchased_package_index]

                    # Get the recommended packages (at least 12 if available)
                    recommended_packages = PackageItem.objects.filter(id__in=similar_package_indices[:8])
                   
                    recommended_packages = sorted(recommended_packages, key=lambda package: similarity_scores[package.id], reverse=True)
                    print("for content based recommend")
                    print(recommended_packages)

                    # Print the cosine similarity scores of the recommended packages
                    for package_index in similar_package_indices[:8]:
                       similarity_score = similarity_scores[package_index]
                       #print(f"Cosine similarity of package {package_index} is {similarity_score}")
            else:
                # Cosine similarity model file not found
                recommended_packages = []

        # Create or update the content recommendation model
        content_recommendation, created = ContentRecommendation.objects.get_or_create(user=user)
        content_recommendation.recommended_packages.set(recommended_packages)
        content_recommendation.save()

        #End of content based recommendation








        #start of sentiment analysis -2



        #new changes to sentiment
        # Get the current user
        user = request.user
        # Load the sentiment analysis model
        # Define the absolute file path for the cosine similarity model
        tokenizer_path = os.path.join(settings.BASE_DIR, 'marketplace', 'tokenizer.pkl')

        # Check if the sentiment analysis model file exists
        if os.path.exists(tokenizer_path):
            # Load the sentiment analysis model
            with open(tokenizer_path, 'rb') as f:
                tokenizer= pickle.load(f)
                print("Tokenizer is successfully loaded.")
        else:
            print("Error loading Tokenizer model.")


        label_encoder_path = os.path.join(settings.BASE_DIR, 'marketplace', 'label_encoder.pkl')

        # Check if the vectorizer model file exists
        if os.path.exists(label_encoder_path):
            # Load the sentiment analysis model
            with open(label_encoder_path, 'rb') as f:
                label_encoder = pickle.load(f)
                print("label_encoder model is successfully loaded.")
        else:
            print("Error loading label_encoder model.")

        

        # Load the trained model
        model_path = os.path.join(settings.BASE_DIR, 'marketplace', 'sentiment_model.h5')

        if os.path.exists(model_path):
            model = load_model(model_path)
            print("sentiment model loaded")
        else:
            print("failed to load sentiment model")

        max_sequence_length = 100
        DEFAULT_SENTIMENT = 0
        # Get the latest review of the current user on a particular package
        try:
            latest_review = ReviewRatingPackage.objects.filter(user=user).latest('created_at')
            print(latest_review)
        except ReviewRatingPackage.DoesNotExist:
            # Handle the case where no review exists for the user
             latest_review = None
             print("no review made yet")
        
        if latest_review is not None:
           
            current_user_review = preprocess_text(latest_review.review)
            current_user_review_sequence = tokenizer.texts_to_sequences([current_user_review])
            current_user_review_sequence = pad_sequences(current_user_review_sequence, maxlen=max_sequence_length)
            current_user_sentiment = np.argmax(model.predict(current_user_review_sequence))
            
            print("I found your sentiment of your latest comment")
            print(current_user_sentiment)
           
        else:
             current_user_sentiment = DEFAULT_SENTIMENT
        
        # Filter reviews with similar sentiments if latest_review is not None
        if latest_review is not None:
            package_reviews = ReviewRatingPackage.objects.filter(package=latest_review.package).exclude(user=user)
            similar_users = []
            for review in package_reviews:
                processed_review = preprocess_text(review.review)
                review_sequence = tokenizer.texts_to_sequences([processed_review])
                review_sequence = pad_sequences(review_sequence, maxlen=max_sequence_length)
                sentiment = np.argmax(model.predict(review_sequence))

                if sentiment == current_user_sentiment:
                    similar_users.append(review.user)
                    print("Similar user found based on sentiment")
        
        else:
            similar_users = []
            print("No similar user based on sentiment")
        
        # Retrieve all purchased packages of similar users
        similar_ordered_packages_init = OrderedPackage.objects.exclude(user=user).filter(user__in=similar_users).values_list('packageitem', flat=True)
        print("Based on your review:")


        if similar_ordered_packages_init:
            similar_ordered_packages = PackageItem.objects.filter(id__in=similar_ordered_packages_init[:8])
            print(similar_ordered_packages)
            print("from new")
        
        else:
            # Retrieve previously stored packages from SentimentRecommendation
            sentiment_recommendation, created = SentimentRecommendation.objects.get_or_create(user=user)
            similar_ordered_packages = sentiment_recommendation.recommended_packages_s.all()
            print(similar_ordered_packages)
            print("from old packages")

        # Create or update the sentiment recommendation model
        sentiment_recommendation, created = SentimentRecommendation.objects.get_or_create(user=user)
        sentiment_recommendation.recommended_packages_s.set(similar_ordered_packages)




           
            
        
            
     
            
            

           
        
     
       




        #original  start
        # # Get the current user
        # user = request.user
        # # Load the sentiment analysis model
        # # Define the absolute file path for the cosine similarity model
        # file_path = os.path.join(settings.BASE_DIR, 'marketplace', 'sentiment_model.pkl')

        # # Check if the sentiment analysis model file exists
        # if os.path.exists(file_path):
        #     # Load the sentiment analysis model
        #     with open(file_path, 'rb') as f:
        #         sentiment_model = pickle.load(f)
        #         print("Sentiment analysis model is successfully loaded.")
        #         print("hello from sentiment")
        # else:
        #     print("Error loading sentiment analysis model.")


        # file_path = os.path.join(settings.BASE_DIR, 'marketplace', 'vectorizer.pkl')

        # # Check if the vectorizer model file exists
        # if os.path.exists(file_path):
        #     # Load the sentiment analysis model
        #     with open(file_path, 'rb') as f:
        #         vectorizer = pickle.load(f)
        #         print("Svectorizer model is successfully loaded.")
        # else:
        #     print("Error loading vectorizer model.")

        # DEFAULT_SENTIMENT = 0

        # # Get the latest review of the current user on a particular package

        # try:
        #     latest_review = ReviewRatingPackage.objects.filter(user=user).latest('created_at')
        #     print(latest_review)

        # except ReviewRatingPackage.DoesNotExist:

        #     # Handle the case where no review exists for the user
        #     latest_review = None
        
        # if latest_review is not None:
        #     current_user_review = preprocess_text(latest_review.review)
        #     current_user_review_vectorized = vectorizer.transform([current_user_review])
        #     current_user_sentiment = sentiment_model.predict(current_user_review_vectorized)[0]
        #     print("i found your sentiment")
        #     print(current_user_sentiment)
        # else:
        #     current_user_sentiment = DEFAULT_SENTIMENT


        # # Filter reviews with similar sentiments if latest_review is not None
        # if latest_review is not None:
        #     package_reviews = ReviewRatingPackage.objects.filter(package=latest_review.package).exclude(user=user)
        #     similar_users = []
        #     print(f"Number of reviews in other_users_reviews: {len(package_reviews)}")
            
            
        #     for review in package_reviews:
                 
        #         processed_review = preprocess_text(review.review)
        #         review_vectorized = vectorizer.transform([processed_review])
        #         sentiment = sentiment_model.predict(review_vectorized)[0]

        #         if sentiment == current_user_sentiment:
        #             similar_users.append(review.user)
        #             print("Similar user found based on sentiment")
        # else:
        #     similar_users = []
        #     print("No similar user based on sentiment")
        
        # # Retrieve all purchased packages of similar users
        # similar_ordered_packages_init = OrderedPackage.objects.exclude(user=user).filter(user__in=similar_users).values_list('packageitem', flat=True)
        # print("Based on your review:")

        # if similar_ordered_packages_init:
        #     similar_ordered_packages = PackageItem.objects.filter(id__in=similar_ordered_packages_init[:8])
        #     print(similar_ordered_packages)
        #     print("from new")
        # else:
        #     # Retrieve previously stored packages from SentimentRecommendation
        #     sentiment_recommendation, created = SentimentRecommendation.objects.get_or_create(user=user)
        #     similar_ordered_packages = sentiment_recommendation.recommended_packages_s.all()
        #     print(similar_ordered_packages)
        #     print("from old packages")
        
        # # Create or update the sentiment recommendation model
        # sentiment_recommendation, created = SentimentRecommendation.objects.get_or_create(user=user)
        # sentiment_recommendation.recommended_packages_s.set(similar_ordered_packages)
        
       

        




        #end of sentiment analysis -2




        package = PackageItem.objects.filter(is_available=True)[:8]

        if get_or_set_current_location(request) is not None:
            pnt = GEOSGeometry('POINT(%s %s)' % (get_or_set_current_location(request)))
            vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=1000))
                                            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for v in vendors:
                v.kms = round(v.distance.km, 1)
        else:
            vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]

        context = {
            'is_customer': True,
            'user': request.user,
            'recommended_packages_cf': recommended_packages_cf,
            'package_items': package_items,
            'vendors': vendors,
            'package': package,
            'has_purchase_history': has_purchase_history,
            'recommended_packages': recommended_packages,
            'is_customer': (request.user.role == 'Customer'),
            'similar_ordered_packages':similar_ordered_packages,
            
        
            

        }

        return render(request, 'home.html', context)
    
    else:
        print("hello from new User")
        package = PackageItem.objects.filter(is_available=True)[:8]

        if get_or_set_current_location(request) is not None:
            pnt = GEOSGeometry('POINT(%s %s)' % (get_or_set_current_location(request)))
            vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=1000))
                                            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for v in vendors:
                v.kms = round(v.distance.km, 1)
        else:
            vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]

        context = {
            'is_customer': False,
            'user': request.user,
            'vendors': vendors,
            'package': package,
        }

        return render(request, 'home.html', context)
