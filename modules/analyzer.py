"""
Core citation analysis functionality
"""

import re
from typing import Dict, List

class CitationAnalyzer:
    @staticmethod
    def analyze(wikitext: str) -> Dict:
        """
        Analyze wikitext for incomplete citations
        Args:
            wikitext: Article content to analyze
        Returns:
            Dictionary with analysis results:
            {
                'total': Total citations found,
                'incomplete': List of missing fields,
                'problems': Detailed citation issues
            }
        """
        if not wikitext:
            return {'total': 0, 'incomplete': [], 'problems': []}

        wikitext = wikitext.replace("{{!}}", "|").replace("{{pipe}}", "|")
        citations = re.findall(
            r"\{\{\s*Cite\s+web\s*\|([^{}]*?(?:\{[^{}]*\}[^{}]*)*)\}\}", 
            wikitext, 
            re.IGNORECASE | re.DOTALL
        )

        results = {
            'total': len(citations),
            'incomplete': [],
            'problems': []
        }

        for citation in citations:
            missing = []
            text = citation.lower().replace(" ", "")

            # Check for required fields
            if not re.search(r"title\s*=", text):
                missing.append("title")
            if not re.search(r"url\s*=", text):
                missing.append("url")

            if missing:
                results['incomplete'].append(", ".join(missing))
                results['problems'].append({
                    'missing': ", ".join(missing),
                    'text': f"{{{{Cite web|{citation}}}}}"
                })

        return results