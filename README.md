Twitter Content Analysis Web Application
This project is a web application that analyzes Twitter content (tweets and images) to identify potential hate speech or offensive content. It provides an intuitive web interface for users to enter a Twitter username and receive an analysis report.

Features
-> Twitter Content Retrieval: Fetches tweets from specified Twitter accounts using the Twitter API
-> Text Analysis: Analyzes tweet text for potential hate speech using a keyword-based classifier
-> Image Analysis: Performs basic classification of images attached to tweets
-> Summary Statistics: Generates summary metrics for the analyzed content
-> Web Interface: Provides a clean, user-friendly interface for accessing the analysis

Technology Stack
-> Backend: Python with Flask web framework
-> Data Processing: NumPy, Pandas
-> Image Processing: PIL (Python Imaging Library)
-> API Integration: Tweepy (Twitter API client)
-> Visualization: Matplotlib
-> Frontend: HTML, CSS, JavaScript (through Flask templates)

Getting Started
Prerequisites
-> Python 3.8 or higher
-> Twitter Developer Account with API access

Installation
Clone this repository:
git clone https://github.com/MananJK/Twitter-X-Hate-Speech-Detector.git
cd twitter-content-analysis

Create a virtual environment and activate it:
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

Install the required dependencies:
pip install -r requirements.txt

Replace the Twitter API credentials in app.py with your own:
consumer_key = "your-consumer-key"
consumer_secret = "your-consumer-secret"
access_token = "your-access-token"
access_token_secret = "your-access-token-secret"
bearer_token = "your-bearer-token"

Running the Application
1. Start the Flask development server:
   python appgit.py

2. Open your web browser and navigate to:
   http://127.0.0.1:5000/

3. Enter a Twitter username (with or without the @ symbol) and click "Analyze" to see the results.

How It Works
Text Classification
The application uses a keyword-based approach to classify text:

1. It preprocesses text by removing URLs, mentions, hashtags, and special characters
2. It counts occurrences of predefined positive and negative words
3. It calculates sentiment scores based on word counts
4. It maps sentiment scores to content categories (normal, offensive, hate speech)

Image Classification
The current implementation uses a simple placeholder classifier that:

1. Verifies image accessibility by downloading it
2. Returns a default "normal" classification
3. Could be extended to use more sophisticated image classification in the future

Project Structure:
twitter-content-analysis/
├── app.py              # Main application file with Flask routes and logic
├── templates/          # HTML templates for the web interface
│   └── index.html      # Main page template
├── static/             # Static assets (CSS, JS, images)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation

Future Improvements
-> Implement more sophisticated text classification using machine learning models
-> Add actual image classification capability for better accuracy
-> Expand analysis to include other social media platforms
-> Add user authentication for saved reports
-> Implement caching to improve performance for repeated analyses

Acknowledgments
Twitter for providing the API access
Flask and Python communities for excellent documentation
All the open-source libraries that made this project possible
