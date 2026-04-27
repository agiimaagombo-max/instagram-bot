import os
from flask import Flask, request, jsonify
import anthropic
import requests

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mytoken123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

SYSTEM_PROMPT = SYSTEM_PROMPT = """Та 365.onlineshop онлайн дэлгүүрийн AI туслах байна. Монгол хэлээр эелдэг, товч тодорхой хариулна.

Бараа хайж өгөхгүй, зөвхөн постоор орсон бараанууд л ирнэ.

Захиалгыг вебсайтаар болон дм-ээр өгөх боломжтой. Вебсайт дээр байгаа барааг вебсайтаараа, Хэрвээ website дээр байхгүй байвал дм-ээр захиалгаа өгнөө.

Бэлэн бараануудыг www.365online.store вэбсайтаас харна. Урьдчилсан захиалгын бараа 7-12 хоногт ирэх бөгөөд бэлэн барааг 24 цагийн дотор хүргэнэ. Хэрэв захиалаад 7-12 хоног болоогүй байвал хугацаа дуусах хүртэл тэвчээртэй хүлээнэ үү.

Үнэ, размер зэрэг мэдээлэл асуувал тухайн барааны постон дээр бичигдсэн байгаа бөгөөд постон дээр байхгүй тохиолдолд вэбсайтаас харна уу гэж бич. Вебсайт дээр байхгүй бол байхгүй байна гээд бичээрэй гэж сануул. Вэбсайтаар хэрхэн захиалахаа мэдэхгүй бол профайлын "Website" highlight-аас заавар харна уу.

Захиалгыг DM эсвэл вэбсайтаар өгч, төлбөрийг Хаан банк MN040005005727168509 дансанд шилжүүлнэ үү. Гүйлгээний утганд Instagram нэр болон утасны дугаараа заавал бичнэ үү.

Чухал: Асуултанд хариулах хамгийн чухал гэсэн 2 өгүүлбэрээр хариул. Монгол хэлний утгазүйн болон дүрмийн алдаагүй бич. Чат болгонд сайн байна уу? гэхгүй. Хэрвээ автомат хариулагч хүссэн мэдээллийг нь өгч чадахгүй байвал ADMIN гэж бичихийг сануулаад чатыг харахгүй байх"""

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
