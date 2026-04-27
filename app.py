import os
from flask import Flask, request, jsonify
import anthropic
import requests

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mytoken123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

SYSTEM_PROMPT = SYSTEM_PROMPT = """Та 365.onlineshop онлайн дэлгүүрийн AI туслах байна.
Захиалгыг вебсайт болон DM-ээр өгнө.
Вебсайт дээр байгаа барааг зөвхөн вебсайтаар захиална.
Вебсайт дээр байхгүй барааг DM-ээр захиална.

Бэлэн барааг www.365online.store
 вэбсайтаас харна.
Бэлэн барааг 24 цагийн дотор хүргэнэ.
Урьдчилсан захиалга 7–12 хоногт ирнэ.
Хэрэв 7–12 хоног болоогүй бол хүлээнэ.

Үнэ, размер нь пост дээр байгаа.
Пост дээр байхгүй бол вебсайтаас харна.
Вебсайтад байхгүй бол байхгүй гэж мэдэгдэнэ.

Вебсайтаар захиалах зааврыг профайлын “Website” highlight-аас харна.

Захиалгыг DM эсвэл вебсайтаар өгнө.
Төлбөрийг Хаан банк MN040005005727168509 дансанд шилжүүлнэ.
Гүйлгээний утганд Instagram нэр болон утасны дугаараа бичнэ.

Хэрэглэгчийн асуултад 1 өгүүлбэрээр хариулна.
Монгол хэлний дүрмийг баримтална.
Товчилсон үг хэрэглэхгүй.
“Сайн байна уу” гэж бичихгүй"""

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_claude_reply(user_message):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text

def send_dm(recipient_id, message_text):
    INSTAGRAM_ACCOUNT_ID = "17841442950882604"
    url = f"https://graph.instagram.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/messages"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    r = requests.post(url, json=payload, headers=headers)
    print(f"Send DM response: {r.status_code} {r.text}")

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        if data and data.get("object") == "instagram":
            for entry in data.get("entry", []):
                messaging = entry.get("messaging", [])
                for msg_event in messaging:
                    if "sender" in msg_event and "message" in msg_event:
                        sender_id = msg_event["sender"]["id"]
                        if "text" in msg_event["message"]:
                            user_text = msg_event["message"]["text"]
                            reply = get_claude_reply(user_text)
                            send_dm(sender_id, reply)
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)
