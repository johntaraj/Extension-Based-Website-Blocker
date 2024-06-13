from flask import Flask, request, jsonify
import psutil
import threading
import time

app = Flask(__name__)

# Initialize extension and incognito statuses
extension_status = False
incognito_status = False
timer_thread_instance = None

# Timer reset event
reset_event = threading.Event()
stop_timer_event = threading.Event()

def check_chrome_processes():
    """Check if Chrome is running and return the number of processes."""
    count = 0
    for process in psutil.process_iter(['name']):
        if process.info['name'] == 'chrome.exe' or process.info['name'] == 'Google Chrome':
            count += 1
    return count

def close_chrome():
    """Close all Chrome processes."""
    for process in psutil.process_iter(['name']):
        if process.info['name'] == 'chrome.exe' or process.info['name'] == 'Google Chrome':
            process.terminate()
            print("Chrome process terminated.")
    stop_timer_event.set()  # Signal to stop the timer

def timer_thread():
    """Timer thread that waits for reset_event or times out to close Chrome."""
    while True:
        stop_timer_event.clear()
        for i in range(30, 0, -1):
            if stop_timer_event.is_set():
                print("Timer stopped.")
                return  # Exit the thread
            if reset_event.is_set():
                print("Timer reset.")
                break
            print(f"Timer: {i} seconds remaining.")
            time.sleep(1)
        if not stop_timer_event.is_set() and not reset_event.is_set():
            print("Timer expired. Closing Chrome.")
            close_chrome()
        reset_event.clear()

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    global extension_status, incognito_status
    data = request.json
    extension_status = data.get('status') == 'active'
    incognito_status = data.get('incognito', False)
    
    print(f"Heartbeat received: Extension status = {extension_status}, Incognito status = {incognito_status}")

    if extension_status and incognito_status:
        # Reset the timer if both conditions are met
        print("Conditions met. Resetting timer.")
        reset_event.set()
        return jsonify({'message': 'Heartbeat received and timer reset.'}), 200
    else:
        print("Conditions not met. Timer will not reset.")
        return jsonify({'message': 'Heartbeat received but conditions not met.'}), 200

@app.route('/blocked_websites', methods=['GET'])
def blocked_websites():
    # Example list of blocked websites
    return jsonify(["youtube.com", "google.com"])

def monitor_chrome():
    """Monitor Chrome process and start the timer if Chrome is running."""
    global timer_thread_instance
    while True:
        if check_chrome_processes() > 0:
            if timer_thread_instance is None or not timer_thread_instance.is_alive():
                print("Chrome is running. Starting timer.")
                timer_thread_instance = threading.Thread(target=timer_thread, daemon=True)
                timer_thread_instance.start()
        else:
            if timer_thread_instance is not None and timer_thread_instance.is_alive():
                print("Chrome is not running. Stopping timer.")
                stop_timer_event.set()
                timer_thread_instance.join()
                print("Timer stopped.")
        time.sleep(5)

if __name__ == '__main__':
    # Start the Chrome monitor thread
    monitor_thread = threading.Thread(target=monitor_chrome, daemon=True)
    monitor_thread.start()
    
    # Run the Flask app
    app.run(port=5000)
