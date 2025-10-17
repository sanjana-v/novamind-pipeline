# NovaMind Content Pipeline

AI-powered marketing automation system that generates, distributes, and optimizes blog and newsletter content.

## Overview

This system automates the entire content marketing workflow:
1. **AI Content Generation** - Creates blog posts and personalized newsletters
2. **CRM Integration** - Syncs contacts and sends campaigns via HubSpot
3. **Performance Analytics** - Tracks engagement and generates insights
4. **Content Optimization** - AI-powered suggestions for improvement

## Architecture

### User Input → AI Generation → Database Storage → CRM Distribution → Analytics

### Components:
- **Content Generator**: Uses Claude AI to create blog posts and newsletters
- **Database**: SQLite for storing content and metrics
- **CRM Manager**: HubSpot API integration for contact management
- **Analytics Engine**: Performance tracking and AI-powered insights
- **Web Dashboard**: Flask-based UI for managing campaigns

## Tech Stack

- **Backend**: Python 3.9+
- **AI**: Anthropic Claude API
- **CRM**: HubSpot API
- **Database**: SQLite
- **Web Framework**: Flask
- **Data Analysis**: Pandas

## Installation

### Prerequisites
- Python 3.9 or higher
- API keys for Anthropic Claude and HubSpot

### Setup Steps

1. **Clone the repository**
bash
git clone <your-repo-url>
cd novamind-pipeline

Create virtual environment

bashpython -m venv venv


# Mac/Linux
source venv/bin/activate

Install dependencies

bashpip install -r requirements.txt


4. **Configure environment variables**

Create `.env` file in root directory:
```
ANTHROPIC_API_KEY=your_claude_api_key
HUBSPOT_API_KEY=your_hubspot_api_key

Initialize database

bashpython -c "from src.database import Database; Database()"
Usage
Option 1: Command Line Pipeline
Run the full pipeline:
bashpython run_pipeline.py
This will:

Generate a blog post
Create 3 personalized newsletters
Sync contacts to HubSpot
Simulate campaign distribution
Generate performance analytics
Provide optimization suggestions

##  Web Dashboard
Start the web server:
bashpython web/app.py


Then open: http://localhost:5000

The dashboard allows you to:
- Generate content through a UI
- Launch campaigns with one click
- View analytics and performance metrics
## Overview
## Features
````
### Core Requirements

**1. AI Content Generation**
- Blog post generation (400-600 words)
- Three personalized newsletter variations
- Content stored in structured format

**2. CRM Integration**
- HubSpot contact creation/updates
- Persona-based segmentation
- Campaign logging

**3. Performance Analytics**
- Engagement metrics (opens, clicks, etc.)
- Historical data storage
- AI-generated performance summaries

###  Additional Features

**4. Content Optimization**
- Alternative version generation (A/B testing)
- Performance-based suggestions
- Next topic recommendations

**5. Web Dashboard**
- Visual campaign management
- Real-time content generation
- Analytics visualization

## Project Structure
```
novamind-pipeline/
├── src/                          # Core modules
│   ├── database.py              # Database operations
│   ├── content_generator.py    # AI content creation
│   ├── crm_manager.py           # HubSpot integration
│   ├── analytics_engine.py     # Performance analysis
│   └── optimizer.py             # Content optimization
├── web/                         # Web dashboard
│   ├── app.py                   # Flask application
│   └── templates/               # HTML templates
├── data/                        # Data files
│   ├── personas.json            # Audience personas
│   ├── mock_contacts.json       # Test contacts
│   └── novamind.db              # SQLite database
├── outputs/                     # Generated reports
├── docs/                        # Documentation
├── run_pipeline.py              # Main pipeline script
├── requirements.txt             # Python dependencies
└── README.md                    # This file

```
## Output
<video src="output-1.mov" controls playsinline muted style="max-width:100%; border-radius:12px;">

  Here’s a <a href="output-1.mov">direct link</a>.
</video>

## Author

SANJANA VENKATESH ;)

