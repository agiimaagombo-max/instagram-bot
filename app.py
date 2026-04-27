import os
from flask import Flask, request, jsonify
import anthropic
import requests

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mytoken123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

SYSTEM_PROMPT = """Та 365.onlineshop онлайн дэлгүүрийн AI туслах байна. Монгол хэлээр эелдэг, товч хариулна.

Захиалгат бараа 7-12 хоногт ирнэ. Бэлэн бараа 24 цагт хүргэгдэнэ.
Үнэ, размер постон дээр байгаа. Байхгүй бол www.365online.store сайтаас харна.
Захиалга DM эсвэл вэбсайтаар 24/7 авдаг.
Хаан банк: MN040005005727168509
DM захиалгад гүйлгээний утганд Instagram нэр, утасны дугаар бичнэ.
Вэбсайт захиалгад захиалгын дугаар бичнэ."""

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_claude_reply(user_message):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
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
