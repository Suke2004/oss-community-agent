# apps/ui/utils/helpers.py

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import hashlib

def load_css(file_path: str):
    """Load and inject CSS file into Streamlit"""
    try:
        with open(file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {file_path}")

def init_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = True  # Simplified auth for demo
    
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    if 'selected_filters' not in st.session_state:
        st.session_state.selected_filters = {}
    
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    except:
        return "Unknown"

def create_status_badge(status: str) -> str:
    """Create HTML status badge"""
    badge_classes = {
        'pending': 'status-badge pending',
        'approved': 'status-badge approved',
        'rejected': 'status-badge rejected',
        'processing': 'status-badge processing'
    }
    
    badge_class = badge_classes.get(status.lower(), 'status-badge')
    return f'<span class="{badge_class}">{status}</span>'

def create_metric_card(title: str, value: str, change: str = None, change_type: str = "neutral") -> str:
    """Create HTML metric card"""
    change_html = ""
    if change:
        change_class = f"metric-change {change_type}"
        change_html = f'<p class="{change_class}">{change}</p>'
    
    return f'''
    <div class="metric-card">
        <h3 class="metric-value">{value}</h3>
        <p class="metric-label">{title}</p>
        {change_html}
    </div>
    '''

def create_request_card(request: Dict[str, Any]) -> str:
    """Create HTML request card for display"""
    status_badge = create_status_badge(request.get('status', 'pending'))
    timestamp = format_timestamp(request.get('created_at', ''))
    
    # Truncate content for display
    content = request.get('post_content', '')
    if len(content) > 200:
        content = content[:200] + '...'
    
    reply = request.get('drafted_reply', '')
    if len(reply) > 300:
        reply = reply[:300] + '...'
    
    return f'''
    <div class="request-card">
        <div class="request-header">
            <div>
                <h4 class="request-title">{request.get('post_title', 'Untitled Post')}</h4>
                <div class="request-meta">
                    <span>r/{request.get('subreddit', 'unknown')}</span>
                    <span>{timestamp}</span>
                    {status_badge}
                </div>
            </div>
        </div>
        <div class="request-content">
            <strong>Original Question:</strong><br>
            {content}
        </div>
        {f'<div class="request-reply"><strong>Drafted Reply:</strong><br>{reply}</div>' if reply else ''}
    </div>
    '''

def calculate_metrics_change(current: float, previous: float) -> tuple:
    """Calculate percentage change and determine if positive/negative"""
    if previous == 0:
        return (100.0, "positive") if current > 0 else (0.0, "neutral")
    
    change = ((current - previous) / previous) * 100
    change_type = "positive" if change > 0 else "negative" if change < 0 else "neutral"
    return (abs(change), change_type)

def export_data_to_json(data: List[Dict], filename: str) -> str:
    """Export data to JSON file and return file path"""
    filepath = f"data/exports/{filename}"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return filepath

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    import html
    return html.escape(text) if text else ""

def generate_request_id() -> str:
    """Generate unique request ID"""
    timestamp = datetime.now().isoformat()
    return hashlib.md5(timestamp.encode()).hexdigest()[:12]

def validate_reddit_credentials(credentials: Dict[str, str]) -> Dict[str, Any]:
    """Validate Reddit API credentials"""
    required_fields = ['client_id', 'client_secret', 'username', 'password']
    missing_fields = [field for field in required_fields if not credentials.get(field)]
    
    if missing_fields:
        return {
            'valid': False,
            'errors': f"Missing required fields: {', '.join(missing_fields)}"
        }
    
    # Basic validation (in production, you'd test actual connection)
    if len(credentials.get('client_id', '')) < 10:
        return {
            'valid': False,
            'errors': "Client ID appears to be invalid"
        }
    
    return {'valid': True, 'errors': None}

def format_confidence_score(score: float) -> str:
    """Format confidence score for display"""
    if score is None:
        return "N/A"
    
    percentage = score * 100
    if percentage >= 80:
        return f"🟢 {percentage:.1f}%"
    elif percentage >= 60:
        return f"🟡 {percentage:.1f}%"
    else:
        return f"🔴 {percentage:.1f}%"

def create_navigation_item(icon: str, label: str, page_key: str, is_active: bool = False) -> str:
    """Create navigation item HTML"""
    active_class = "nav-item active" if is_active else "nav-item"
    return f'''
    <div class="{active_class}" onclick="window.location.href='?page={page_key}'">
        <span>{icon}</span>
        <span>{label}</span>
    </div>
    '''

def get_chart_colors() -> Dict[str, str]:
    """Get consistent chart colors for visualizations"""
    return {
        'primary': '#6366f1',
        'secondary': '#ec4899',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'info': '#3b82f6'
    }

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def parse_citations(citations_json: str) -> List[Dict[str, str]]:
    """Parse citations JSON string"""
    try:
        if not citations_json:
            return []
        citations = json.loads(citations_json)
        return citations if isinstance(citations, list) else []
    except:
        return []

def format_processing_time(seconds: float) -> str:
    """Format processing time for display"""
    if seconds is None:
        return "N/A"
    
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:.0f}m {remaining_seconds:.0f}s"

def create_alert(message: str, alert_type: str = "info") -> str:
    """Create alert HTML"""
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    icon = icons.get(alert_type, 'ℹ️')
    return f'''
    <div class="alert alert-{alert_type}">
        <span class="alert-icon">{icon}</span>
        <span class="alert-message">{message}</span>
    </div>
    '''
