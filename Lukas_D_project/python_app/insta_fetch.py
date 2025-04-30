from instagrapi import Client
from dotenv import load_dotenv
import os

# Load Instagram credentials from .env
load_dotenv()
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")

# Initialize the client
cl = Client()

# Try to load previous session if exists
try:
    cl.load_settings("session.json")
    print("🔁 Loaded previous session.")
except:
    print("⚠️ No previous session found, will create a new one.")

# Login and save session
try:
    cl.login(IG_USERNAME, IG_PASSWORD)
    cl.dump_settings("session.json")
    print(f"✅ Logged in as {IG_USERNAME} and session saved.")
except Exception as e:
    print("❌ Login failed:", e)
    exit()

# 🔍 Fetch target account info
TARGET_USERNAME = "izylemonsqueeze"

try:
    user_id = cl.user_id_from_username(TARGET_USERNAME)
    user_info = cl.user_info(user_id)

    print("\n--- 📊 TARGET ACCOUNT INFO ---")
    print("👤 Username:", user_info.username)
    print("📸 Profile Picture URL:", user_info.profile_pic_url)
    print("👥 Followers:", user_info.follower_count)
    print("➡️ Following:", user_info.following_count)
except Exception as e:
    print("❌ Failed to fetch target info:", e)