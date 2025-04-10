"""
Handles all interactions with Wikipedia's API
"""

import time
import requests
from typing import Dict, List
from config import Config

class WikipediaAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.USER_AGENT})
        
    def authenticate(self):
        """
        Authenticate with Wikipedia using bot credentials
        Raises Exception if authentication fails
        """
        print("\n🔐 Authenticating bot...")
        try:
            if not Config.BOT_USERNAME or not Config.BOT_PASSWORD:
                raise Exception("Missing bot credentials. Set WIKI_BOT_USERNAME and WIKI_BOT_PASSWORD environment variables.")

            token_params = {
                'action': 'query',
                'meta': 'tokens',
                'type': 'login',
                'format': 'json'
            }
            token_response = self.session.get(Config.API_URL, params=token_params).json()
            login_token = token_response['query']['tokens']['logintoken']

            auth_params = {
                'action': 'login',
                'lgname': Config.BOT_USERNAME,
                'lgpassword': Config.BOT_PASSWORD,
                'lgtoken': login_token,
                'format': 'json'
            }
            
            login_response = self.session.post(Config.API_URL, data=auth_params).json()
            if login_response.get('login', {}).get('result') != 'Success':
                raise Exception("❌ Bot login failed. Check credentials.")
            print("✅ Authentication successful\n")
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            raise
    
    def make_request(self, params: Dict, max_retries=3) -> Dict:
        """
        Make API request with rate limiting and retries
        Args:
            params: API parameters
            max_retries: Maximum attempts before failing
        Returns:
            JSON response data
        """
        for attempt in range(max_retries):
            try:
                time.sleep(Config.REQUEST_DELAY)
                params['format'] = 'json'
                response = self.session.post(Config.API_URL, data=params)
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    print(f"⏳ Rate limited. Waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                print(f"⚠️ Attempt {attempt+1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep((attempt + 1) * 2)
    
    def get_article_batch(self, titles: List[str]) -> Dict[str, str]:
        """
        Fetch content for multiple articles in one request
        Args:
            titles: List of article titles
        Returns:
            Dictionary of {title: content} pairs
        """
        params = {
            'action': 'query',
            'prop': 'revisions',
            'rvprop': 'content',
            'rvslots': 'main',
            'titles': '|'.join(titles),
            'format': 'json',
            'formatversion': '2'
        }
        
        data = self.api_request(params)
        results = {}
        for page in data.get('query', {}).get('pages', []):
            if 'missing' not in page:
                results[page['title']] = page['revisions'][0]['slots']['main']['content']
        return results
    
    def find_articles_using_template(self, template: str, limit: int) -> List[str]:
        """
        Find articles using a specific template
        Args:
            template: Template name (e.g., 'Cite_web')
            limit: Maximum articles to return
        Returns:
            List of article titles
        """
        articles = []
        params = {
            'action': 'query',
            'list': 'embeddedin',
            'eititle': f'Template:{template}',
            'eilimit': Config.BATCH_SIZE,
            'format': 'json'
        }
    
        while len(articles) < limit:
            data = self.make_request(params)
            new_articles = [page['title'] for page in data.get('query', {}).get('embeddedin', [])]
            articles.extend(new_articles)
            
            if 'continue' not in data or len(articles) >= limit:
                break
                
            params.update(data['continue'])
    
        return articles[:limit]