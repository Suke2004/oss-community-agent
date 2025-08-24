#!/usr/bin/env python3
"""
Production Monitoring Script for OSS Community Agent
Monitors system health, performance, and provides alerts
"""

import os
import sys
import time
import json
import logging
import psutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Ensure logs directory exists
Path('data/logs').mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring and health checks"""
    
    def __init__(self):
        self.db_path = "data/agent_data.db"
        self.start_time = datetime.now()
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database health
            db_health = self.check_database_health()
            
            # Agent health
            agent_health = self.check_agent_health()
            
            # Process monitoring
            process_info = self.get_process_info()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                },
                "database": db_health,
                "agent": agent_health,
                "processes": process_info,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"error": str(e)}
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check table sizes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            table_stats = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_stats[table_name] = count
            
            # Check recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM requests 
                WHERE created_at > datetime('now', '-1 hour')
            """)
            recent_requests = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "status": "healthy",
                "tables": table_stats,
                "recent_requests_1h": recent_requests,
                "connection": "ok"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "connection": "failed"
            }
    
    def check_agent_health(self) -> Dict[str, Any]:
        """Check agent system health"""
        try:
            # Check if agent files exist
            agent_files = [
                "apps/agent/main.py",
                "tools/reddit_tool.py",
                "tools/rag_tool.py",
                "tools/moderation_tools.py"
            ]
            
            missing_files = []
            for file_path in agent_files:
                if not Path(file_path).exists():
                    missing_files.append(file_path)
            
            # Check environment variables
            required_env_vars = [
                "REDDIT_CLIENT_ID",
                "REDDIT_CLIENT_SECRET",
                "REDDIT_USERNAME",
                "REDDIT_PASSWORD"
            ]
            
            missing_env_vars = []
            for var in required_env_vars:
                if not os.getenv(var):
                    missing_env_vars.append(var)
            
            # Check RAG database
            rag_db_exists = Path("rag_db/chroma.sqlite3").exists()
            
            return {
                "status": "healthy" if not missing_files and not missing_env_vars else "warning",
                "missing_files": missing_files,
                "missing_env_vars": missing_env_vars,
                "rag_database": "ok" if rag_db_exists else "missing",
                "mock_portia": Path("mock_portia.py").exists()
            }
        except Exception as e:
            logger.error(f"Agent health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get information about running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['name'] and proc_info['cpu_percent'] > 0:
                        processes.append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "cpu_percent": proc_info['cpu_percent'],
                            "memory_percent": proc_info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                "total_processes": len(processes),
                "top_processes": processes[:10]  # Top 10 by CPU usage
            }
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return {"error": str(e)}
    
    def check_alerts(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for system alerts based on health data"""
        alerts = []
        
        # CPU alert
        if health_data.get("system", {}).get("cpu_percent", 0) > 80:
            alerts.append({
                "level": "warning",
                "message": f"High CPU usage: {health_data['system']['cpu_percent']}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # Memory alert
        if health_data.get("system", {}).get("memory_percent", 0) > 85:
            alerts.append({
                "level": "warning",
                "message": f"High memory usage: {health_data['system']['memory_percent']}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # Disk alert
        if health_data.get("system", {}).get("disk_percent", 0) > 90:
            alerts.append({
                "level": "critical",
                "message": f"Low disk space: {health_data['system']['disk_percent']}% used",
                "timestamp": datetime.now().isoformat()
            })
        
        # Database alert
        if health_data.get("database", {}).get("status") == "error":
            alerts.append({
                "level": "critical",
                "message": "Database connection failed",
                "timestamp": datetime.now().isoformat()
            })
        
        # Agent alert
        agent_health = health_data.get("agent", {})
        if agent_health.get("status") == "error":
            alerts.append({
                "level": "critical",
                "message": "Agent system error",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def save_health_data(self, health_data: Dict[str, Any]):
        """Save health data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create health_logs table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    health_data TEXT,
                    alerts TEXT
                )
            """)
            
            # Insert health data
            alerts = self.check_alerts(health_data)
            cursor.execute("""
                INSERT INTO health_logs (health_data, alerts)
                VALUES (?, ?)
            """, (json.dumps(health_data), json.dumps(alerts)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving health data: {e}")
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health data history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, health_data, alerts
                FROM health_logs
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
            """.format(hours))
            
            results = cursor.fetchall()
            conn.close()
            
            history = []
            for row in results:
                history.append({
                    "timestamp": row[0],
                    "health_data": json.loads(row[1]),
                    "alerts": json.loads(row[2])
                })
            
            return history
        except Exception as e:
            logger.error(f"Error getting health history: {e}")
            return []

def main():
    """Main monitoring function"""
    print("🔍 OSS Community Agent - System Monitor")
    print("=" * 50)
    
    monitor = SystemMonitor()
    
    try:
        while True:
            # Get system health
            health_data = monitor.get_system_health()
            
            # Save to database
            monitor.save_health_data(health_data)
            
            # Check for alerts
            alerts = monitor.check_alerts(health_data)
            
            # Display current status
            print(f"\n📊 System Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 40)
            
            # System metrics
            system = health_data.get("system", {})
            print(f"CPU: {system.get('cpu_percent', 0):.1f}%")
            print(f"Memory: {system.get('memory_percent', 0):.1f}%")
            print(f"Disk: {system.get('disk_percent', 0):.1f}%")
            
            # Database status
            db_status = health_data.get("database", {}).get("status", "unknown")
            print(f"Database: {db_status}")
            
            # Agent status
            agent_status = health_data.get("agent", {}).get("status", "unknown")
            print(f"Agent: {agent_status}")
            
            # Display alerts
            if alerts:
                print("\n🚨 Alerts:")
                for alert in alerts:
                    print(f"  [{alert['level'].upper()}] {alert['message']}")
            else:
                print("\n✅ No alerts")
            
            # Wait before next check
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Monitoring error: {e}")
        print(f"\n❌ Monitoring error: {e}")

if __name__ == "__main__":
    main()
