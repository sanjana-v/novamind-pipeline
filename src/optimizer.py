import os
from typing import Dict, List
from anthropic import Anthropic

class ContentOptimizer:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None
    
    def suggest_improvements(self, content: str, performance_data: Dict) -> Dict:
        if not self.client:
            return {
                'suggestions': [
                    "Add more specific examples",
                    "Include data and statistics",
                    "Strengthen call-to-action"
                ],
                'confidence': 0.7
            }
        
        prompt = f"""Review this newsletter content and suggest improvements based on performance data:

Content:
{content}

Performance:
- Open rate: {performance_data.get('open_rate', 0)}%
- Click rate: {performance_data.get('click_rate', 0)}%

Provide 3-5 specific, actionable suggestions to improve engagement. Focus on:
1. Subject line optimization
2. Content structure
3. Call-to-action effectiveness
4. Personalization opportunities

Format as a numbered list."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            suggestions_text = message.content[0].text
            suggestions = [
                line.strip() for line in suggestions_text.split('\n')
                if line.strip() and line[0].isdigit()
            ]
            
            return {
                'suggestions': suggestions,
                'confidence': 0.85
            }
            
        except Exception as e:
            print(f"Error generating suggestions: {str(e)}")
            return {
                'suggestions': ["Could not generate suggestions"],
                'confidence': 0.0
            }
    
    def optimize_subject_line(self, subject: str, target_persona: str) -> List[str]:
        if not self.client:
            return [
                f"[Optimized] {subject}",
                f"[Improved] {subject}",
                f"[Enhanced] {subject}"
            ]
        
        prompt = f"""Optimize this email subject line for {target_persona}:

Original: {subject}

Create 3 variations that:
1. Are more engaging and clickable
2. Use proven email marketing techniques
3. Stay under 60 characters
4. Appeal specifically to {target_persona}

Return just the 3 subject lines, numbered."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = message.content[0].text
            variations = []
            
            for line in response.split('\n'):
                if line.strip() and line[0].isdigit():
                    variations.append(line.split('. ', 1)[1] if '. ' in line else line)
            
            return variations[:3]
            
        except Exception as e:
            print(f"Error optimizing subject: {str(e)}")
            return [subject]