import os
import json
from typing import Dict, List
from anthropic import Anthropic
import httpx
class ContentGenerator:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        client=httpx.Client()
        self.client = Anthropic(api_key=api_key,http_client=client)
        self.personas = self.load_personas()
    
    def load_personas(self) -> Dict:
        personas_path = 'data/personas.json'
        if os.path.exists(personas_path):
            with open(personas_path, 'r') as f:
                return json.load(f)
        
        return {
            "founders": {
                "name": "Founders / Decision-Makers",
                "focus": ["ROI", "growth", "efficiency"],
                "tone": "strategic and data-driven",
                "pain_points": ["time management", "scaling challenges"]
            },
            "creatives": {
                "name": "Creative Professionals",
                "focus": ["inspiration", "time-saving tools"],
                "tone": "inspiring and visual",
                "pain_points": ["creative blocks", "repetitive tasks"]
            },
            "operations": {
                "name": "Operations Managers",
                "focus": ["workflows", "integrations", "reliability"],
                "tone": "practical and detail-oriented",
                "pain_points": ["system integration", "team coordination"]
            }
        }
    
    def generate_blog_post(self, topic: str, additional_context: str = "") -> Dict:
        print(f"\n🤖 Generating blog post about: {topic}")
        
        prompt = f"""You are a content writer for NovaMind, an AI startup helping creative agencies automate workflows.

Topic: {topic}
{f'Additional Context: {additional_context}' if additional_context else ''}

Write a blog post that:
1. Addresses automation trends in creative work
2. Shows practical value and real-world applications
3. Is approximately 500 words
4. Has an engaging, conversational tone
5. Includes actionable takeaways

First provide a brief outline (3-4 main sections), then write the full blog post.

Format your response as:
TITLE: [compelling title]

OUTLINE:
[outline here]

CONTENT:
[full blog post here]"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            parts = response_text.split('\n\n')
            title = ""
            outline = ""
            content = ""
            
            current_section = None
            for part in parts:
                if part.startswith('TITLE:'):
                    title = part.replace('TITLE:', '').strip()
                    current_section = 'title'
                elif part.startswith('OUTLINE:'):
                    current_section = 'outline'
                elif part.startswith('CONTENT:'):
                    current_section = 'content'
                else:
                    if current_section == 'outline':
                        outline += part + '\n\n'
                    elif current_section == 'content':
                        content += part + '\n\n'
            
            print(f"✅ Blog post generated: {title}")
            
            return {
                'title': title,
                'outline': outline.strip(),
                'content': content.strip()
            }
        except Exception as e:
            print(f"❌ Error generating blog post: {str(e)}")
            raise
    
    def generate_newsletter_variations(self, blog_content: Dict) -> Dict[str, Dict]:
        print(f"\n📧 Generating personalized newsletters...")
        
        newsletters = {}
        
        for persona_key, persona_info in self.personas.items():
            prompt = f"""Based on this blog post, create a personalized newsletter version for {persona_info['name']}.

Blog Title: {blog_content['title']}
Blog Content: {blog_content['content']}

Persona Details:
- Focus areas: {', '.join(persona_info['focus'])}
- Tone: {persona_info['tone']}
- Pain points: {', '.join(persona_info['pain_points'])}

Create a newsletter that:
1. Has a compelling subject line (under 60 characters)
2. Includes a preview text (under 100 characters)
3. Summarizes the blog in 150-200 words
4. Emphasizes points relevant to this persona
5. Has a clear call-to-action to read the full blog
6. Uses the appropriate tone for this audience

Format:
SUBJECT: [subject line]
PREVIEW: [preview text]
BODY: [newsletter content]"""

            try:
                message = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=800,
                    temperature=0.8,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response = message.content[0].text
                
                subject = ""
                preview = ""
                body = ""
                
                lines = response.split('\n')
                current_section = None
                
                for line in lines:
                    if line.startswith('SUBJECT:'):
                        subject = line.replace('SUBJECT:', '').strip()
                    elif line.startswith('PREVIEW:'):
                        preview = line.replace('PREVIEW:', '').strip()
                    elif line.startswith('BODY:'):
                        current_section = 'body'
                    elif current_section == 'body' and line.strip():
                        body += line + '\n'
                
                newsletters[persona_key] = {
                    'persona': persona_info['name'],
                    'subject_line': subject,
                    'preview_text': preview,
                    'content': body.strip()
                }
                
                print(f"✅ Newsletter created for {persona_info['name']}")
                
            except Exception as e:
                print(f"❌ Error generating newsletter for {persona_key}: {str(e)}")
                raise
        
        return newsletters
    
    def generate_alternative_versions(self, original_content: str, 
                                     content_type: str = "subject_line", count: int = 3) -> List[str]:
        print(f"\n🔄 Generating {count} alternatives for {content_type}...")
        
        prompt = f"""Generate {count} alternative versions of this {content_type}:

Original: {original_content}

Make each version:
1. Significantly different in approach
2. Equally compelling
3. Appropriate for professional marketing

Return just the {count} alternatives, numbered 1-{count}."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=0.9,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = message.content[0].text
            alternatives = []
            
            for line in response.split('\n'):
                line = line.strip()
                if line and line[0].isdigit():
                    if '. ' in line:
                        alternatives.append(line.split('. ', 1)[1])
                    else:
                        alternatives.append(line)
            
            print(f"✅ Generated {len(alternatives)} alternatives")
            return alternatives[:count]
            
        except Exception as e:
            print(f"❌ Error generating alternatives: {str(e)}")
            return []