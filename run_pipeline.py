import os
import json
from dotenv import load_dotenv
from src.database import Database
from src.content_gen import ContentGenerator
from src.crm_manager import HubSpotManager
from src.analytics_engine import AnalyticsEngine
from src.optimizer import ContentOptimizer

# Load environment variables
load_dotenv()

def print_banner():
    print("\n" + "="*60)
    print("🚀 NOVAMIND CONTENT PIPELINE")
    print("="*60 + "\n")

def load_mock_contacts():
    with open('data/mock_contacts.json', 'r') as f:
        data = json.load(f)
    return data['contacts']

def run_full_pipeline(topic: str, additional_context: str = ""):
    print_banner()
    
    # Initialize components
    print("🔧 Initializing pipeline components...")
    db = Database()
    generator = ContentGenerator()
    crm = HubSpotManager()
    analytics = AnalyticsEngine(db)
    optimizer = ContentOptimizer()
    print("✅ All components initialized\n")
    
    # STEP 1: Generate blog content
    print("=" * 60)
    print("STEP 1: GENERATING BLOG CONTENT")
    print("=" * 60)
    
    blog_content = generator.generate_blog_post(topic, additional_context)
    blog_id = db.save_blog_post(
        topic=topic,
        title=blog_content['title'],
        outline=blog_content['outline'],
        content=blog_content['content'],
        metadata={'status': 'published'}
    )
    
    print(f"\n📝 Blog Post Created (ID: {blog_id})")
    print(f"   Title: {blog_content['title']}")
    print(f"   Word Count: {len(blog_content['content'].split())}")
    
    # STEP 2: Generate personalized newsletters
    print("\n" + "=" * 60)
    print("STEP 2: GENERATING PERSONALIZED NEWSLETTERS")
    print("=" * 60)
    
    newsletters = generator.generate_newsletter_variations(blog_content)
    
    newsletter_ids = {}
    for persona_key, newsletter in newsletters.items():
        newsletter_id = db.save_newsletter(
            blog_id=blog_id,
            persona=newsletter['persona'],
            subject_line=newsletter['subject_line'],
            preview_text=newsletter['preview_text'],
            content=newsletter['content']
        )
        newsletter_ids[persona_key] = newsletter_id
        
        print(f"\n📧 Newsletter for {newsletter['persona']}")
        print(f"   Subject: {newsletter['subject_line']}")
        print(f"   Preview: {newsletter['preview_text'][:50]}...")
    
    # STEP 3: Create alternative versions (BONUS FEATURE)
    print("\n" + "=" * 60)
    print("STEP 3: GENERATING ALTERNATIVE VERSIONS (A/B TEST)")
    print("=" * 60)
    
    alternatives = {}
    for persona_key, newsletter in newsletters.items():
        alts = generator.generate_alternative_versions(
            newsletter['subject_line'],
            content_type="subject_line",
            count=2
        )
        alternatives[persona_key] = alts
        
        print(f"\n🔄 Alternatives for {newsletter['persona']}:")
        for i, alt in enumerate(alts, 1):
            print(f"   {i}. {alt}")
    
    # STEP 4: Create contacts in CRM
    print("\n" + "=" * 60)
    print("STEP 4: SYNCING CONTACTS TO HUBSPOT")
    print("=" * 60)
    
    contacts = load_mock_contacts()
    contact_map = crm.bulk_create_contacts(contacts)
    
    # Group contacts by persona
    contacts_by_persona = {}
    for contact in contacts:
        persona = contact['persona']
        if persona not in contacts_by_persona:
            contacts_by_persona[persona] = []
        contacts_by_persona[persona].append(contact_map.get(contact['email']))
    
    # STEP 5: Send newsletters
    print("\n" + "=" * 60)
    print("STEP 5: DISTRIBUTING NEWSLETTERS")
    print("=" * 60)
    
    campaign_name = f"{blog_content['title']} - {topic}"
    campaign_id = db.create_campaign(blog_id, campaign_name, hubspot_campaign_id="sim_campaign")
    
    for persona_key, newsletter in newsletters.items():
        contact_ids = contacts_by_persona.get(persona_key, [])
        if contact_ids:
            crm.send_email_to_segment(
                persona=newsletter['persona'],
                contact_ids=contact_ids,
                email_content=newsletter
            )
    
    print(f"\n✅ Campaign launched: {campaign_name}")
    
    # STEP 6: Collect performance data
    print("\n" + "=" * 60)
    print("STEP 6: COLLECTING PERFORMANCE METRICS")
    print("=" * 60)
    
    metrics_by_persona = {}
    for persona_key in newsletters.keys():
        metrics = crm.generate_simulated_stats(persona_key)
        db.save_performance_metrics(campaign_id, persona_key, metrics)
        metrics_by_persona[persona_key] = metrics
        
        print(f"\n📊 {persona_key.upper()} Metrics:")
        print(f"   Sent: {metrics['sent']}")
        print(f"   Opens: {metrics['opens']} ({metrics['open_rate']}%)")
        print(f"   Clicks: {metrics['clicks']} ({metrics['click_rate']}%)")
    
    # STEP 7: Analyze performance
    print("\n" + "=" * 60)
    print("STEP 7: ANALYZING PERFORMANCE & GENERATING INSIGHTS")
    print("=" * 60)
    
    analysis = analytics.analyze_campaign_performance(campaign_id, metrics_by_persona)
    
    print(f"\n📈 Campaign Summary:")
    print(f"   Total Sent: {analysis['summary']['total_sent']}")
    print(f"   Average Open Rate: {analysis['summary']['avg_open_rate']}%")
    print(f"   Average Click Rate: {analysis['summary']['avg_click_rate']}%")
    
    print(f"\n🏆 Best Performer: {analysis['best_performer']['persona']}")
    print(f"   Click Rate: {analysis['best_performer']['click_rate']}%")
    
    print(f"\n📉 Needs Improvement: {analysis['worst_performer']['persona']}")
    print(f"   Click Rate: {analysis['worst_performer']['click_rate']}%")
    
    print(f"\n🤖 AI Insights:\n{analysis['ai_insights']}")
    
    # Save analysis
    analytics.save_analysis_report(campaign_id, analysis)
    
    # STEP 8: Generate optimization suggestions (BONUS)
    print("\n" + "=" * 60)
    print("STEP 8: GENERATING OPTIMIZATION SUGGESTIONS")
    print("=" * 60)
    
    worst_performer = analysis['worst_performer']['persona']
    worst_metrics = metrics_by_persona[worst_performer]
    worst_newsletter = newsletters[worst_performer]
    
    improvements = optimizer.suggest_improvements(
        worst_newsletter['content'],
        worst_metrics
    )
    
    print(f"\n💡 Suggestions for {worst_performer}:")
    for suggestion in improvements['suggestions']:
        print(f"   • {suggestion}")
    
    # Save suggestions to database
    for suggestion in improvements['suggestions']:
        db.save_optimization_suggestion(
            campaign_id=campaign_id,
            suggestion_type="content_improvement",
            suggestion_text=suggestion,
            confidence_score=improvements['confidence']
        )
    
    # STEP 9: Suggest next topics (BONUS)
    print("\n" + "=" * 60)
    print("STEP 9: SUGGESTING NEXT BLOG TOPICS")
    print("=" * 60)
    
    campaigns = db.get_all_campaigns()
    next_topics = analytics.suggest_next_topics(campaigns)
    
    print("\n📝 Recommended topics for next campaign:")
    for i, topic in enumerate(next_topics, 1):
        print(f"   {i}. {topic}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Results saved:")
    print(f"   • Blog ID: {blog_id}")
    print(f"   • Campaign ID: {campaign_id}")
    print(f"   • Database: data/novamind.db")
    print(f"   • Analysis: outputs/campaign_{campaign_id}_analysis_*.json")
    print("\n")
    
    return {
        'blog_id': blog_id,
        'campaign_id': campaign_id,
        'analysis': analysis
    }

def main():
    # Example usage
    topic = "Boost Productivity with AI in 2025"
    context = "Discover how AI tools can streamline your daily tasks, automate routine work, and help your team achieve more in less time"
    
    run_full_pipeline(topic, context)

if __name__ == "__main__":
    main()
