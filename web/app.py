import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from src.database import Database
from src.content_gen import ContentGenerator
from src.crm_manager import HubSpotManager
from src.analytics_engine import AnalyticsEngine
from src.optimizer import ContentOptimizer
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = 'novamind-secret-key-change-in-production'

# Initialize components
db = Database()
generator = ContentGenerator()
crm = HubSpotManager()
analytics = AnalyticsEngine(db)
optimizer = ContentOptimizer()

@app.route('/')
def index():
    campaigns = db.get_all_campaigns()
    return render_template('index.html', campaigns=campaigns)

@app.route('/generate')
def generate_page():
    return render_template('generate.html')

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    data = request.json
    topic = data.get('topic')
    context = data.get('context', '')
    
    try:
        # Generate blog
        blog_content = generator.generate_blog_post(topic, context)
        blog_id = db.save_blog_post(
            topic=topic,
            title=blog_content['title'],
            outline=blog_content['outline'],
            content=blog_content['content']
        )
        
        # Generate newsletters
        newsletters = generator.generate_newsletter_variations(blog_content)
        
        for persona_key, newsletter in newsletters.items():
            db.save_newsletter(
                blog_id=blog_id,
                persona=newsletter['persona'],
                subject_line=newsletter['subject_line'],
                preview_text=newsletter['preview_text'],
                content=newsletter['content']
            )
        
        return jsonify({
            'success': True,
            'blog_id': blog_id,
            'blog': blog_content,
            'newsletters': newsletters
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/launch-campaign', methods=['POST'])
def launch_campaign():
    data = request.json
    blog_id = data.get('blog_id')
    
    try:
        # Load contacts
        with open('data/mock_contacts.json', 'r') as f:
            contacts = json.load(f)['contacts']
        
        # Create contacts in HubSpot
        contact_map = crm.bulk_create_contacts(contacts)
        
        # Group by persona
        contacts_by_persona = {}
        for contact in contacts:
            persona = contact['persona']
            if persona not in contacts_by_persona:
                contacts_by_persona[persona] = []
            if contact['email'] in contact_map:
                contacts_by_persona[persona].append(contact_map[contact['email']])
        
        # Get blog and newsletters
        blog = db.get_blog_post(blog_id)
        newsletters = db.get_newsletters_for_blog(blog_id)
        
        # Create campaign
        campaign_name = f"{blog['title']}"
        campaign_id = db.create_campaign(blog_id, campaign_name)
        
        # Send newsletters
        for newsletter in newsletters:
            persona_key = newsletter['persona'].lower().split()[0]
            contact_ids = contacts_by_persona.get(persona_key, [])
            
            if contact_ids:
                crm.send_email_to_segment(
                    persona=newsletter['persona'],
                    contact_ids=contact_ids,
                    email_content=newsletter
                )
        
        # Generate metrics
        metrics_by_persona = {}
        for newsletter in newsletters:
            persona_key = newsletter['persona'].lower().split()[0]
            metrics = crm.generate_simulated_stats(persona_key)
            db.save_performance_metrics(campaign_id, persona_key, metrics)
            metrics_by_persona[persona_key] = metrics
        
        # Analyze
        analysis = analytics.analyze_campaign_performance(campaign_id, metrics_by_persona)
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analytics')
def analytics_page():
    campaigns = db.get_all_campaigns()
    return render_template('analytics.html', campaigns=campaigns)

@app.route('/api/campaign/<int:campaign_id>')
def get_campaign_details(campaign_id):
    metrics = db.get_campaign_performance(campaign_id)
    return jsonify({'metrics': metrics})

if __name__ == '__main__':
    app.run(debug=True, port=5000)