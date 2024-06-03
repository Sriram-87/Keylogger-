# Keylogger Project

## Description
This project implements a keylogger that captures keystrokes, captures screenshots, records audio, and sends reports via email. It also includes features like webcam activation, microphone activation, file system monitoring, network sniffing, geolocation tracking, data exfiltration, anomaly detection, phishing email sending, and more.

## Features
- Captures keystrokes
- Captures screenshots at specified intervals
- Records audio at specified intervals
- Sends email reports with captured data
- Activates webcam and captures photos
- Activates microphone and records audio
- Monitors file system events
- Sniffs network traffic
- Tracks geolocation of target IP addresses
- Exfiltrates captured data to a remote server
- Detects anomalies in captured data
- Sends phishing emails with attached keylogger
- Hides files and folders
- Adds itself to startup entries for auto-start

## Usage
1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Modify the `config.json` file with your desired settings.
4. Run the `keylogger.py` script.
5. Check the logs and reports in the specified locations.

## Configuration
Modify the `config.json` file to customize the keylogger settings such as reporting intervals, screenshot intervals, audio intervals, target windows, email sender details, etc.

## Disclaimer
This project is for educational purposes only. Misuse of this software for malicious purposes is illegal and unethical. The author assumes no responsibility for any misuse or damage caused by this software.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
