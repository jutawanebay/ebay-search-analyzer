from collections import Counter
from typing import List, Dict, Optional, Tuple
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import sys
from statistics import mean, median

# Download required NLTK data at startup
print("Downloading required NLTK data...")
try:
    # Download required packages
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    print("Successfully downloaded NLTK data")
except Exception as e:
    print(f"Error downloading NLTK data: {str(e)}", file=sys.stderr)
    raise

def preprocess_text(text: str) -> List[str]:
    """
    Preprocess text by converting to lowercase, removing punctuation,
    and filtering out stopwords and non-alphabetic tokens
    """
    try:
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Simple word splitting as fallback if NLTK tokenization fails
        try:
            tokens = word_tokenize(text)
        except Exception as e:
            print(f"Warning: NLTK tokenization failed, using simple split: {str(e)}")
            tokens = text.split()

        # Get English stopwords
        try:
            stop_words = set(stopwords.words('english'))
        except Exception as e:
            print(f"Warning: Could not load stopwords, using basic set: {str(e)}")
            stop_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for',
                         'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on',
                         'that', 'the', 'to', 'was', 'were', 'will', 'with'}

        # Add custom stopwords relevant to eBay listings
        custom_stopwords = {
            'new', 'brand', 'lot', 'free', 'shipping', 'sale', 'sealed',
            'uk', 'us', 'box', 'set', 'edition', 'complete', 'original'
        }
        stop_words.update(custom_stopwords)

        # Filter tokens
        tokens = [
            token for token in tokens
            if token.isalpha()  # Only alphabetic tokens
            and len(token) > 2  # Longer than 2 characters
            and token not in stop_words  # Not a stopword
        ]

        return tokens
    except Exception as e:
        print(f"Error during text preprocessing: {str(e)}", file=sys.stderr)
        return []

def analyze_keywords(titles: List[str]) -> Dict[str, int]:
    """
    Analyze keyword frequency in a list of titles
    """
    try:
        # Combine all titles
        all_text = ' '.join(titles)

        # Preprocess and tokenize
        tokens = preprocess_text(all_text)

        # Count frequencies
        keyword_freq = Counter(tokens)

        # Convert to dictionary and sort by frequency
        return dict(sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True))
    except Exception as e:
        print(f"Error during keyword analysis: {str(e)}", file=sys.stderr)
        return {}

def suggest_title(keyword_freq: Dict[str, int], max_length: int = 80) -> str:
    """
    Generate a suggested title based on keyword frequency analysis
    with optimized character usage within the 80-char limit
    """
    try:
        # Get more keywords than we might need to have options
        top_keywords = list(keyword_freq.items())[:10]  # Get top 10 instead of 5

        # Sort keywords by frequency
        sorted_keywords = sorted(top_keywords, key=lambda x: x[1], reverse=True)

        # Build title starting with most frequent keywords
        title_parts = []
        current_length = 0

        for keyword, freq in sorted_keywords:
            # Calculate length with spacing and potential comma
            word_length = len(keyword)
            space_needed = 1 if title_parts else 0  # Space needed if not first word
            comma_needed = 1 if title_parts else 0  # Comma needed if not first word
            total_addition = word_length + space_needed + comma_needed

            # Check if adding this word would exceed the limit
            if current_length + total_addition <= max_length:
                # Add appropriate spacing and punctuation
                if title_parts:
                    title_parts.append(", ")
                    current_length += 2  # Length of ", "

                title_parts.append(keyword.title())  # Capitalize each word
                current_length += word_length
            else:
                break

        # Join all parts
        title = "".join(title_parts)

        # If we have room, add some common eBay terms if title is too short
        if len(title) < max_length - 15:  # Leave room for suffix
            common_suffixes = [" - New", " - Lot", " - Sale"]
            for suffix in common_suffixes:
                if len(title) + len(suffix) <= max_length:
                    title += suffix
                    break

        return title
    except Exception as e:
        print(f"Error generating title suggestion: {str(e)}", file=sys.stderr)
        return "Could not generate title suggestion"

def calculate_price_stats(prices: List[float]) -> Dict[str, float]:
    """
    Calculate price statistics from the listings
    """
    try:
        # Filter out None values
        valid_prices = [p for p in prices if p is not None]

        if not valid_prices:
            return {
                'average': 0.0,
                'median': 0.0,
                'min': 0.0,
                'max': 0.0
            }

        return {
            'average': round(mean(valid_prices), 2),
            'median': round(median(valid_prices), 2),
            'min': round(min(valid_prices), 2),
            'max': round(max(valid_prices), 2)
        }
    except Exception as e:
        print(f"Error calculating price statistics: {str(e)}", file=sys.stderr)
        return {
            'average': 0.0,
            'median': 0.0,
            'min': 0.0,
            'max': 0.0
        }