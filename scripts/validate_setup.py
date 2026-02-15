"""
Validation script to check TODO list before running tasks
"""
import sys
import os


def read_todo():
    """Read TODO.md file"""
    todo_path = os.path.join(os.path.dirname(__file__), "..", "TODO.md")
    
    if not os.path.exists(todo_path):
        print("❌ ERROR: TODO.md not found!")
        return False
    
    with open(todo_path, 'r') as f:
        content = f.read()
    
    return content


def check_prerequisites():
    """Check if prerequisites are met"""
    print("=" * 60)
    print("CHECKING PREREQUISITES")
    print("=" * 60)
    
    checks = {
        "TODO.md exists": False,
        "Configuration example exists": False,
        "Requirements file exists": False,
    }
    
    # Check TODO.md
    todo_path = os.path.join(os.path.dirname(__file__), "..", "TODO.md")
    checks["TODO.md exists"] = os.path.exists(todo_path)
    
    # Check config
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env.example")
    checks["Configuration example exists"] = os.path.exists(config_path)
    
    # Check requirements
    req_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
    checks["Requirements file exists"] = os.path.exists(req_path)
    
    # Print results
    all_passed = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    return all_passed


def validate_setup():
    """Main validation function"""
    print("\n🔍 PSI-FREQ SCALPER SETUP VALIDATOR\n")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed!")
        print("Please ensure all required files are in place.")
        return False
    
    # Read TODO
    todo_content = read_todo()
    if not todo_content:
        return False
    
    print("\n📋 TODO LIST SUMMARY:")
    print("-" * 60)
    
    # Count tasks
    total_tasks = todo_content.count("- [ ]") + todo_content.count("- [x]")
    completed_tasks = todo_content.count("- [x]")
    pending_tasks = todo_content.count("- [ ]")
    
    print(f"Total Tasks: {total_tasks}")
    print(f"Completed: {completed_tasks}")
    print(f"Pending: {pending_tasks}")
    print(f"Progress: {(completed_tasks/total_tasks*100) if total_tasks > 0 else 0:.1f}%")
    
    print("-" * 60)
    
    # Check if critical tasks are done
    critical_sections = [
        "IMPORTANT: Read Before Starting Any Task",
        "Setup and Configuration"
    ]
    
    print("\n⚠️  IMPORTANT REMINDERS:")
    print("1. Review TODO.md completely before starting any task")
    print("2. Configure API keys in config/.env (copy from .env.example)")
    print("3. Always test in paper trading mode first")
    print("4. Verify all dependencies are installed")
    
    print("\n" + "=" * 60)
    print("✅ Validation complete!")
    print("=" * 60 + "\n")
    
    return True


if __name__ == "__main__":
    success = validate_setup()
    sys.exit(0 if success else 1)
