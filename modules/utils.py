"""
Utility functions for file handling and output formatting
"""

import csv
from datetime import datetime
from typing import List, Dict

def save_to_csv(results: List[Dict], filename_prefix: str = "citation_analysis") -> str:
    """
    Save analysis results to CSV file
    Args:
        results: List of analysis result dictionaries
        filename_prefix: Base name for output file
    Returns:
        Path to generated CSV file
    """
    if not results:
        return ""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'article_title',
            'total_citations',
            'incomplete_citations', 
            'missing_fields',
            'problematic_citations'
        ])
        
        writer.writeheader()
        
        for item in results:
            problematic = "\n\n".join(
                [f"Missing: {prob['missing']}\n{prob['text']}" 
                 for prob in item['problems']]
            ) if item['problems'] else "None"
            
            writer.writerow({
                'article_title': item['title'],
                'total_citations': item['total'],
                'incomplete_citations': len(item['incomplete']),
                'missing_fields': "; ".join(set(item['incomplete'])),
                'problematic_citations': problematic
            })
    
    return filename

def display_article_analysis(title: str, analysis: Dict):
    """
    Print analysis results for a single article
    Args:
        title: Article title
        analysis: Analysis results dictionary
    """
    print(f"\n📄 Article: {title}")
    print(f"📊 Total citations: {analysis['total']}")
    print(f"⚠️ Incomplete citations: {len(analysis['incomplete'])}")
    
    if analysis['problems']:
        print("\nProblematic citations:")
        for i, problem in enumerate(analysis['problems'], 1):
            print(f"\n{i}. Missing: {problem['missing']}")
            print(problem['text'])
    else:
        print("✅ All citations are complete!")
    print("\n" + "-"*50)