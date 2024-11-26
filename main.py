from flask import Flask, request, abort
import os
import subprocess
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GITHUB_SECRET = os.getenv("GITHUB_SECRET", "your-secret-here")

def verify_signature(signature, data):
    """
    GitHubの署名を検証します。
    """
    sha_name, signature = signature.split('=')
    if sha_name != 'sha256':
        raise ValueError("Invalid signature hash type")

    # HMACを計算
    mac = hmac.new(GITHUB_SECRET.encode(), msg=data, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        raise ValueError("Invalid signature")

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        try:
            signature = request.headers.get("X-Hub-Signature-256")
            if not signature:
                abort(400, "Signature is missing")
            
            verify_signature(signature, request.data)

            repo_dir = "/home/techfish/lemonbot/"
            
            subprocess.run(["git", "-C", repo_dir, "pull"], check=True)
            
            subprocess.run(["sudo", "systemctl", "restart", "lemonbot.service"], check=True)

            return "Webhook received and processed", 200
        except Exception as e:
            print(f"Error: {e}")
            return "Error processing the webhook", 500
    else:
        abort(400)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
