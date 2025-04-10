"""
Configuration settings for Wikipedia Citation Analyzer
"""

import os

class Config:
    # API Configuration
    API_URL = "https://en.wikipedia.org/w/api.php"
    USER_AGENT = "CitationAnalyzerBot/1.0"
    REQUEST_DELAY = 0.3  # Seconds between API requests
    
    # Bot Credentials (set via environment variables)
    BOT_USERNAME = os.getenv('WIKI_BOT_USERNAME')
    BOT_PASSWORD = os.getenv('WIKI_BOT_PASSWORD')
    
    # Processing Limits
    MAX_ARTICLES = 2000
    BATCH_SIZE = 50  # Articles per API request