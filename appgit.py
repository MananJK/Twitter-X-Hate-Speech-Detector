import os
import tweepy
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
import requests
import re
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Twitter API credentials - replace with your own
consumer_key = "Your consumer key"
consumer_secret = "Your consumer secret"
access_token = "Your access token"
access_token_secret = "Your access token secret"
bearer_token = "Your bearer token"

# Set up Twitter API client
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# Mock text classifier that doesn't use transformers
class MockTextClassifier:
    def __init__(self):
        # Define sentiment keywords
        self.negative_words = ['bad', 'awful', 'terrible', 'hate', 'dislike', 'angry', 'sad', 'disappointed', 'hurt', 'pain']
        self.positive_words = ['good', 'great', 'excellent', 'love', 'like', 'happy', 'joy', 'wonderful', 'amazing', 'fantastic']
    
    def preprocess(self, text):
        # Convert to lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Remove user mentions
        text = re.sub(r'@\w+', '', text)
        # Remove hashtags
        text = re.sub(r'#\w+', '', text)
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def classify(self, text):
        processed_text = self.preprocess(text)
        words = processed_text.split()
        
        # Count positive and negative words
        negative_count = sum(1 for word in words if word in self.negative_words)
        positive_count = sum(1 for word in words if word in self.positive_words)
        
        # Calculate sentiment scores
        total_words = len(words) if len(words) > 0 else 1
        negative_score = negative_count / total_words
        positive_score = positive_count / total_words
        neutral_score = 1.0 - (negative_score + positive_score)
        
        # Ensure scores are positive and sum to 1
        total_score = negative_score + positive_score + neutral_score
        if total_score > 0:
            negative_score /= total_score
            positive_score /= total_score
            neutral_score /= total_score
        
        # Determine label
        if negative_score > positive_score and negative_score > neutral_score:
            mapped_label = 'hate_speech'
            confidence = negative_score
        elif positive_score > negative_score and positive_score > neutral_score:
            mapped_label = 'normal'
            confidence = positive_score
        else:
            mapped_label = 'normal'
            confidence = neutral_score
        
        return {
            "label": mapped_label,
            "confidence": float(confidence),
            "scores": {
                "hate_speech": float(negative_score),
                "normal": float(positive_score + neutral_score),
                "offensive": 0.0  # not detected by this model
            }
        }

# Simple image classifier
class SimpleImageClassifier:
    def __init__(self):
        self.labels = ["normal", "offensive", "hate_speech"]
    
    def classify(self, image_url):
        try:
            # Download image to verify it exists and is accessible
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            
            # Return a default "normal" classification
            return {
                "label": "normal",
                "confidence": 0.9,
                "scores": {
                    "normal": 0.9,
                    "offensive": 0.05,
                    "hate_speech": 0.05
                }
            }
        except Exception as e:
            print(f"Error classifying image: {e}")
            return {
                "label": "error",
                "confidence": 0.0,
                "scores": {},
                "error": str(e)
            }

# Initialize classifiers
text_classifier = MockTextClassifier()
image_classifier = SimpleImageClassifier()

# Function to get tweets
def get_user_tweets(username, count=50):
    try:
        # Get user ID
        user = client.get_user(username=username, user_fields=["profile_image_url"])
        if not user.data:
            return []
        user_id = user.data.id
        
        # Get tweets
        tweets = client.get_users_tweets(
            id=user_id,
            max_results=count,
            tweet_fields=["created_at", "public_metrics", "entities"],
            expansions=["attachments.media_keys"],
            media_fields=["url", "preview_image_url"]
        )
        
        # Process tweets
        results = []
        media_dict = {}
        
        if hasattr(tweets, 'includes') and "media" in tweets.includes:
            for media in tweets.includes["media"]:
                media_dict[media.media_key] = media
        
        if hasattr(tweets, 'data') and tweets.data:
            for tweet in tweets.data:
                tweet_data = {
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "metrics": tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                    "media": []
                }
                
                # Get media
                if hasattr(tweet, "attachments") and hasattr(tweet.attachments, "media_keys"):
                    for media_key in tweet.attachments.media_keys:
                        if media_key in media_dict:
                            media = media_dict[media_key]
                            media_url = getattr(media, "url", None) or getattr(media, "preview_image_url", None)
                            if media_url:
                                tweet_data["media"].append(media_url)
                
                results.append(tweet_data)
        
        return results
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return []

# Function to analyze tweets
def analyze_tweets(username, count=50):
    tweets = get_user_tweets(username, count)
    results = []
    
    for tweet in tweets:
        # Analyze text
        text_result = text_classifier.classify(tweet["text"])
        
        # Analyze images
        image_results = []
        for media_url in tweet.get("media", []):
            image_result = image_classifier.classify(media_url)
            image_results.append({
                "url": media_url,
                "result": image_result
            })
        
        results.append({
            "tweet_id": tweet["id"],
            "text": tweet["text"],
            "created_at": tweet["created_at"],
            "text_analysis": text_result,
            "image_analysis": image_results
        })
    
    # Summarize results
    summary = {
        "total_tweets": len(results),
        "hate_speech": sum(1 for tweet in results if tweet["text_analysis"]["label"] == "hate_speech"),
        "offensive": sum(1 for tweet in results if tweet["text_analysis"]["label"] == "offensive"),
        "normal": sum(1 for tweet in results if tweet["text_analysis"]["label"] == "normal"),
        "tweets_with_images": sum(1 for tweet in results if tweet["image_analysis"]),
        "hate_speech_images": sum(1 for tweet in results 
                                  for img in tweet["image_analysis"] 
                                  if img["result"]["label"] == "hate_speech"),
        "offensive_images": sum(1 for tweet in results 
                               for img in tweet["image_analysis"] 
                               if img["result"]["label"] == "offensive"),
    }
    
    return {
        "username": username,
        "summary": summary,
        "tweets": results
    }

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    username = request.form.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    # Remove @ symbol if present
    username = username.strip('@')
    
    try:
        result = analyze_tweets(username)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)