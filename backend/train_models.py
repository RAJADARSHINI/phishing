"""
Model Training Script for Phishing Detection

This script:
1. Loads email spam and URL phishing datasets
2. Preprocesses the data (cleaning, tokenization)
3. Converts text to numeric features using TF-IDF
4. Trains Logistic Regression and Random Forest models
5. Saves trained models and vectorizers to disk
"""

import pandas as pd
import numpy as np
import re
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')


class TextPreprocessor:
    """Handles text preprocessing for emails and URLs"""
    
    @staticmethod
    def clean_email(text):
        """
        Clean email text by removing extra whitespace and normalizing
        """
        if pd.isna(text):
            return ""
        text = str(text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might cause issues (keep basic punctuation)
        text = text.strip()
        return text
    
    @staticmethod
    def clean_url(url):
        """
        Clean URL text
        """
        if pd.isna(url):
            return ""
        url = str(url)
        # Remove newlines and extra whitespace
        url = re.sub(r'\s+', ' ', url)
        # Remove quotes if present
        url = url.strip('"\'')
        return url.strip()
    
    @staticmethod
    def extract_url_features(url):
        """
        Extract basic features from URL for additional context
        Returns the URL as-is for now (can be extended with domain, path features)
        """
        return url


def load_and_preprocess_data():
    """
    Load CSV files and preprocess the data
    Returns: (email_data, url_data) tuples of (text, labels)
    """
    print("Loading datasets...")
    
    # Load email spam dataset
    email_path = 'data/enron_spam.csv'
    if not os.path.exists(email_path):
        print(f"Warning: {email_path} not found. Creating dummy dataset for testing.")
        # Create dummy data if file doesn't exist
        email_data = pd.DataFrame({
            'text': [
                'Click here to claim your prize!',
                'Meeting scheduled for tomorrow at 3pm',
                'You have won $1000000! Click now!',
                'Project update: Status is on track',
                'URGENT: Verify your account immediately',
                'Thanks for your email, I will review it',
            ],
            'labels': [1, 0, 1, 0, 1, 0]
        })
    else:
        email_data = pd.read_csv(email_path)
        # Handle different column name variations
        if 'label' in email_data.columns:
            email_data['labels'] = email_data['label']
        elif 'spam' in email_data.columns:
            email_data['labels'] = email_data['spam']
    
    # Load URL phishing dataset
    url_paths = [
        'data/phishing_sites.csv',
        '../phishing_sites.csv',
        '../../phishing_sites.csv',
        os.path.join(os.path.dirname(__file__), '..', 'phishing_sites.csv')
    ]
    
    url_data = None
    for url_path in url_paths:
        if os.path.exists(url_path):
            print(f"Found URL dataset at: {url_path}")
            url_data = pd.read_csv(url_path)
            break
    
    if url_data is None:
        print(f"Warning: phishing_sites.csv not found in expected locations.")
        print("Please place phishing_sites.csv in the data/ directory or project root.")
        url_data = None
    else:
        # Handle different column name variations
        if 'label' in url_data.columns:
            url_data['labels'] = url_data['label']
        elif 'phishing' in url_data.columns:
            url_data['labels'] = url_data['phishing']
    
    # Preprocess email data
    print("Preprocessing email data...")
    preprocessor = TextPreprocessor()
    
    if email_data is not None and 'text' in email_data.columns:
        email_data['cleaned_text'] = email_data['text'].apply(preprocessor.clean_email)
        email_texts = email_data['cleaned_text'].tolist()
        email_labels = email_data['labels'].tolist()
    else:
        email_texts = []
        email_labels = []
    
    # Preprocess URL data
    print("Preprocessing URL data...")
    if url_data is not None and 'text' in url_data.columns:
        url_data['cleaned_text'] = url_data['text'].apply(preprocessor.clean_url)
        url_texts = url_data['cleaned_text'].tolist()
        url_labels = url_data['labels'].tolist()
    else:
        url_texts = []
        url_labels = []
    
    return (email_texts, email_labels), (url_texts, url_labels)


def train_email_model(email_texts, email_labels):
    """
    Train model for email spam detection
    """
    print("\n" + "="*50)
    print("Training Email Spam Detection Model")
    print("="*50)
    
    if len(email_texts) == 0:
        print("No email data available. Creating dummy model.")
        # Create a simple dummy model
        email_texts = [
            'spam email click here',
            'normal email meeting',
            'spam urgent verify',
            'normal project update'
        ]
        email_labels = [1, 0, 1, 0]
    
    # Create TF-IDF vectorizer
    print("Creating TF-IDF features...")
    email_vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        stop_words='english'
    )
    
    # Transform texts to features
    X_email = email_vectorizer.fit_transform(email_texts)
    y_email = np.array(email_labels)
    
    print(f"Feature matrix shape: {X_email.shape}")
    print(f"Number of spam emails: {sum(y_email)}")
    print(f"Number of normal emails: {len(y_email) - sum(y_email)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_email, y_email, test_size=0.2, random_state=42, stratify=y_email
    )
    
    # Train Logistic Regression
    print("\nTraining Logistic Regression model...")
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    lr_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = lr_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Logistic Regression Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Spam']))
    
    # Train Random Forest (as alternative)
    print("\nTraining Random Forest model...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    
    y_pred_rf = rf_model.predict(X_test)
    accuracy_rf = accuracy_score(y_test, y_pred_rf)
    print(f"Random Forest Accuracy: {accuracy_rf:.4f}")
    
    # Use the better model (or Logistic Regression by default for speed)
    selected_model = lr_model
    print(f"\nSelected model: Logistic Regression (accuracy: {accuracy:.4f})")
    
    return selected_model, email_vectorizer


def train_url_model(url_texts, url_labels):
    """
    Train model for URL phishing detection
    """
    print("\n" + "="*50)
    print("Training URL Phishing Detection Model")
    print("="*50)
    
    if len(url_texts) == 0:
        print("No URL data available. Creating dummy model.")
        url_texts = [
            'http://paypal-security-verify.com',
            'https://www.paypal.com/login',
            'http://bank-verify-now.com',
            'https://www.bankofamerica.com'
        ]
        url_labels = [1, 0, 1, 0]
    
    # Create TF-IDF vectorizer for URLs
    print("Creating TF-IDF features...")
    url_vectorizer = TfidfVectorizer(
        max_features=3000,
        ngram_range=(1, 3),  # Use character n-grams for URLs
        analyzer='char_wb',  # Character-based n-grams
        min_df=2,
        max_df=0.95
    )
    
    # Transform URLs to features
    X_url = url_vectorizer.fit_transform(url_texts)
    y_url = np.array(url_labels)
    
    print(f"Feature matrix shape: {X_url.shape}")
    print(f"Number of phishing URLs: {sum(y_url)}")
    print(f"Number of safe URLs: {len(y_url) - sum(y_url)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_url, y_url, test_size=0.2, random_state=42, stratify=y_url
    )
    
    # Train Logistic Regression
    print("\nTraining Logistic Regression model...")
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    lr_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = lr_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Logistic Regression Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Safe', 'Phishing']))
    
    # Train Random Forest
    print("\nTraining Random Forest model...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    
    y_pred_rf = rf_model.predict(X_test)
    accuracy_rf = accuracy_score(y_test, y_pred_rf)
    print(f"Random Forest Accuracy: {accuracy_rf:.4f}")
    
    # Use Logistic Regression by default
    selected_model = lr_model
    print(f"\nSelected model: Logistic Regression (accuracy: {accuracy:.4f})")
    
    return selected_model, url_vectorizer


def save_models(email_model, email_vectorizer, url_model, url_vectorizer):
    """
    Save trained models and vectorizers to disk
    """
    print("\n" + "="*50)
    print("Saving Models")
    print("="*50)
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save email model and vectorizer
    with open('models/email_model.pkl', 'wb') as f:
        pickle.dump(email_model, f)
    print("Saved: models/email_model.pkl")
    
    with open('models/email_vectorizer.pkl', 'wb') as f:
        pickle.dump(email_vectorizer, f)
    print("Saved: models/email_vectorizer.pkl")
    
    # Save URL model and vectorizer
    with open('models/url_model.pkl', 'wb') as f:
        pickle.dump(url_model, f)
    print("Saved: models/url_model.pkl")
    
    with open('models/url_vectorizer.pkl', 'wb') as f:
        pickle.dump(url_vectorizer, f)
    print("Saved: models/url_vectorizer.pkl")
    
    print("\nAll models saved successfully!")


def main():
    """
    Main training pipeline
    """
    print("="*50)
    print("Phishing Detection Model Training")
    print("="*50)
    
    # Load and preprocess data
    (email_texts, email_labels), (url_texts, url_labels) = load_and_preprocess_data()
    
    # Train email model
    email_model, email_vectorizer = train_email_model(email_texts, email_labels)
    
    # Train URL model
    url_model, url_vectorizer = train_url_model(url_texts, url_labels)
    
    # Save models
    save_models(email_model, email_vectorizer, url_model, url_vectorizer)
    
    print("\n" + "="*50)
    print("Training Complete!")
    print("="*50)


if __name__ == '__main__':
    main()
