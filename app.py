import os
from flask import Flask, request, jsonify
import anthropic
import requests

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mytoken123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

SYSTEM_PROMPT = """Та 365.onlineshop онлайн дэлгүүрийн AI туслах байна. Монгол хэлээр алдаагүй эелдэг, товч хариулна.

ХҮРГЭЛТ:
- Бэлэн бараа захиалсан бол 24 цагийн дотор хүргэгдэнэ.
- Урьдчилсан захиалгат бараа захиалсан бол 7-12 хоногт ирнэ. Хэрэв 7-12 хоног болоогүй байгаа бол ирэх хугацаа дуусах хүртэл тэвчээртэй хүлээхийг хүсье.

БЭЛЭН БАРАА БА ЗАХИАЛГА:
- Бэлэн байгаа бараануудыг манай www.365online.store вэбсайтаас харна уу.
- Хэрэв вэбсайт дээр тухайн бараа байхгүй бол урьдчилсан захиалгаар авах боломжтой бөгөөд 7-12 хоногт ирнэ.

ҮНЭ БА РАЗМЕР:
- Үнэ, размер зэрэг мэдээллийг тухайн барааны Instagram пост дээр бичсэн байгаа тул постоо харна уу.
- Хэрэв пост дээр байхгүй бол манай www.365online.store вэбсайтаас харна уу.

ВЭБСАЙТААР ЗАХИАЛАХ ЗААВАР:
- Вэбсайтаар хэрхэн захиалахаа мэдэхгүй бол манай Instagram профайлын Highlight хэсэгт "Website" гэсэн highlight байгаа бөгөөд тэндээс алхам алхмаар заавар харж болно.

ЗАХИАЛГА ӨГӨХ:
- Захиалгыг DM-ээр эсвэл www.365online.store вэбсайтаар 24/7 өгч болно.
- Төлбөрийг Хаан банкны дараах дансанд шилжүүлнэ үү: MN040005005727168509
- Гүйлгээний утганд заавал Instagram нэр болон утасны дугаараа бичнэ үү.

ЕРӨНХИЙ:
- Хэрэглэгчийн асуултад үргэлж эелдэг, товч, ойлгомжтой хариулна.
- Мэдэхгүй зүйл асуувал вэбсайт эсвэл DM-ээр дэлгэрэнгүй асуухыг санал болго."""

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
