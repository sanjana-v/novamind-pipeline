import os
import json
from typing import Dict, List
from anthropic import Anthropic
from datetime import datetime

class AnalyticsEngine:
    def __init__(self, db):
        self.db = db
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None
    
    def analyze_campaign_performance(self, campaign_id: int, 
                                    metrics_by_persona: Dict[str, Dict]) -> Dict:
        print(f"\n Analyzing campaign performance...")
        
        total_sent = sum(m['sent'] for m in metrics_by_persona.values())
        total_opens = sum(m['opens'] for m in metrics_by_persona.values())
        total_clicks = sum(m['clicks'] for m in metrics_by_persona.values())
        
        avg_open_rate = sum(m['open_rate'] for m in metrics_by_persona.values()) / len(metrics_by_persona)
        avg_click_rate = sum(m['click_rate'] for m in metrics_by_persona.values()) / len(metrics_by_persona)
        
        # Find best performing persona
        best_persona = max(metrics_by_persona.items(), 
                          key=lambda x: x[1]['click_rate'])
        worst_persona = min(metrics_by_persona.items(), 
                           key=lambda x: x[1]['click_rate'])
        
        analysis = {
            'summary': {
                'total_sent': total_sent,
                'total_opens': total_opens,
                'total_clicks': total_clicks,
                'avg_open_rate': round(avg_open_rate, 2),
                'avg_click_rate': round(avg_click_rate, 2)
            },
            'best_performer': {
                'persona': best_persona[0],
                'click_rate': best_persona[1]['click_rate']
            },
            'worst_performer': {
                'persona': worst_persona[0],
                'click_rate': worst_persona[1]['click_rate']
            }
        }
        
        # Generate AI insights
        if self.client:
            insights = self.generate_ai_insights(metrics_by_persona, analysis)
            analysis['ai_insights'] = insights
        else:
            analysis['ai_insights'] = self.generate_basic_insights(analysis)
        
        print(f"✅ Analysis complete")
        return analysis
    
    def generate_ai_insights(self, metrics: Dict[str, Dict], analysis: Dict) -> str:
        print("🤖 Generating AI-powered insights...")
        
        metrics_text = "\n".join([
            f"- {persona}: {data['open_rate']}% open rate, {data['click_rate']}% click rate"
            for persona, data in metrics.items()
        ])
        
        prompt = f"""Analyze this email campaign performance data and provide actionable insights:

Campaign Metrics by Persona:
{metrics_text}

Overall Performance:
- Average open rate: {analysis['summary']['avg_open_rate']}%
- Average click rate: {analysis['summary']['avg_click_rate']}%
- Best performer: {analysis['best_performer']['persona']} ({analysis['best_performer']['click_rate']}% CTR)

Provide:
1. Key insights about what worked well
2. Recommendations for improving underperforming segments
3. Specific content suggestions for the next campaign
4. A/B test ideas

Keep response under 200 words and make it actionable."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            insights = message.content[0].text
            print("✅ AI insights generated")
            return insights
            
        except Exception as e:
            print(f"⚠️  Could not generate AI insights: {str(e)}")
            return self.generate_basic_insights(analysis)
    
    def generate_basic_insights(self, analysis: Dict) -> str:
        best = analysis['best_performer']
        worst = analysis['worst_performer']
        
        return f"""Performance Summary:

The {best['persona']} segment performed best with a {best['click_rate']}% click rate. 
The {worst['persona']} segment had the lowest engagement at {worst['click_rate']}%.

Recommendations:
1. Replicate successful elements from the {best['persona']} newsletter
2. Test different messaging approaches for {worst['persona']}
3. Consider A/B testing subject lines to improve open rates
4. Focus on pain points more relevant to underperforming segments"""
    
    def suggest_next_topics(self, campaign_history: List[Dict]) -> List[str]:
        print("\n💡 Generating topic suggestions...")
        
        if not self.client:
            return [
                "AI automation tools comparison",
                "Workflow optimization case studies",
                "Creative productivity hacks"
            ]
        
        recent_topics = [c.get('topic', '') for c in campaign_history[-3:]]
        topics_text = "\n".join([f"- {t}" for t in recent_topics if t])
        
        prompt = f"""Based on these recent blog topics for an AI automation startup:

{topics_text}

Suggest 5 new blog topics that:
1. Are different from recent topics
2. Appeal to creative agency decision-makers
3. Focus on automation, AI, and workflow optimization
4. Are timely and trend-relevant

Return just the 5 topics, one per line."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = message.content[0].text
            topics = [line.strip('- ').strip() for line in response.split('\n') 
                     if line.strip() and not line.strip().isdigit()]
            
            print(f"✅ Generated {len(topics)} topic suggestions")
            return topics[:5]
            
        except Exception as e:
            print(f"⚠️  Could not generate topics: {str(e)}")
            return [
                "AI automation tools comparison",
                "Workflow optimization case studies",
                "Creative productivity hacks"
            ]
    
    def save_analysis_report(self, campaign_id: int, analysis: Dict, 
                            output_path: str = None):
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"outputs/campaign_{campaign_id}_analysis_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"Analysis saved to {output_path}")
