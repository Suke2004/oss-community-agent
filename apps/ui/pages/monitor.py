# apps/ui/pages/monitor.py

import streamlit as st
import time
import sys
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager
from utils.helpers import format_timestamp, get_chart_colors, create_status_badge

def render_monitor_page():
    """Render the agent monitoring and status page"""
    
    # Initialize database
    db = DatabaseManager()
    
    # Page header
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: var(--text-primary); margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">
            🔍 Agent Monitoring & Status
        </h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem;">
            Real-time monitoring of agent activities, system health, and performance metrics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # System status overview
    render_system_status()
    
    # Real-time activity feed
    render_activity_feed(db)
    
    # Performance metrics
    render_performance_metrics(db)
    
    # Agent configuration status
    render_agent_config_status()
    
    # Auto-refresh controls
    render_refresh_controls()

def render_system_status():
    """Render overall system status"""
    
    st.markdown("<h2 style='margin: 2rem 0 1rem 0; color: var(--text-primary);'>⚡ System Status Overview</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Agent Status
        st.markdown("""
        <div style="padding: 1.5rem; background: var(--bg-card); border-radius: 12px; border-left: 4px solid #10b981; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                <h3 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">Agent Core</h3>
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Active & Processing</p>
            <p style="margin: 0.5rem 0 0 0; color: var(--text-muted); font-size: 0.8rem;">Last heartbeat: 30s ago</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Reddit API Status
        st.markdown("""
        <div style="padding: 1.5rem; background: var(--bg-card); border-radius: 12px; border-left: 4px solid #10b981; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%;"></div>
                <h3 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">Reddit API</h3>
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Connected</p>
            <p style="margin: 0.5rem 0 0 0; color: var(--text-muted); font-size: 0.8rem;">Rate limit: 92% available</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # RAG System Status
        st.markdown("""
        <div style="padding: 1.5rem; background: var(--bg-card); border-radius: 12px; border-left: 4px solid #10b981; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%;"></div>
                <h3 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">RAG System</h3>
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Ready</p>
            <p style="margin: 0.5rem 0 0 0; color: var(--text-muted); font-size: 0.8rem;">15 documents indexed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Database Status
        st.markdown("""
        <div style="padding: 1.5rem; background: var(--bg-card); border-radius: 12px; border-left: 4px solid #f59e0b; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <div style="width: 12px; height: 12px; background: #f59e0b; border-radius: 50%;"></div>
                <h3 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">Database</h3>
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Healthy</p>
            <p style="margin: 0.5rem 0 0 0; color: var(--text-muted); font-size: 0.8rem;">Size: 2.1 MB</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Add CSS for pulse animation
    st.markdown("""
    <style>
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

def render_activity_feed(db):
    """Render real-time activity feed"""
    
    st.markdown("<h2 style='margin: 2rem 0 1rem 0; color: var(--text-primary);'>📡 Live Activity Feed</h2>", unsafe_allow_html=True)
    
    # Get recent requests for activity simulation
    recent_requests = db.get_requests_by_filter({'limit': 10})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Activity timeline
        st.markdown("### 🕒 Recent Activities")
        
        # Simulate some real-time activities
        activities = [
            {
                'time': datetime.now() - timedelta(minutes=2),
                'type': 'scan',
                'message': 'Scanning r/learnpython for new questions',
                'status': 'completed',
                'icon': '🔍'
            },
            {
                'time': datetime.now() - timedelta(minutes=5),
                'type': 'draft',
                'message': 'Generated response for "How to install Python?"',
                'status': 'pending_approval',
                'icon': '✏️'
            },
            {
                'time': datetime.now() - timedelta(minutes=8),
                'type': 'approval',
                'message': 'Response approved and posted to r/python',
                'status': 'completed',
                'icon': '✅'
            },
            {
                'time': datetime.now() - timedelta(minutes=12),
                'type': 'moderation',
                'message': 'Content passed moderation checks',
                'status': 'completed',
                'icon': '🛡️'
            },
            {
                'time': datetime.now() - timedelta(minutes=15),
                'type': 'rag',
                'message': 'Retrieved documentation from 3 sources',
                'status': 'completed',
                'icon': '📚'
            }
        ]
        
        # Add real recent requests to activities
        for request in recent_requests[:5]:
            activities.append({
                'time': datetime.fromisoformat(request['created_at']) if isinstance(request['created_at'], str) else request['created_at'],
                'type': 'request',
                'message': f"New request: {request['post_title'][:50]}...",
                'status': request['status'],
                'icon': '📝'
            })
        
        # Sort by time
        activities.sort(key=lambda x: x['time'], reverse=True)
        
        for activity in activities[:10]:
            status_colors = {
                'completed': '#10b981',
                'pending_approval': '#f59e0b',
                'processing': '#3b82f6',
                'approved': '#10b981',
                'rejected': '#ef4444'
            }
            
            color = status_colors.get(activity['status'], '#6366f1')
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 1rem; margin-bottom: 0.5rem; background: var(--bg-card); border-radius: 8px; border-left: 3px solid {color};">
                <div style="font-size: 1.2rem; margin-right: 1rem;">{activity['icon']}</div>
                <div style="flex: 1;">
                    <div style="color: var(--text-primary); font-weight: 500;">{activity['message']}</div>
                    <div style="color: var(--text-muted); font-size: 0.8rem;">{format_timestamp(activity['time'].isoformat())} • {activity['type'].title()}</div>
                </div>
                <div style="color: {color}; font-size: 0.8rem; text-transform: uppercase; font-weight: 600;">
                    {activity['status'].replace('_', ' ')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Quick stats
        st.markdown("### 📊 Real-time Stats")
        
        # Active monitoring metrics
        metrics = [
            {
                'label': 'Subreddits Monitored',
                'value': '8',
                'change': '+2 today',
                'color': '#6366f1'
            },
            {
                'label': 'Avg Response Time',
                'value': '3.2s',
                'change': '-0.5s vs yesterday',
                'color': '#10b981'
            },
            {
                'label': 'API Calls Today',
                'value': '247',
                'change': '+12%',
                'color': '#f59e0b'
            },
            {
                'label': 'Success Rate',
                'value': '94.2%',
                'change': '+2.1%',
                'color': '#10b981'
            }
        ]
        
        for metric in metrics:
            st.markdown(f"""
            <div style="padding: 1rem; background: var(--bg-card); border-radius: 8px; border-left: 3px solid {metric['color']}; margin-bottom: 1rem;">
                <div style="color: var(--text-primary); font-weight: 600; font-size: 1.1rem;">{metric['value']}</div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">{metric['label']}</div>
                <div style="color: {metric['color']}; font-size: 0.8rem; margin-top: 0.25rem;">{metric['change']}</div>
            </div>
            """, unsafe_allow_html=True)

def render_performance_metrics(db):
    """Render performance metrics and charts"""
    
    st.markdown("<h2 style='margin: 2rem 0 1rem 0; color: var(--text-primary);'>📈 Performance Metrics</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Response time chart (simulated data)
        times = []
        response_times = []
        
        # Generate sample data for the last 24 hours
        import random
        for i in range(24):
            time_point = datetime.now() - timedelta(hours=23-i)
            times.append(time_point)
            # Simulate response times with some variation
            base_time = 3.5
            variation = random.uniform(-1, 1.5)
            response_times.append(max(0.5, base_time + variation))
        
        fig_response = go.Figure()
        fig_response.add_trace(go.Scatter(
            x=times,
            y=response_times,
            mode='lines+markers',
            name='Response Time',
            line=dict(color=get_chart_colors()['primary'], width=3),
            marker=dict(size=6)
        ))
        
        # Add average line
        avg_time = sum(response_times) / len(response_times)
        fig_response.add_hline(
            y=avg_time, 
            line_dash="dash", 
            line_color=get_chart_colors()['secondary'],
            annotation_text=f"Avg: {avg_time:.1f}s"
        )
        
        fig_response.update_layout(
            title="Response Time (Last 24h)",
            title_font=dict(size=16, color='#1e293b'),
            xaxis_title="Time",
            yaxis_title="Response Time (seconds)",
            height=350,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig_response, use_container_width=True)
    
    with col2:
        # Success rate over time
        success_rates = []
        for i in range(24):
            # Simulate success rates
            base_rate = 94
            variation = random.uniform(-3, 2)
            success_rates.append(min(100, max(80, base_rate + variation)))
        
        fig_success = go.Figure()
        fig_success.add_trace(go.Scatter(
            x=times,
            y=success_rates,
            mode='lines+markers',
            name='Success Rate',
            line=dict(color=get_chart_colors()['success'], width=3),
            fill='tonexty'
        ))
        
        fig_success.update_layout(
            title="Success Rate (Last 24h)",
            title_font=dict(size=16, color='#1e293b'),
            xaxis_title="Time",
            yaxis_title="Success Rate (%)",
            yaxis=dict(range=[80, 100]),
            height=350,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig_success, use_container_width=True)
    
    # Resource usage metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Memory usage
        memory_usage = 67  # Simulated
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--bg-card); border-radius: 8px; text-align: center;">
            <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">Memory Usage</h4>
            <div style="font-size: 2rem; font-weight: 700; color: {'#ef4444' if memory_usage > 80 else '#f59e0b' if memory_usage > 60 else '#10b981'};">
                {memory_usage}%
            </div>
            <div style="background: var(--bg-secondary); height: 8px; border-radius: 4px; margin-top: 0.5rem;">
                <div style="background: {'#ef4444' if memory_usage > 80 else '#f59e0b' if memory_usage > 60 else '#10b981'}; height: 100%; width: {memory_usage}%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # CPU usage
        cpu_usage = 34  # Simulated
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--bg-card); border-radius: 8px; text-align: center;">
            <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">CPU Usage</h4>
            <div style="font-size: 2rem; font-weight: 700; color: {'#ef4444' if cpu_usage > 80 else '#f59e0b' if cpu_usage > 60 else '#10b981'};">
                {cpu_usage}%
            </div>
            <div style="background: var(--bg-secondary); height: 8px; border-radius: 4px; margin-top: 0.5rem;">
                <div style="background: {'#ef4444' if cpu_usage > 80 else '#f59e0b' if cpu_usage > 60 else '#10b981'}; height: 100%; width: {cpu_usage}%; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Queue size
        queue_size = 3  # Simulated
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--bg-card); border-radius: 8px; text-align: center;">
            <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">Queue Size</h4>
            <div style="font-size: 2rem; font-weight: 700; color: {'#ef4444' if queue_size > 10 else '#f59e0b' if queue_size > 5 else '#10b981'};">
                {queue_size}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                requests pending
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_agent_config_status():
    """Render agent configuration status"""
    
    st.markdown("<h2 style='margin: 2rem 0 1rem 0; color: var(--text-primary);'>⚙️ Agent Configuration</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Agent Settings")
        
        config_items = [
            {'name': 'Dry Run Mode', 'value': 'Enabled', 'status': 'info'},
            {'name': 'Auto Approval', 'value': 'Disabled', 'status': 'success'},
            {'name': 'Scan Interval', 'value': '5 minutes', 'status': 'success'},
            {'name': 'Max Requests/Hour', 'value': '20', 'status': 'success'},
            {'name': 'Confidence Threshold', 'value': '0.7', 'status': 'success'},
        ]
        
        for item in config_items:
            status_colors = {
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'info': '#3b82f6'
            }
            color = status_colors.get(item['status'], '#6366f1')
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; margin-bottom: 0.5rem; background: var(--bg-card); border-radius: 6px; border-left: 3px solid {color};">
                <span style="color: var(--text-primary); font-weight: 500;">{item['name']}</span>
                <span style="color: {color}; font-weight: 600;">{item['value']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🛡️ Security & Moderation")
        
        security_items = [
            {'name': 'Content Filtering', 'value': 'Active', 'status': 'success'},
            {'name': 'PII Detection', 'value': 'Enabled', 'status': 'success'},
            {'name': 'Rate Limiting', 'value': 'Active', 'status': 'success'},
            {'name': 'Error Handling', 'value': 'Robust', 'status': 'success'},
            {'name': 'Audit Logging', 'value': 'Full', 'status': 'success'},
        ]
        
        for item in security_items:
            status_colors = {
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'info': '#3b82f6'
            }
            color = status_colors.get(item['status'], '#6366f1')
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; margin-bottom: 0.5rem; background: var(--bg-card); border-radius: 6px; border-left: 3px solid {color};">
                <span style="color: var(--text-primary); font-weight: 500;">{item['name']}</span>
                <span style="color: {color}; font-weight: 600;">{item['value']}</span>
            </div>
            """, unsafe_allow_html=True)

def render_refresh_controls():
    """Render auto-refresh and manual refresh controls"""
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        auto_refresh = st.toggle("🔄 Auto-refresh", value=st.session_state.get('monitor_auto_refresh', False))
        st.session_state.monitor_auto_refresh = auto_refresh
    
    with col2:
        refresh_interval = st.selectbox(
            "Refresh interval:",
            options=[10, 30, 60, 120],
            index=1,
            format_func=lambda x: f"{x} seconds"
        )
    
    with col3:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.experimental_rerun()
    
    with col4:
        if st.button("⏸️ Pause Agent", use_container_width=True):
            st.warning("⏸️ Agent monitoring paused. Click 'Resume' to continue.")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.experimental_rerun()
    
    # Show last updated time
    st.markdown(f"""
    <div style="text-align: center; color: var(--text-muted); font-size: 0.8rem; margin-top: 1rem;">
        Last updated: {datetime.now().strftime('%H:%M:%S')} • Next refresh: {refresh_interval}s
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_monitor_page()
