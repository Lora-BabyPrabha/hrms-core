import os
import time
import sys

def run_escalation():
    while True:
        print("Running escalate_tickets command...")
        command = f'"{sys.executable}" manage.py escalate_tickets'  # <== wrap in quotes
        os.system(command)
        time.sleep(60)  # Wait 60 seconds

if __name__ == "__main__":
    try:
        run_escalation()
    except KeyboardInterrupt:
        print("Stopped manual escalation loop.")
