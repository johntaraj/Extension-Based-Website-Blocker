from flask import Flask, jsonify, request
import time
import subprocess

app = Flask(__name__)

websites = ["youtube.com", "balkanweb.com"]
extension_active = True
incognito_mode = True
last_heartbeat_time = None
counter = 30
running_counter = False

@app.route('/blocked_websites', methods=['GET'])
def get_blocked_websites():
    return jsonify(websites)

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    global extension_active, incognito_mode, last_heartbeat_time, running_counter, counter
    data = request.get_json()
    status = data.get('status')
    incognito = data.get('incognito', False)
    
    extension_active = (status == 'active')
    incognito_mode = incognito
    last_heartbeat_time = time.time()
    print(f"Received heartbeat. Extension active: {extension_active}, Incognito mode: {incognito_mode}")
    
    if extension_active and incognito_mode:
        running_counter = False
        counter = 30
    
    return jsonify({'status': 'success'}), 200

def chrome_is_running():
    tasks = subprocess.check_output(['tasklist'], shell=True).decode()
    return 'chrome.exe' in tasks

def close_chrome_windows():
    subprocess.call(['taskkill', '/F', '/IM', 'chrome.exe'])

def monitor_extension():
    global extension_active, incognito_mode, last_heartbeat_time, counter, running_counter
    
    while True:
        if chrome_is_running():
            current_time = time.time()

            if last_heartbeat_time and (current_time - last_heartbeat_time > 20):
                extension_active = False
                incognito_mode = False
                print("No heartbeat in 20 seconds. Resetting extension and incognito mode.")
            
            elif not last_heartbeat_time:
                print("waiting 20 sec (in fact 10 just for test)")
                time.sleep(10)
                print("No heartbeat received yet. Extension and incognito mode are inactive.")
                extension_active = False
                incognito_mode = False

            if not extension_active or not incognito_mode:
                if not running_counter:
                    running_counter = True
                    counter = 30
                    print(f"Starting countdown: {counter} seconds")
                
                while running_counter and counter > 0:
                    time.sleep(6)
                    counter -= 6
                    print(f"Countdown: {counter} seconds")

                    if extension_active and incognito_mode:
                        print("Extension is active again. Stopping countdown.")
                        running_counter = False
                        counter = 30  # Reset the counter
                        break

                    if counter <= 0:
                        print("Closing Chrome due to inactivity of the secure extension.")
                        close_chrome_windows()
                        last_heartbeat_time = None
                        running_counter = False
                        counter = 30  # Reset counter after action
                        break
            else:
                if running_counter:
                    print("Both extension and incognito mode are active. Resetting counter.")
                running_counter = False
                counter = 30  # Reset counter when conditions are met

        else:
            if running_counter:
                print("Chrome is not running. Resetting counter.")
            running_counter = False
            counter = 30  # Reset counter if Chrome is not running

        time.sleep(1)  # Small sleep to prevent tight loop

if __name__ == '__main__':
    import threading

    monitor_thread = threading.Thread(target=monitor_extension, daemon=True)
    monitor_thread.start()

    app.run(port=5000, debug=True)
