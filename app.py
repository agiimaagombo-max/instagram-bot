import os
from flask import Flask, request, jsonify
import anthropic
import requests

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mytoken123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

SYSTEM_PROMPT = """Та монгол онлайн дэлгүүрийн AI туслах байна.
Монгол хэлээр эелдэг, товч хариулна.
Хүргэлт: Улаанбаатар хотод 1-2 хоног.
Буцаалт: 7 хоногийн дотор боломжтой.
Мэдэхгүй зүйлд: Манай менежертэй холбогдоно уу гэж хэл."""

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_claude_reply(user_message):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text

def send_dm(recipient_id, message_text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "access_token": PAGE_ACCESS_TOKEN
    }
    requests.post(url, json=payload)

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            for msg_event in entry.get("messaging", []):
                sender_id = msg_event["sender"]["id"]
                if "message" in msg_event and "text" in msg_event["message"]:
                    user_text = msg_event["message"]["text"]
                    reply = get_claude_reply(user_text)
                    send_dm(sender_id, reply)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)
