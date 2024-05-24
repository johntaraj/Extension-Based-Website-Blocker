# Extension-Based-Website-Blocker


# Chrome Extension  Blocker

This project is a Flask-based application that monitors the activity of a Chrome extension and incognito mode. It ensures that the Chrome browser closes if the extension is inactive or incognito mode is disabled for more than a specified time.

## Overview

This application works in conjunction with a Chrome extension. The extension sends periodic heartbeat signals to the Flask server to indicate its status and whether Chrome is in incognito mode. If the Flask server does not receive these signals within a specified time (20 seconds in this case), it triggers a countdown to close the Chrome browser to maintain security.

## Features

- Monitors the status of a Chrome extension and incognito mode.
- Closes Chrome browser if the extension is inactive or incognito mode is disabled for more than 20 seconds.
- Uses Flask to handle HTTP requests from the Chrome extension.
- Runs a monitoring loop to manage the countdown and potential closure of Chrome.

## Prerequisites

- Python 3.x
- Flask
- Chrome browser
- A Chrome extension that sends heartbeat signals to the Flask server.

## Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/johntaraj/Extension-Based-Website-Blocker.git
    ```

2. **Install the required Python packages:**

    ```bash
    pip install Flask
    ```

3. **Run the Flask server:**

    ```bash
    python firewall_blocker.py
    ```

## How It Works

1. The Flask server runs and listens for heartbeat signals from the Chrome extension.
2. The Chrome extension periodically sends a POST request to the `/heartbeat` endpoint with its status and incognito mode status.
3. The Flask server resets the countdown timer upon receiving the heartbeat signal.
4. If the Flask server does not receive a heartbeat signal for more than 20 seconds, it triggers a countdown.
5. If the countdown reaches zero without receiving a new heartbeat signal, the server closes the Chrome browser.


## Chrome Extension

You need a Chrome extension that sends periodic POST requests to the `/heartbeat` endpoint of this Flask server with the status of the extension and incognito mode. 
To use the extension, load the folder extension in chrome as developer mode, enable it, and run firewall_blocker.py

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request.
