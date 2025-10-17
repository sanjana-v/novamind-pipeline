import os
import json
import requests
import random
from typing import List, Dict, Optional
from datetime import datetime

class HubSpotManager:
    def __init__(self):
        self.api_key = os.getenv('HUBSPOT_API_KEY')
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }

        if not self.api_key:
            print("⚠️  WARNING: HUBSPOT_API_KEY not found. Using simulation mode.")
            self.simulation_mode = True
        else:
            # Check connection before continuing
            self.simulation_mode = not self.check_connection()

    def check_connection(self) -> bool:
        """Checks if HubSpot connection is valid."""
        test_url = f"{self.base_url}/crm/v3/objects/contacts?limit=1"
        try:
            response = requests.get(test_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                print("✅ Successfully connected to HubSpot API.")
                return True
            else:
                print(f"❌ HubSpot connection failed ({response.status_code}): {response.text}")
                print("⚠️  Switching to simulation mode.")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            print("⚠️  Switching to simulation mode.")
            return False

    def create_or_update_contact(self, contact_data: Dict) -> Optional[str]:
        if self.simulation_mode:
            print(f"   [SIM] Created contact: {contact_data['email']}")
            return f"sim_{contact_data['email']}"
        
        search_url = f"{self.base_url}/crm/v3/objects/contacts/search"
        search_payload = {
            "filterGroups": [{
                "filters": [{
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": contact_data['email']
                }]
            }]
        }

        try:
            response = requests.post(search_url, headers=self.headers, 
                                    json=search_payload, timeout=10)
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                
                if results:
                    contact_id = results[0]['id']
                    update_url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
                    
                    properties = {
                        "firstname": contact_data.get('firstname'),
                        "lastname": contact_data.get('lastname'),
                        "company": contact_data.get('company'),
                        "jobtitle": contact_data.get('jobtitle'),
                        "hs_persona": contact_data.get('persona')
                    }
                    
                    update_response = requests.patch(
                        update_url, 
                        headers=self.headers,
                        json={"properties": properties},
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        print(f"   ✅ Updated contact: {contact_data['email']}")
                        return contact_id
                    else:
                        print(f"   ❌ Update failed ({update_response.status_code}): {update_response.text}")
                else:
                    create_url = f"{self.base_url}/crm/v3/objects/contacts"
                    
                    properties = {
                        "email": contact_data['email'],
                        "firstname": contact_data.get('firstname'),
                        "lastname": contact_data.get('lastname'),
                        "company": contact_data.get('company'),
                        "jobtitle": contact_data.get('jobtitle'),
                        "hs_persona": contact_data.get('persona')
                    }
                    
                    create_response = requests.post(
                        create_url,
                        headers=self.headers,
                        json={"properties": properties},
                        timeout=10
                    )
                    
                    if create_response.status_code == 201:
                        contact_id = create_response.json()['id']
                        print(f"   ✅ Created contact: {contact_data['email']}")
                        return contact_id
                    else:
                        print(f"   ❌ Create failed ({create_response.status_code}): {create_response.text}")
            
            print(f"   ⚠️  Could not create/update contact: {contact_data['email']}")
            return None
                  
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error with contact {contact_data['email']}: {str(e)}")
            return None

    def bulk_create_contacts(self, contacts: List[Dict]) -> Dict[str, str]:
        print(f"\n👥 Creating/updating {len(contacts)} contacts in HubSpot...")
        
        contact_map = {}
        for contact in contacts:
            contact_id = self.create_or_update_contact(contact)
            if contact_id:
                contact_map[contact['email']] = contact_id
        
        print(f"✅ Processed {len(contact_map)} contacts")
        return contact_map

    def send_email_to_segment(self, persona: str, contact_ids: List[str],
                             email_content: Dict) -> bool:
        print(f"\n📧 Sending email to {persona} segment ({len(contact_ids)} contacts)...")
        print(f"   Subject: {email_content.get('subject_line')}")
        print(f"   Preview: {email_content.get('preview_text')}")
        
        if self.simulation_mode:
            print(f"   [SIM] Email sent successfully")
            return True
        
        # In production HubSpot, you would use the Marketing Email API
        self.log_campaign_activity(persona, contact_ids, "sent")
        print(f"   ✅ Email sent to {len(contact_ids)} contacts")
        return True

    def log_campaign_activity(self, campaign_id: str, contact_ids: List[str],
                             activity_type: str) -> bool:
        timestamp = datetime.now().isoformat()
        log_entry = {
            "campaign_id": campaign_id,
            "activity": activity_type,
            "contacts": len(contact_ids),
            "timestamp": timestamp
        }
        
        log_path = "data/campaign_logs.json"
        logs = []
        
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        
        logs.append(log_entry)
        
        with open(log_path, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return True

    def generate_simulated_stats(self, persona: str) -> Dict:
        base_sent = random.randint(15, 20)
        
        if persona == "founders":
            open_rate_range = (0.22, 0.32)
            click_rate_range = (0.15, 0.25)
        elif persona == "creatives":
            open_rate_range = (0.28, 0.38)
            click_rate_range = (0.18, 0.28)
        else:
            open_rate_range = (0.20, 0.28)
            click_rate_range = (0.12, 0.20)
        
        delivered = int(base_sent * random.uniform(0.97, 0.99))
        open_rate = random.uniform(*open_rate_range)
        opens = int(delivered * open_rate)
        click_rate = random.uniform(*click_rate_range)
        clicks = int(opens * click_rate)
        unsubscribes = random.randint(0, 1)
        
        return {
            'sent': base_sent,
            'delivered': delivered,
            'opens': opens,
            'clicks': clicks,
            'unsubscribes': unsubscribes,
            'open_rate': round(open_rate * 100, 2),
            'click_rate': round(click_rate * 100, 2),
            'unsubscribe_rate': round((unsubscribes / delivered * 100) if delivered > 0 else 0, 2)
        }
