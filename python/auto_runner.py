import subprocess
import time

# Command to be monitored and restarted
command = ["python", "run_bot.py", "-r", "-t", "f6abe600-faa8-441e-b0aa-41045dcc47bf"]

def is_process_running(cmd):
    """Check if a process with the specified command is running."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        process_list = result.stdout
        cmd_str = ' '.join(cmd)
        return cmd_str in process_list
    except Exception as e:
        print(f"Error checking processes: {e}")
        return False

def run_command(cmd):
    """Run the specified command and return the process object."""
    return subprocess.Popen(cmd)

def main():
    proc = None
    while True:
        if proc is None or proc.poll() is not None:
            if proc:
                print("Restarting the bot...")
            else:
                print("Starting the bot...")
            proc = run_command(command)
        else:
            print("Bot is running...")
        
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
