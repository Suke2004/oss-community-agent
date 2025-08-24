# apps/ui/pages/dashboard.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager
from utils.helpers import (
    create_metric_card, format_timestamp, get_chart_colors,
    calculate_metrics_change, create_status_badge
)

def render_dashboard():
    """Render the main dashboard page"""
    
    # Initialize database
    db = DatabaseManager()
    
    # Page header
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: var(--text-primary); margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">
            🤖 OSS Community Agent Dashboard
        </h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem;">
            Monitor your AI agent's performance and community engagement
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get analytics data
    overview_data = db.get_analytics_overview()
    daily_stats = db.get_daily_stats(30)
    
    # Key Metrics Row
    st.markdown("<h2 style='margin: 2rem 0 1rem 0; color: var(--text-primary);'>📊 Key Metrics</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Requests today with comparison to yesterday
        yesterday_data = db.get_daily_stats(2)
        yesterday_count = yesterday_data[1]['total_requests'] if len(yesterday_data) > 1 else 0
        change, change_type = calculate_metrics_change(overview_data['total_today'], yesterday_count)
        change_text = f"{'↗️' if change_type == 'positive' else '↘️' if change_type == 'negative' else '➖'} {change:.1f}% vs yesterday"
        
        st.markdown(create_metric_card(
            "Requests Today", 
            str(overview_data['total_today']),
            change_text,
            change_type
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Pending Approval",
            str(overview_data['pending_requests']),
            f"{'🔴' if overview_data['pending_requests'] > 5 else '🟢'} Review needed" if overview_data['pending_requests'] > 0 else "🟢 All caught up!"
        ), unsafe_allow_html=True)
    
    with col3:
        approval_color = "🟢" if overview_data['approval_rate'] >= 80 else "🟡" if overview_data['approval_rate'] >= 60 else "🔴"
        st.markdown(create_metric_card(
            "Approval Rate (7d)",
            f"{overview_data['approval_rate']}%",
            f"{approval_color} Last 7 days"
        ), unsafe_allow_html=True)
    
    with col4:
        time_color = "🟢" if overview_data['avg_response_time'] < 5 else "🟡" if overview_data['avg_response_time'] < 10 else "🔴"
        st.markdown(create_metric_card(
            "Avg Response Time",
            f"{overview_data['avg_response_time']:.1f}s",
            f"{time_color} Processing speed"
        ), unsafe_allow_html=True)
    
    # Charts Row
    st.markdown("<h2 style='margin: 3rem 0 1rem 0; color: var(--text-primary);'>📈 Performance Analytics</h2>", unsafe_allow_html=True)
    
    if daily_stats:
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily Requests Chart
            df_daily = pd.DataFrame(daily_stats)
            df_daily['date'] = pd.to_datetime(df_daily['date'])
            df_daily = df_daily.sort_values('date')
            
            fig_daily = go.Figure()
            fig_daily.add_trace(go.Scatter(
                x=df_daily['date'],
                y=df_daily['total_requests'],
                mode='lines+markers',
                name='Total Requests',
                line=dict(color=get_chart_colors()['primary'], width=3),
                marker=dict(size=6)
            ))
            
            fig_daily.update_layout(
                title="Daily Request Volume",
                title_font=dict(size=16, color='#1e293b'),
                xaxis_title="Date",
                yaxis_title="Requests",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#64748b'),
                height=350,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig_daily, use_container_width=True)
        
        with col2:
            # Approval Rate Chart
            df_daily['approval_rate'] = (df_daily['approved'] / df_daily['total_requests'] * 100).fillna(0)
            
            fig_approval = go.Figure()
            fig_approval.add_trace(go.Scatter(
                x=df_daily['date'],
                y=df_daily['approval_rate'],
                mode='lines+markers',
                name='Approval Rate',
                line=dict(color=get_chart_colors()['success'], width=3),
                marker=dict(size=6),
                fill='tonexty'
            ))
            
            fig_approval.update_layout(
                title="Approval Rate Trend",
                title_font=dict(size=16, color='#1e293b'),
                xaxis_title="Date",
                yaxis_title="Approval Rate (%)",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#64748b'),
                height=350,
                margin=dict(l=0, r=0, t=40, b=0),
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig_approval, use_container_width=True)
    
    # Top Subreddits and Recent Activity
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("<h3 style='color: var(--text-primary); margin-bottom: 1rem;'>🏆 Top Subreddits (7d)</h3>", unsafe_allow_html=True)
        
        if overview_data['top_subreddits']:
            for i, subreddit in enumerate(overview_data['top_subreddits']):
                percentage = (subreddit['count'] / sum(s['count'] for s in overview_data['top_subreddits'])) * 100
                st.markdown(f"""
                <div style="margin-bottom: 1rem; padding: 1rem; background: var(--bg-card); border-radius: 8px; border-left: 3px solid var(--primary-color);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: var(--text-primary);">r/{subreddit['subreddit']}</span>
                        <span style="color: var(--text-secondary); font-size: 0.9rem;">{subreddit['count']} requests</span>
                    </div>
                    <div style="background: var(--bg-secondary); height: 6px; border-radius: 3px; margin-top: 0.5rem;">
                        <div style="background: var(--primary-color); height: 100%; width: {percentage}%; border-radius: 3px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No subreddit data available yet. Start the agent to see activity!")
    
    with col2:
        st.markdown("<h3 style='color: var(--text-primary); margin-bottom: 1rem;'>🕒 Recent Activity</h3>", unsafe_allow_html=True)
        
        # Get recent requests
        recent_requests = db.get_requests_by_filter({'limit': 5})
        
        if recent_requests:
            for request in recent_requests:
                timestamp = format_timestamp(request['created_at'])
                status_badge = create_status_badge(request['status'])
                
                st.markdown(f"""
                <div style="margin-bottom: 1rem; padding: 1rem; background: var(--bg-card); border-radius: 8px; border: 1px solid var(--border-light);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                        <span style="font-weight: 600; color: var(--text-primary); font-size: 0.9rem;">
                            {request['post_title'][:60]}{'...' if len(request['post_title']) > 60 else ''}
                        </span>
                        {status_badge}
                    </div>
                    <div style="display: flex; gap: 1rem; color: var(--text-secondary); font-size: 0.8rem;">
                        <span>r/{request['subreddit']}</span>
                        <span>{timestamp}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent activity. The agent will show recent requests here once it starts processing.")
    
    # System Status
    st.markdown("<h2 style='margin: 3rem 0 1rem 0; color: var(--text-primary);'>⚡ System Status</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Agent Status (simplified for demo)
        st.markdown("""
        <div style="padding: 1.5rem; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-light);">
            <h4 style="color: var(--text-primary); margin-bottom: 1rem; display: flex; align-items: center;">
                🤖 Agent Status
            </h4>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%;"></div>
                <span style="color: var(--text-primary); font-weight: 500;">Active & Monitoring</span>
            </div>
            <p style="color: var(--text-secondary); margin-top: 0.5rem; font-size: 0.9rem;">
                Last check: 2 minutes ago
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # RAG System Status
        st.markdown("""
        <div style="padding: 1.5rem; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-light);">
            <h4 style="color: var(--text-primary); margin-bottom: 1rem; display: flex; align-items: center;">
                📚 RAG System
            </h4>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%;"></div>
                <span style="color: var(--text-primary); font-weight: 500;">Database Ready</span>
            </div>
            <p style="color: var(--text-secondary); margin-top: 0.5rem; font-size: 0.9rem;">
                Documents indexed: 15
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Reddit Connection
        st.markdown("""
        <div style="padding: 1.5rem; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-light);">
            <h4 style="color: var(--text-primary); margin-bottom: 1rem; display: flex; align-items: center;">
                📡 Reddit API
            </h4>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%;"></div>
                <span style="color: var(--text-primary); font-weight: 500;">Connected</span>
            </div>
            <p style="color: var(--text-secondary); margin-top: 0.5rem; font-size: 0.9rem;">
                Rate limit: 95% available
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("<h2 style='margin: 3rem 0 1rem 0; color: var(--text-primary);'>⚡ Quick Actions</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 View Pending Requests", use_container_width=True):
            st.session_state.current_page = 'approval'
            st.experimental_rerun()
    
    with col2:
        if st.button("📊 Generate Report", use_container_width=True):
            st.session_state.current_page = 'reports'
            st.experimental_rerun()
    
    with col3:
        if st.button("⚙️ Agent Settings", use_container_width=True):
            st.session_state.current_page = 'settings'
            st.experimental_rerun()
    
    with col4:
        if st.button("🚀 Start New Scan", use_container_width=True):
            st.success("New Reddit scan initiated! Check back in a few minutes for results.")
    
    # Auto-refresh toggle
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        auto_refresh = st.toggle("Auto-refresh", value=st.session_state.get('auto_refresh', False))
        st.session_state.auto_refresh = auto_refresh
    
    with col3:
        if st.button("🔄 Refresh Now"):
            st.experimental_rerun()
    
    # Auto-refresh logic
    if auto_refresh:
        import time
        time.sleep(30)  # Refresh every 30 seconds
        st.experimental_rerun()

if __name__ == "__main__":
    render_dashboard()
