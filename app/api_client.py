import requests
from flask import session, redirect, url_for, flash
from functools import wraps
from config import Config

class AuthenticationError(Exception):
    pass

class APIError(Exception):
    pass

class MailServerAPI:
    def __init__(self):
        self.base_url = Config.MAIL_SERVER_API_URL
    
    def _make_request(self, method, endpoint, token=None, **kwargs):
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired token")
            
            response.raise_for_status()
            
            if response.status_code == 204:
                return None
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    # Authentication
    def login(self, email, password):
        """Authenticate user and return JWT token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={'email': email, 'password': password}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['token'], data['user']
        elif response.status_code == 401:
            raise AuthenticationError("Invalid credentials")
        else:
            raise APIError(f"Login failed: {response.status_code}")
    
    # Emails
    def get_emails(self, token, folder_id=None, page=1, limit=20):
        """Get list of emails"""
        params = {'page': page, 'limit': limit}
        if folder_id:
            params['folder_id'] = folder_id
        return self._make_request('GET', '/api/emails', token, params=params)
    
    def get_email(self, token, email_id):
        """Get single email by ID"""
        return self._make_request('GET', f'/api/emails/{email_id}', token)
    
    def send_email(self, token, to, subject, body, cc=None, bcc=None):
        """Send a new email"""
        data = {'to': to, 'subject': subject, 'body': body}
        if cc:
            data['cc'] = cc
        if bcc:
            data['bcc'] = bcc
        return self._make_request('POST', '/api/emails', token, json=data)
    
    def mark_read(self, token, email_id):
        """Mark email as read"""
        return self._make_request('POST', f'/api/emails/{email_id}/read', token)
    
    def toggle_star(self, token, email_id):
        """Toggle star status"""
        return self._make_request('POST', f'/api/emails/{email_id}/star', token)
    
    def delete_email(self, token, email_id):
        """Delete email"""
        return self._make_request('DELETE', f'/api/emails/{email_id}', token)
    
    def move_email(self, token, email_id, folder_id):
        """Move email to folder"""
        return self._make_request('POST', f'/api/emails/{email_id}/move', token, json={'folder_id': folder_id})
    
    # Folders
    def get_folders(self, token):
        """Get all folders"""
        return self._make_request('GET', '/api/folders', token)
    
    def create_folder(self, token, name):
        """Create new folder"""
        return self._make_request('POST', '/api/folders', token, json={'name': name})
    
    def delete_folder(self, token, folder_id):
        """Delete folder"""
        return self._make_request('DELETE', f'/api/folders/{folder_id}', token)
    
    # Search
    def search_emails(self, token, query, folder_id=None, flag=None, page=1, limit=20):
        """Search emails"""
        params = {'q': query, 'page': page, 'limit': limit}
        if folder_id:
            params['folder_id'] = folder_id
        if flag:
            params['flag'] = flag
        return self._make_request('GET', '/api/search', token, params=params)
    
    # Blacklist
    def get_blacklist(self, token, source=None, page=1, limit=20):
        """Get blacklisted IPs"""
        params = {'page': page, 'limit': limit}
        if source:
            params['source'] = source
        return self._make_request('GET', '/api/blacklist/ip', token, params=params)
    
    def remove_from_blacklist(self, token, ip_id):
        """Remove IP from blacklist"""
        return self._make_request('DELETE', f'/api/blacklist/ip/{ip_id}', token)
    
    def get_blacklist_stats(self, token):
        """Get blacklist statistics"""
        return self._make_request('GET', '/api/blacklist/stats', token)
    
    def check_ip_blacklist(self, token, ip_address):
        """Check if IP is blacklisted"""
        return self._make_request('GET', f'/api/blacklist/ip/check/{ip_address}', token)
    
    # Delivery Status
    def get_delivery_status(self, token, email_id):
        """Get email delivery status"""
        return self._make_request('GET', f'/api/emails/{email_id}/delivery-status', token)

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_api_client():
    """Get API client instance"""
    return MailServerAPI()
