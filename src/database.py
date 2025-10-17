import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "data/novamind.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        print("connection estabilished")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                title TEXT NOT NULL,
                outline TEXT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                word_count INTEGER,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS newsletters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blog_id INTEGER,
                persona TEXT NOT NULL,
                subject_line TEXT NOT NULL,
                preview_text TEXT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (blog_id) REFERENCES blog_posts (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blog_id INTEGER,
                campaign_name TEXT NOT NULL,
                send_date TIMESTAMP,
                hubspot_campaign_id TEXT,
                status TEXT DEFAULT 'draft',
                FOREIGN KEY (blog_id) REFERENCES blog_posts (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                persona TEXT NOT NULL,
                sent_count INTEGER DEFAULT 0,
                delivered_count INTEGER DEFAULT 0,
                open_count INTEGER DEFAULT 0,
                click_count INTEGER DEFAULT 0,
                unsubscribe_count INTEGER DEFAULT 0,
                open_rate REAL,
                click_rate REAL,
                unsubscribe_rate REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                suggestion_type TEXT,
                suggestion_text TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            )
        ''')
        print("executed")
        conn.commit()

        conn.close()
    
    def save_blog_post(self, topic: str, title: str, outline: str, 
                       content: str, metadata: Dict = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        word_count = len(content.split())
        metadata_json = json.dumps(metadata) if metadata else "{}"
        
        cursor.execute('''
            INSERT INTO blog_posts (topic, title, outline, content, word_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (topic, title, outline, content, word_count, metadata_json))
        
        blog_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return blog_id
    
    def save_newsletter(self, blog_id: int, persona: str, 
                       subject_line: str, preview_text: str, content: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO newsletters (blog_id, persona, subject_line, preview_text, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (blog_id, persona, subject_line, preview_text, content))
        
        newsletter_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return newsletter_id
    
    def create_campaign(self, blog_id: int, campaign_name: str, 
                       hubspot_campaign_id: str = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaigns (blog_id, campaign_name, send_date, hubspot_campaign_id, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (blog_id, campaign_name, datetime.now(), hubspot_campaign_id, 'sent'))
        
        campaign_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return campaign_id
    
    def save_performance_metrics(self, campaign_id: int, persona: str, metrics: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics 
            (campaign_id, persona, sent_count, delivered_count, open_count, 
             click_count, unsubscribe_count, open_rate, click_rate, unsubscribe_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id, persona, metrics.get('sent', 0), metrics.get('delivered', 0),
            metrics.get('opens', 0), metrics.get('clicks', 0), metrics.get('unsubscribes', 0),
            metrics.get('open_rate', 0), metrics.get('click_rate', 0), 
            metrics.get('unsubscribe_rate', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def save_optimization_suggestion(self, campaign_id: int, suggestion_type: str,
                                    suggestion_text: str, confidence_score: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO optimization_suggestions 
            (campaign_id, suggestion_type, suggestion_text, confidence_score)
            VALUES (?, ?, ?, ?)
        ''', (campaign_id, suggestion_type, suggestion_text, confidence_score))
        
        conn.commit()
        conn.close()
    
    def get_all_campaigns(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.campaign_name, c.send_date, c.status, b.title, b.topic
            FROM campaigns c
            JOIN blog_posts b ON c.blog_id = b.id
            ORDER BY c.send_date DESC
        ''')
        
        campaigns = []
        for row in cursor.fetchall():
            campaigns.append({
                'id': row[0],
                'name': row[1],
                'send_date': row[2],
                'status': row[3],
                'blog_title': row[4],
                'topic': row[5]
            })
        
        conn.close()
        return campaigns
    
    def get_campaign_performance(self, campaign_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT persona, sent_count, open_count, click_count, 
                   open_rate, click_rate, unsubscribe_rate
            FROM performance_metrics
            WHERE campaign_id = ?
        ''', (campaign_id,))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'persona': row[0],
                'sent': row[1],
                'opens': row[2],
                'clicks': row[3],
                'open_rate': row[4],
                'click_rate': row[5],
                'unsubscribe_rate': row[6]
            })
        
        conn.close()
        return metrics
    
    def get_blog_post(self, blog_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, topic, title, outline, content, created_at, word_count
            FROM blog_posts
            WHERE id = ?
        ''', (blog_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'topic': row[1],
                'title': row[2],
                'outline': row[3],
                'content': row[4],
                'created_at': row[5],
                'word_count': row[6]
            }
        return None
    
    def get_newsletters_for_blog(self, blog_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, persona, subject_line, preview_text, content
            FROM newsletters
            WHERE blog_id = ?
        ''', (blog_id,))
        
        newsletters = []
        for row in cursor.fetchall():
            newsletters.append({
                'id': row[0],
                'persona': row[1],
                'subject_line': row[2],
                'preview_text': row[3],
                'content': row[4]
            })
        
        conn.close()
        return newsletters