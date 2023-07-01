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
#from marketplace.models import SentimentRecommendation


#rating_based
from django.db.models import Avg
from marketplace.views import ReviewRatingPackage




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
def preprocess_text(text):
    print(f"Input text type: {type(text)}")
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



# end for sentiment based-1



@login_required(login_url='login')
def home(request):

   # start colaborative recommendation from marketplace's recommend_packages
    
   # Get the user's cart items

    user_cart = Cart.objects.filter(user=request.user)
    user_cart_items = user_cart.values_list('packageitem__id', flat=True)
   

    # Find other users who have similar cart items
    similar_users = Cart.objects.filter(packageitem__in=user_cart_items).exclude(user=request.user)
    #similar_users_cart_items = similar_users.values_list('packageitem__id', flat=True)

    # Find the packages that are in the similar users' carts but not in the current user's cart
    #recommended_packages_cf =  PackageItem.objects.filter(id__in=similar_users_cart_items)[:8]
    # Save the collaborative recommendations for the user
    collaborative_recommendation, created = CollaborativeRecommendation.objects.get_or_create(user=request.user)
    

    similar_users_cart_items = Cart.objects.filter(user__in=similar_users.values_list('user')).exclude(user=request.user)
    recommended_packages_cf = PackageItem.objects.filter(cart__in=similar_users_cart_items).distinct()[:8]

    collaborative_recommendation.recommended_packages.set(recommended_packages_cf)
    # print(recommended_packages_cf)

   #end of  colaborative recommendation from marketplace's recommend_packages


    #start of for category==interest
    user = User.objects.get(email=request.user.email)
    user_interest = user.interest
    package_items = PackageItem.objects.filter(category__category_name=user_interest)
    # print(package_items)

  
   

    

    #end of  category==interest

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
                #print('hello')
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
                #print(similar_package_indices)

                # Exclude the purchased package itself
                similar_package_indices = similar_package_indices[similar_package_indices != purchased_package_index]

                # Get the recommended packages (at least 8 if available)
                recommended_packages = PackageItem.objects.filter(id__in=similar_package_indices[:8])
                print(recommended_packages)

                # Print the cosine similarity scores of the recommended packages
                for package_index in similar_package_indices[:8]:
                    similarity_score = similarity_scores[package_index]
                    print(f"Cosine similarity of package {package_index} is {similarity_score}")
                

        else:
            # Cosine similarity model file not found
            recommended_packages = []

    # Create or update the content recommendation model
    content_recommendation, created = ContentRecommendation.objects.get_or_create(user=user)
    content_recommendation.recommended_packages.set(recommended_packages)
    content_recommendation.save()

    

      #end of content based from 2 models 

# start for sentiment based-2
# #       # Get the current user
#     user = request.user

# #     # Load the sentiment analysis model
# #     # Define the absolute file path for the cosine similarity model
#     file_path = os.path.join(settings.BASE_DIR, 'marketplace', 'sentiment_model.pkl')

# #         
# #    # Check if the sentiment analysis model file exists
#     if os.path.exists(file_path):
# #         # Load the sentiment analysis model
#         with open(file_path, 'rb') as f:
#             sentiment_model = pickle.load(f)
#             print("Sentiment analysis model is successfully loaded.")
#             print("hello from sentiment")
           
#     else:
#         print("Error loading sentiment analysis model.")
#         print("bye from sentiment")

    
    
    
# #   

    

  

#     file_path = os.path.join(settings.BASE_DIR, 'marketplace', 'vectorizer.pkl')
# #    Check if the vectorizer model file exists
#     if os.path.exists(file_path):
# #         # Load the sentiment analysis model
#         with open(file_path, 'rb') as f:
#             vectorizer = pickle.load(f)
#             print("Svectorizer model is successfully loaded.")
           
           
#     else:
#         print("Error loading vectorizer model.")
#       # Get the latest review of the current user on a particular package
#     # Get the latest review of the current user on a particular package
#     latest_review = ReviewRatingPackage.objects.filter(user=user).latest('created_at')
#     print(latest_review)
#     current_user_review = preprocess_text(latest_review.review)
#     current_user_review_vectorized = vectorizer.transform([current_user_review])
#     current_user_sentiment = sentiment_model.predict(current_user_review_vectorized)[0]
#     #print(current_user_sentiment)

#    # Get all reviews on the same package by all users
#     package_reviews = ReviewRatingPackage.objects.filter(package=latest_review.package)

#     # Filter reviews with similar sentiments
#     similar_users = []
#     for review in package_reviews:
#         processed_review = preprocess_text(review.review)
#         review_vectorized = vectorizer.transform([processed_review])
#         sentiment = sentiment_model.predict(review_vectorized)[0]
#         if sentiment == current_user_sentiment:
#             similar_users.append(review.user)
#     # Retrieve all purchased packages of similar users
#     # Retrieve all purchased packages of similar users
#     similar_ordered_packages = OrderedPackage.objects.exclude(user=user).filter(user__in=similar_users).values_list('packageitem', flat=True)

#     print(similar_ordered_packages)

#     # Create or update the sentiment recommendation model
#     sentiment_recommendation, created = SentimentRecommendation.objects.get_or_create(user=user)
#     sentiment_recommendation.recommended_packages_s.set(similar_ordered_packages)
   

    
    
# end for sentiment based-2






    package=PackageItem.objects.filter(is_available=True)[:8]
    # Get all packages with their average ratings greater than 3.5
    packages_with_avg_ratings = PackageItem.objects.annotate(average_rating=Avg('reviewratingpackage__rating'))
    filtered_packages = packages_with_avg_ratings.filter(average_rating__gte=3)

    for package in filtered_packages:
        print(f"Package: {package},Package ID: {package.id}, Average Rating: {package.average_rating}")

# Sort the packages in descending order based on average ratings
    sorted_packages = filtered_packages.order_by('-average_rating')

   

    if get_or_set_current_location(request) is not None:
    

        pnt = GEOSGeometry('POINT(%s %s)' % (get_or_set_current_location(request)))
        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=1000))
                ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
            
        for v in vendors:
            v.kms = round(v.distance.km, 1)
    
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]

    
    context = {
        'is_customer': (request.user.role == 'Customer'),
        'user': request.user, 
        'vendors': vendors,
        'package': package,
        'recommended_packages_cf': recommended_packages_cf,
        'package_items': package_items,
        'recommended_packages': recommended_packages,
        'has_purchase_history': has_purchase_history, 
        'sorted_packages': sorted_packages,
        #'recommended_packages_s': sentiment_recommendation.recommended_packages_s.all()
          
         
    }
    if request.user.is_authenticated:
        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html',context)