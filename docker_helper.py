"""
Docker Helper Script for RAG Engine
Provides convenient commands for Docker operations
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(message):
    print(f"\n{'='*70}")
    print(f"  {message}")
    print(f"{'='*70}\n")


def run_command(cmd, description=""):
    """Run a shell command and handle errors"""
    if description:
        print(f"→ {description}")
    try:
        subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e}")
        return False


def docker_build():
    """Build Docker image"""
    print_header("Building Docker Image")
    return run_command("docker-compose build", "Building image...")


def docker_up_dev():
    """Start development environment"""
    print_header("Starting Development Environment (with hot-reload)")
    print("🔍 Tips:")
    print("  • Edit code and changes will reload automatically")
    print("  • Access API at http://localhost:8000/docs")
    print("  • View logs: docker-compose logs -f")
    print("  • Stop: CTRL+C\n")
    return run_command("docker-compose up", "Starting containers...")


def docker_up_prod():
    """Start production environment"""
    print_header("Starting Production Environment")
    print("⚠️  Notes:")
    print("  • No hot-reload (code cannot be modified)")
    print("  • Optimized for performance")
    print("  • Resource limits applied")
    print("  • Access API at http://localhost:8000/docs\n")
    return run_command("docker-compose -f docker-compose.prod.yml up", "Starting containers...")


def docker_down():
    """Stop and remove containers"""
    print_header("Stopping Containers")
    return run_command("docker-compose down", "Stopping containers...")


def docker_logs():
    """View live logs"""
    print_header("Real-time Logs")
    print("Press CTRL+C to stop\n")
    return run_command("docker-compose logs -f", "Streaming logs...")


def docker_bash():
    """Open bash shell in container"""
    print_header("Opening Container Shell")
    print("Type 'exit' to return\n")
    return run_command("docker-compose exec rag-engine bash", "")


def docker_status():
    """Check container status"""
    print_header("Container Status")
    run_command("docker ps --filter 'name=rag-engine'", "")
    return True


def docker_health():
    """Check health status"""
    print_header("Health Check")
    run_command("curl -s http://localhost:8000/health | python -m json.tool", "Checking API health...")
    return True


def docker_stats():
    """Show container statistics"""
    print_header("Container Statistics")
    print("(Press CTRL+C to stop)\n")
    return run_command("docker stats --no-stream rag-engine-app", "")


def docker_clean():
    """Clean up Docker resources"""
    print_header("Cleanup")
    print("Removing stopped containers...")
    run_command("docker-compose down", "")
    print("\nRemoving unused images...")
    run_command("docker image prune -f", "")
    print("\n✅ Cleanup complete")
    return True


def docker_db_info():
    """Show database information"""
    print_header("Database Information")
    
    # SQLite info
    print("📁 SQLite Database:")
    run_command("docker-compose exec rag-engine ls -lh /app/data/database.db 2>/dev/null || echo '❌ Database not created yet'", "")
    
    # FAISS info
    print("\n📁 FAISS Index:")
    run_command("docker-compose exec rag-engine ls -lh /app/data/vector.index 2>/dev/null || echo '❌ Index not created yet'", "")
    
    # Logs info
    print("\n📁 Logs:")
    run_command("docker-compose exec rag-engine ls -lh /app/data/logs/ 2>/dev/null || echo '❌ No logs yet'", "")
    
    return True


def show_menu():
    """Display interactive menu"""
    print_header("🐳 RAG Engine - Docker Control Menu")
    print("Choose an option:\n")
    print("  1. 🏗️  Build Docker image")
    print("  2. 🚀 Start development environment (with hot-reload)")
    print("  3. 🚀 Start production environment")
    print("  4. ⏹️  Stop all containers")
    print("  5. 📋 View logs")
    print("  6. 💻 Open container shell")
    print("  7. 📊 Check container status")
    print("  8. 💚 Health check")
    print("  9. 📈 Container statistics")
    print(" 10. 🧹 Cleanup Docker resources")
    print(" 11. 💾 Database information")
    print("  0. ❌ Exit")
    print()


def main():
    if len(sys.argv) > 1:
        # Command line argument provided
        command = sys.argv[1].lower()
        
        commands = {
            'build': docker_build,
            'up-dev': docker_up_dev,
            'up-prod': docker_up_prod,
            'down': docker_down,
            'logs': docker_logs,
            'bash': docker_bash,
            'status': docker_status,
            'health': docker_health,
            'stats': docker_stats,
            'clean': docker_clean,
            'db-info': docker_db_info,
        }
        
        if command in commands:
            commands[command]()
            return
        
        print(f"❌ Unknown command: {command}")
        print("\nAvailable commands:")
        for cmd in commands.keys():
            print(f"  python docker_helper.py {cmd}")
        return
    
    # Interactive menu
    while True:
        show_menu()
        choice = input("Enter your choice (0-11): ").strip()
        
        commands = {
            '1': docker_build,
            '2': docker_up_dev,
            '3': docker_up_prod,
            '4': docker_down,
            '5': docker_logs,
            '6': docker_bash,
            '7': docker_status,
            '8': docker_health,
            '9': docker_stats,
            '10': docker_clean,
            '11': docker_db_info,
            '0': lambda: sys.exit(0),
        }
        
        if choice in commands:
            commands[choice]()
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
