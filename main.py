"""
Wikipedia Citation Analyzer - Main Entry Point
"""

from modules.wikipedia_api import WikipediaAPI
from modules.analyzer import CitationAnalyzer
from modules.utils import save_to_csv, display_article_analysis
from modules.config import Config 

def main_menu():
    """Display the ascii art, main menu and handle user input"""
    print(r"""
+-----------------------------------------------+
|  🔍 Wikipedia Citation Analyzer (CLI Edition) |
+-----------------------------------------------+
|  • Bot-authenticated API access              |
|  • Scans for incomplete Cite web templates   |
|  • Processes multiple articles               |
|  • CSV export capability                     |
+-----------------------------------------------+
""")
    
    print("\n" + "="*50)
    print("1. Scan random articles using Cite web template (CSV export)")
    print("2. Analyze specific articles (screen output only)")
    print("3. Exit")
    return input("\nChoose option (1-3): ").strip()

def analyze_specific_articles(api: WikipediaAPI):
    """
    Analyze user-provided articles and display results
    Args:
        api: Authenticated WikipediaAPI instance
    """
    print("\nEnter article titles (one per line, blank line to finish):")
    articles = []
    while True:
        article = input("> ").strip()
        if not article:
            break
        articles.append(article)
    
    if not articles:
        print("\nNo articles entered.")
        return
    
    print(f"\n🔍 Analyzing {len(articles)} articles...")
    
    for i in range(0, len(articles), Config.BATCH_SIZE):
        batch = articles[i:i + Config.BATCH_SIZE]
        wikitexts = api.get_article_batch(batch)
        
        for title, text in wikitexts.items():
            analysis = CitationAnalyzer.analyze(text)
            display_article_analysis(title, analysis)

def analyze_random_articles(api: WikipediaAPI):
    """
    Analyze random articles using Cite web template and save to CSV
    Args:
        api: Authenticated WikipediaAPI instance
    """
    limit = int(input(f"\nHow many articles to scan? (Max {Config.MAX_ARTICLES}): ") or "100")
    limit = min(limit, Config.MAX_ARTICLES)
    
    articles = api.find_articles_using_template("Cite_web", limit)
    results = []
    
    for i in range(0, len(articles), Config.BATCH_SIZE):
        batch = articles[i:i + Config.BATCH_SIZE]
        wikitexts = api.get_article_batch(batch)
        
        for title, text in wikitexts.items():
            analysis = CitationAnalyzer.analyze(text)
            if analysis['incomplete']:
                results.append({'title': title, **analysis})
    
    if results:
        filename = save_to_csv(results)
        print(f"\n📁 Results saved to: {filename}")
    else:
        print("\nNo incomplete citations found.")

def main():
    """Main execution flow"""
    try:
        api = WikipediaAPI()
        api.authenticate()
        
        while True:
            choice = main_menu()
            
            if choice == "1":
                analyze_random_articles(api)
            elif choice == "2":
                analyze_specific_articles(api)
            elif choice == "3":
                print("\nThank you for using Wikipedia Citation Analyzer!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()