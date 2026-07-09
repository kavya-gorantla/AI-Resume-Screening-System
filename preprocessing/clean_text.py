import re
import string
import nltk
from nltk.corpus import stopwords

def clean_text(text):
    """
    Cleans raw text extracted from resumes or JDs.
    - Lowercases text
    - Removes URLs
    - Removes punctuation and special characters
    - Removes extra whitespaces
    - Removes stop words
    """
    if not text:
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text, flags=re.MULTILINE)
    
    # Remove emails (optional, but usually we want to extract them first)
    # text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters and punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove newlines and extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove stopwords
    try:
        stop_words = set(stopwords.words('english'))
        tokens = text.split()
        filtered_text = [word for word in tokens if word not in stop_words]
        text = ' '.join(filtered_text)
    except Exception as e:
        # Fallback if stopwords aren't downloaded
        pass
    
    return text
