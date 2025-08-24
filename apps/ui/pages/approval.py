# apps/ui/pages/approval.py

import streamlit as st
import json
from datetime import datetime
import sys
import os

# Add parent directories to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.database import DatabaseManager
from utils.helpers import (
    format_timestamp, create_status_badge, format_confidence_score,
    parse_citations, format_processing_time, sanitize_input
)
from utils.agent_integration import agent_integration


def render_approval_page():
    """Render the request approval workflow page"""

    # Initialize database
    db = DatabaseManager()

    # Load agent settings (subreddits, thresholds, etc.)
    agent_settings = db.get_agent_settings()
    monitored_subs = agent_settings.get("monitored_subreddits", [])

    # Page header
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: var(--text-primary); margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">
            ✅ Request Approval Workflow
        </h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem;">
            Review, edit, and approve AI-generated responses before they're posted
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Get pending requests
    pending_requests = db.get_pending_requests()

    if not pending_requests:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: var(--bg-card); border-radius: 12px; margin: 2rem 0;">
            <h2 style="color: var(--text-primary); margin-bottom: 1rem;">🎉 All Caught Up!</h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 2rem;">
                No pending requests need approval right now.
            </p>
            <p style="color: var(--text-muted);">
                New requests will appear here when the agent finds relevant questions to answer.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Show recent approved/rejected requests
        st.markdown("<h2 style='margin: 2rem 0 1rem 0; color: var(--text-primary);'>📋 Recent Decisions</h2>", unsafe_allow_html=True)
        recent_requests = db.get_requests_by_filter({'limit': 10})

        for request in recent_requests:
            if request['status'] != 'pending':
                render_request_summary(request)
        return

    # Show summary stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Pending Reviews", len(pending_requests))

    with col2:
        high_confidence = sum(1 for r in pending_requests if r.get('agent_confidence', 0) >= 0.8)
        st.metric("High Confidence", high_confidence)

    with col3:
        avg_confidence = sum(r.get('agent_confidence', 0) for r in pending_requests) / len(pending_requests)
        st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")

    with col4:
        total_citations = sum(len(parse_citations(r.get('citations', '{}'))) for r in pending_requests)
        st.metric("Total Citations", total_citations)

    # Filter and sort options
    st.markdown("<h2 style='margin: 2rem 0 1rem 0; color: var(--text-primary);'>🔍 Filter & Sort</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        sort_option = st.selectbox(
            "Sort by",
            options=["newest", "oldest", "confidence_high", "confidence_low"],
            format_func=lambda x: {
                "newest": "Newest First",
                "oldest": "Oldest First",
                "confidence_high": "Highest Confidence",
                "confidence_low": "Lowest Confidence"
            }[x]
        )

    with col2:
        subreddit_options = ["all"]
        if monitored_subs:
            subreddit_options += monitored_subs
        else:
            subreddit_options += list(set(r['subreddit'] for r in pending_requests))

        subreddit_filter = st.selectbox(
            "Filter by Subreddit",
            options=subreddit_options,
            format_func=lambda x: "All Subreddits" if x == "all" else f"r/{x}"
        )

    with col3:
        confidence_filter = st.selectbox(
            "Confidence Level",
            options=["all", "high", "medium", "low"],
            format_func=lambda x: {
                "all": "All Confidence Levels",
                "high": "High (>80%)",
                "medium": "Medium (60-80%)",
                "low": "Low (<60%)"
            }[x]
        )

    # Apply filters and sorting
    filtered_requests = apply_filters(pending_requests, subreddit_filter, confidence_filter, sort_option)

    # Bulk actions
    st.markdown("<h2 style='margin: 2rem 0 1rem 0; color: var(--text-primary);'>⚡ Bulk Actions</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("✅ Approve All High Confidence", use_container_width=True):
            high_conf_requests = [r for r in filtered_requests if r.get('agent_confidence', 0) >= 0.8]
            success_count = 0
            for req in high_conf_requests:
                res = agent_integration.approve_request(req['id'], req.get('drafted_reply', ''), post_to_reddit=True)
                if res.get('status') in ["success", "dry_run"]:
                    success_count += 1
            st.success(f"Approved {success_count} high confidence requests!")
            st.rerun()

    with col2:
        if st.button("⏭️ Skip Low Confidence", use_container_width=True):
            st.info("Low confidence requests moved to review queue")

    with col3:
        if st.button("🔄 Refresh Queue", use_container_width=True):
            st.rerun()

    with col4:
        export_pending = st.button("📤 Export Pending", use_container_width=True)
        if export_pending:
            # Export functionality would go here
            st.success("Pending requests exported to CSV!")

    # Individual request reviews
    st.markdown("<h2 style='margin: 2rem 0 1rem 0; color: var(--text-primary);'>📝 Review Queue</h2>", unsafe_allow_html=True)

    if filtered_requests:
        # Show results count
        st.markdown(f"<p style='color: var(--text-secondary); margin-bottom: 1rem;'>Showing {len(filtered_requests)} of {len(pending_requests)} requests</p>", unsafe_allow_html=True)

        for i, request in enumerate(filtered_requests):
            render_request_review(request, db, i)
    else:
        st.info("No requests match your current filters.")


def apply_filters(requests, subreddit_filter, confidence_filter, sort_option):
    """Apply filters and sorting to requests"""
    filtered = requests.copy()

    # Filter by subreddit
    if subreddit_filter != "all":
        filtered = [r for r in filtered if r['subreddit'] == subreddit_filter]

    # Filter by confidence
    if confidence_filter == "high":
        filtered = [r for r in filtered if r.get('agent_confidence', 0) >= 0.8]
    elif confidence_filter == "medium":
        filtered = [r for r in filtered if 0.6 <= r.get('agent_confidence', 0) < 0.8]
    elif confidence_filter == "low":
        filtered = [r for r in filtered if r.get('agent_confidence', 0) < 0.6]

    # Sort
    if sort_option == "newest":
        filtered.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_option == "oldest":
        filtered.sort(key=lambda x: x['created_at'])
    elif sort_option == "confidence_high":
        filtered.sort(key=lambda x: x.get('agent_confidence', 0), reverse=True)
    elif sort_option == "confidence_low":
        filtered.sort(key=lambda x: x.get('agent_confidence', 0))

    return filtered


def render_request_review(request, db, index):
    """Render individual request review card"""

    # Create expandable review card
    with st.expander(
        f"📝 {request['post_title'][:80]}{'...' if len(request['post_title']) > 80 else ''} "
        f"• r/{request['subreddit']} • {format_confidence_score(request.get('agent_confidence'))}",
        expanded=(index == 0)  # Expand first item by default
    ):
        # Request metadata
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"**📅 Created:** {format_timestamp(request['created_at'])}")
            st.markdown(f"**👤 Author:** u/{request.get('post_author', 'Unknown')}")

        with col2:
            st.markdown(f"**🏷️ Subreddit:** r/{request['subreddit']}")
            st.markdown(f"**🎯 Confidence:** {format_confidence_score(request.get('agent_confidence'))}")

        with col3:
            processing_time = format_processing_time(request.get('processing_time'))
            st.markdown(f"**⏱️ Processing:** {processing_time}")
            moderation_score = request.get('moderation_score', 0)
            mod_color = "🟢" if moderation_score < 0.3 else "🟡" if moderation_score < 0.7 else "🔴"
            st.markdown(f"**🛡️ Safety:** {mod_color} {moderation_score*100:.0f}%")

        # Original post content
        st.markdown("### 📝 Original Question")
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--bg-secondary); border-radius: 8px; border-left: 3px solid var(--primary-color); margin: 1rem 0;">
            <strong>Title:</strong> {request['post_title']}<br><br>
            <strong>Content:</strong><br>
            {request.get('post_content', 'No content available') or 'No content available'}
        </div>
        """, unsafe_allow_html=True)

        # Show Reddit URL if available
        if request.get('post_url'):
            st.markdown(f"[🔗 View on Reddit]({request['post_url']})")

        # AI-generated response
        st.markdown("### 🤖 AI-Generated Response")

        # Show citations if available
        citations = parse_citations(request.get('citations', '{}'))
        if citations:
            st.markdown("**📚 Sources Used:**")
            for citation in citations:
                st.markdown(f"- {citation.get('title', 'Unknown source')}")

        # Editable response text
        edited_reply = st.text_area(
            "Response (edit if needed):",
            value=request.get('drafted_reply', ''),
            height=200,
            key=f"reply_{request['id']}"
        )

        # Moderation warnings
        if request.get('moderation_score', 0) > 0.5:
            st.warning("⚠️ This response may need additional review due to moderation flags.")

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("✅ Approve", key=f"approve_{request['id']}", use_container_width=True):
                final_reply = sanitize_input(edited_reply)
                result = agent_integration.approve_request(request['id'], final_reply, post_to_reddit=True)
                status = result.get('status')
                if status in ["success", "dry_run"]:
                    st.success(f"✅ Approved! {result.get('message', '')}")
                else:
                    st.warning(f"Approved locally, but posting failed: {result.get('message', 'Unknown error')}")
                st.rerun()

        with col2:
            if st.button("❌ Reject", key=f"reject_{request['id']}", use_container_width=True):
                feedback = st.text_input(f"Rejection reason (optional):", key=f"feedback_{request['id']}")
                result = agent_integration.reject_request(request['id'], feedback)
                if result.get('status') == 'success':
                    st.error("❌ Request rejected")
                else:
                    st.error(f"❌ Failed to reject: {result.get('message', 'Unknown error')}")
                st.rerun()

        with col3:
            if st.button("⏳ Defer", key=f"defer_{request['id']}", use_container_width=True):
                # Keep as pending but mark for later review
                db.log_user_action('defer', request['id'], 'admin')
                st.info("⏳ Request deferred for later review")

        with col4:
            if st.button("🔍 Details", key=f"details_{request['id']}", use_container_width=True):
                # Show detailed information in a modal-like expander
                with st.expander("🔍 Detailed Information", expanded=True):
                    st.json({
                        'request_id': request['id'],
                        'timestamp': request['created_at'],
                        'processing_time': request.get('processing_time'),
                        'confidence': request.get('agent_confidence'),
                        'moderation_flags': json.loads(request.get('moderation_flags', '[]')),
                        'citations': citations
                    })


def render_request_summary(request):
    """Render summary of completed request"""
    status_color = {
        'approved': '#10b981',
        'rejected': '#ef4444'
    }.get(request['status'], '#6366f1')

    st.markdown(f"""
    <div style="padding: 1rem; margin: 1rem 0; background: var(--bg-card); border-radius: 8px; border-left: 3px solid {status_color};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <strong style="color: var(--text-primary);">{request['post_title'][:100]}{'...' if len(request['post_title']) > 100 else ''}</strong>
            {create_status_badge(request['status'])}
        </div>
        <div style="color: var(--text-secondary); font-size: 0.9rem;">
            r/{request['subreddit']} • {format_timestamp(request['created_at'])} • {format_confidence_score(request.get('agent_confidence'))}
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_approval_page()
