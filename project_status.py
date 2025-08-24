#!/usr/bin/env python3
"""
OSS Community Agent - Project Status Checker
Comprehensive analysis of project completion and readiness
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ProjectStatusChecker:
    """Comprehensive project status analysis"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.status = {}
        
    def check_core_components(self) -> Dict[str, Any]:
        """Check core application components"""
        components = {
            "agent_main": "apps/agent/main.py",
            "streamlit_app": "apps/ui/streamlit_app.py",
            "reddit_tool": "tools/reddit_tool.py",
            "rag_tool": "tools/rag_tool.py",
            "moderation_tool": "tools/moderation_tools.py",
            "mock_portia": "mock_portia.py",
            "database": "apps/ui/utils/database.py",
            "requirements": "infra/requirements.txt",
            "env_example": ".env.example",
            "env_file": ".env",
            "start_script": "start.sh",
            "ui_runner": "run_ui.py",
            "full_runner": "run_full_system.py"
        }
        
        results = {}
        for name, path in components.items():
            file_path = self.project_root / path
            results[name] = {
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "path": path
            }
        
        return results
    
    def check_ui_components(self) -> Dict[str, Any]:
        """Check UI components and pages"""
        ui_components = {
            "dashboard": "apps/ui/pages/dashboard.py",
            "approval": "apps/ui/pages/approval.py",
            "logs": "apps/ui/pages/logs.py",
            "monitor": "apps/ui/pages/monitor.py",
            "settings": "apps/ui/pages/settings.py",
            "helpers": "apps/ui/utils/helpers.py",
            "agent_integration": "apps/ui/utils/agent_integration.py",
            "css_styles": "apps/ui/styles/main.css"
        }
        
        results = {}
        for name, path in ui_components.items():
            file_path = self.project_root / path
            results[name] = {
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "path": path
            }
        
        return results
    
    def check_documentation(self) -> Dict[str, Any]:
        """Check documentation and corpus"""
        docs = {
            "readme": "README.md",
            "env_guide": "ENV_FILES_GUIDE.md",
            "env_status": "ENVIRONMENT_STATUS.md",
            "vscode_setup": "VSCODE_SETUP.md",
            "python_basics": "data/corpus/python_basics.md",
            "web_development": "data/corpus/web_development.md",
            "faq": "data/corpus/faq.md",
            "getting_started": "data/corpus/getting_started.md"
        }
        
        results = {}
        for name, path in docs.items():
            file_path = self.project_root / path
            results[name] = {
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "path": path
            }
        
        return results
    
    def check_testing(self) -> Dict[str, Any]:
        """Check testing infrastructure"""
        tests = {
            "test_agent": "tests/test_agent.py",
            "test_tools": "tests/test_tools.py",
            "test_runner": "run_tests.py"
        }
        
        results = {}
        for name, path in tests.items():
            file_path = self.project_root / path
            results[name] = {
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "path": path
            }
        
        return results
    
    def check_data_storage(self) -> Dict[str, Any]:
        """Check data storage and databases"""
        storage = {
            "main_db": "data/agent_data.db",
            "ui_db": "apps/ui/data/agent_data.db",
            "rag_db": "rag_db/chroma.sqlite3",
            "logs_dir": "data/logs"
        }
        
        results = {}
        for name, path in storage.items():
            file_path = self.project_root / path
            if file_path.is_file():
                results[name] = {
                    "exists": True,
                    "size": file_path.stat().st_size,
                    "type": "file",
                    "path": path
                }
            elif file_path.is_dir():
                results[name] = {
                    "exists": True,
                    "size": sum(f.stat().st_size for f in file_path.rglob('*') if f.is_file()),
                    "type": "directory",
                    "path": path
                }
            else:
                results[name] = {
                    "exists": False,
                    "size": 0,
                    "type": "missing",
                    "path": path
                }
        
        return results
    
    def check_environment(self) -> Dict[str, Any]:
        """Check environment and dependencies"""
        # Check Python version
        python_version = sys.version_info
        python_ok = python_version >= (3, 10)
        
        # Check key packages
        packages = [
            'streamlit', 'praw', 'chromadb', 'langchain', 
            'pandas', 'plotly', 'requests', 'psutil'
        ]
        
        package_status = {}
        for package in packages:
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                package_status[package] = {
                    "installed": True,
                    "version": version
                }
            except ImportError:
                package_status[package] = {
                    "installed": False,
                    "version": None
                }
        
        # Check environment variables
        env_vars = [
            'REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 
            'REDDIT_USERNAME', 'REDDIT_PASSWORD'
        ]
        
        env_status = {}
        for var in env_vars:
            env_status[var] = {
                "set": bool(os.getenv(var)),
                "value": "***" if os.getenv(var) else None
            }
        
        return {
            "python_version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            "python_ok": python_ok,
            "packages": package_status,
            "environment_variables": env_status
        }
    
    def calculate_completion_percentage(self) -> Dict[str, float]:
        """Calculate completion percentages for different areas"""
        percentages = {}
        
        # Core components (40% weight)
        core_components = self.check_core_components()
        core_existing = sum(1 for comp in core_components.values() if comp["exists"])
        core_total = len(core_components)
        percentages["core_components"] = (core_existing / core_total) * 100
        
        # UI components (25% weight)
        ui_components = self.check_ui_components()
        ui_existing = sum(1 for comp in ui_components.values() if comp["exists"])
        ui_total = len(ui_components)
        percentages["ui_components"] = (ui_existing / ui_total) * 100
        
        # Documentation (15% weight)
        docs = self.check_documentation()
        docs_existing = sum(1 for doc in docs.values() if doc["exists"])
        docs_total = len(docs)
        percentages["documentation"] = (docs_existing / docs_total) * 100
        
        # Testing (10% weight)
        tests = self.check_testing()
        tests_existing = sum(1 for test in tests.values() if test["exists"])
        tests_total = len(tests)
        percentages["testing"] = (tests_existing / tests_total) * 100
        
        # Data storage (10% weight)
        storage = self.check_data_storage()
        storage_existing = sum(1 for item in storage.values() if item["exists"])
        storage_total = len(storage)
        percentages["data_storage"] = (storage_existing / storage_total) * 100
        
        # Overall weighted completion
        weights = {
            "core_components": 0.40,
            "ui_components": 0.25,
            "documentation": 0.15,
            "testing": 0.10,
            "data_storage": 0.10
        }
        
        overall = sum(percentages[area] * weights[area] for area in weights.keys())
        percentages["overall"] = overall
        
        return percentages
    
    def get_pending_items(self) -> Dict[str, List[str]]:
        """Get list of pending/missing items"""
        pending = {
            "critical": [],
            "important": [],
            "nice_to_have": []
        }
        
        # Check core components
        core_components = self.check_core_components()
        for name, info in core_components.items():
            if not info["exists"]:
                if name in ["agent_main", "streamlit_app", "reddit_tool", "rag_tool"]:
                    pending["critical"].append(f"Missing {name}: {info['path']}")
                else:
                    pending["important"].append(f"Missing {name}: {info['path']}")
        
        # Check environment
        env = self.check_environment()
        if not env["python_ok"]:
            pending["critical"].append("Python version below 3.10 (using mock Portia)")
        
        missing_packages = [pkg for pkg, info in env["packages"].items() if not info["installed"]]
        if missing_packages:
            pending["important"].extend([f"Missing package: {pkg}" for pkg in missing_packages])
        
        missing_env_vars = [var for var, info in env["environment_variables"].items() if not info["set"]]
        if missing_env_vars:
            pending["important"].extend([f"Missing environment variable: {var}" for var in missing_env_vars])
        
        return pending
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive project status report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_name": "OSS Community Agent",
            "completion_percentages": self.calculate_completion_percentage(),
            "core_components": self.check_core_components(),
            "ui_components": self.check_ui_components(),
            "documentation": self.check_documentation(),
            "testing": self.check_testing(),
            "data_storage": self.check_data_storage(),
            "environment": self.check_environment(),
            "pending_items": self.get_pending_items(),
            "recommendations": self.get_recommendations()
        }
        
        return report
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for project completion"""
        recommendations = []
        
        # Check Python version
        env = self.check_environment()
        if not env["python_ok"]:
            recommendations.append("Upgrade Python to 3.11+ for full Portia SDK support")
        
        # Check missing packages
        missing_packages = [pkg for pkg, info in env["packages"].items() if not info["installed"]]
        if missing_packages:
            recommendations.append(f"Install missing packages: pip install {' '.join(missing_packages)}")
        
        # Check environment variables
        missing_env_vars = [var for var, info in env["environment_variables"].items() if not info["set"]]
        if missing_env_vars:
            recommendations.append("Configure missing environment variables in .env file")
        
        # Check testing
        tests = self.check_testing()
        if not all(test["exists"] for test in tests.values()):
            recommendations.append("Complete test suite implementation")
        
        # General recommendations
        recommendations.extend([
            "Run comprehensive tests: python run_tests.py",
            "Test the UI: python run_ui.py",
            "Test full system: python run_full_system.py",
            "Monitor system health: python monitor.py"
        ])
        
        return recommendations

def print_status_report(report: Dict[str, Any]):
    """Print formatted status report"""
    print("🚀 OSS Community Agent - Project Status Report")
    print("=" * 60)
    print(f"Generated: {report['timestamp']}")
    print()
    
    # Overall completion
    overall = report["completion_percentages"]["overall"]
    print(f"📊 Overall Completion: {overall:.1f}%")
    
    # Progress bar
    filled = int(overall / 5)
    bar = "█" * filled + "░" * (20 - filled)
    print(f"Progress: [{bar}] {overall:.1f}%")
    print()
    
    # Detailed percentages
    print("📈 Detailed Completion:")
    for area, percentage in report["completion_percentages"].items():
        if area != "overall":
            print(f"  {area.replace('_', ' ').title()}: {percentage:.1f}%")
    print()
    
    # Pending items
    pending = report["pending_items"]
    if any(pending.values()):
        print("⚠️ Pending Items:")
        for priority, items in pending.items():
            if items:
                print(f"  {priority.title()}:")
                for item in items:
                    print(f"    • {item}")
        print()
    else:
        print("✅ No pending items!")
        print()
    
    # Recommendations
    if report["recommendations"]:
        print("💡 Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
        print()
    
    # Environment status
    env = report["environment"]
    print("🌍 Environment Status:")
    print(f"  Python: {env['python_version']} {'✅' if env['python_ok'] else '⚠️'}")
    
    missing_packages = [pkg for pkg, info in env["packages"].items() if not info["installed"]]
    if missing_packages:
        print(f"  Missing Packages: {', '.join(missing_packages)}")
    else:
        print("  All required packages installed ✅")
    
    missing_env_vars = [var for var, info in env["environment_variables"].items() if not info["set"]]
    if missing_env_vars:
        print(f"  Missing Environment Variables: {', '.join(missing_env_vars)}")
    else:
        print("  Environment variables configured ✅")
    print()
    
    # Final status
    if overall >= 90:
        print("🎉 Project is ready for production!")
    elif overall >= 75:
        print("✅ Project is mostly complete and functional!")
    elif overall >= 50:
        print("🟡 Project is partially complete - some work needed.")
    else:
        print("🔴 Project needs significant work to be functional.")
    
    print(f"\n📁 Project Root: {Path(__file__).parent.absolute()}")

def main():
    """Main function"""
    checker = ProjectStatusChecker()
    report = checker.generate_report()
    print_status_report(report)
    
    # Save report to file
    report_file = Path(__file__).parent / "project_status_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main()
