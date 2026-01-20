import os
import django
from django.conf import settings
import sys
from pathlib import Path

# Setup Django environment
sys.path.append('e:\\Django_Check')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_project.settings')
django.setup()

from core.utils import get_all_commands, save_custom_command, load_custom_commands

def verify_logic():
    print("Verifying Custom Command Logic...")
    
    # 1. Check initial commands (should have base commands)
    initial_commands = get_all_commands()
    print(f"Initial command count: {len(initial_commands)}")
    assert "compress_ultra" in initial_commands, "Base command missing"
    
    # 2. Add custom command
    print("Adding custom command...")
    test_key = "test_custom_cmd"
    test_cmd = ["ffmpeg", "-i", "{input}", "test.mp4"]
    test_desc = "Test Description"
    save_custom_command(test_key, test_cmd, test_desc)
    
    # 3. Verify it's loaded
    print("Verifying loaded commands...")
    updated_commands = get_all_commands()
    assert test_key in updated_commands, "Custom command not found in all commands"
    assert updated_commands[test_key]["description"] == test_desc
    print("Custom command verified successfully!")
    
    # 4. Clean up (optional, or leave it to show user)
    # Reverting changes to keep environment clean
    import json
    with open("custom_commands.json", "w") as f:
        json.dump({}, f)
    print("Cleanup complete.")

if __name__ == "__main__":
    verify_logic()
