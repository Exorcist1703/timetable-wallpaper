import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

DATE = "X"
GROUP = "БИК2506"

# -------------------------
# Получаем расписание
# -------------------------

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://mtuci.ru/time-table/"
}

session.get("https://mtuci.ru/time-table/", headers=headers)

url = "https://mtuci.ru/bitrix/services/main/ajax.php"

params = {
    "c": "mtuci:timetable",
    "action": "getTimetableByValue",
    "mode": "class"
}

if DATE == "X":
    today = datetime.now().strftime("%d.%m.%Y")
else:
    today = DATE

data = {
    "VALUE": GROUP,
    "MONTH": "1",
    "TYPE": "group",
    "SITE_ID": "s3"
}

response = session.post(url, params=params, data=data, headers=headers)
# result_json = response.json()
print("STATUS:", response.status_code)
print("TEXT:")
print(response.text)
exit()

schedule = result_json.get("data", {}).get("days", {})
lessons = schedule.get(today)

blocks = []

if not lessons:
    block = f"""
В этот день пар нет.

"""

    blocks.append(block)

if isinstance(lessons, list):
    for lesson in lessons:
        discipline = lesson.get("UF_DISCIPLINE", "")
        start = lesson.get("UF_TIME_START", "")
        end = lesson.get("UF_TIME_END", "")
        teachers = ", ".join(lesson.get("UF_TEACHER", []))
        audience = ", ".join(lesson.get("UF_AUDIENCE", []))
        lesson_type = lesson.get("UF_TYPE", "")

        block = f"""{start} - {end}
{discipline}
{teachers}
{audience}, {lesson_type}"""

        blocks.append(block)

# -------------------------
# Формируем карточки
# -------------------------

cards_html = ""

for block in blocks:
    cards_html += f"""
        <div class="card">
            <div class="text">{block}</div>
        </div>
    """

# -------------------------
# ТВОЙ CSS (встроенный)
# -------------------------
import base64

# читаем шрифт
with open("Eitai.otf", "rb") as f:
    font_base64 = base64.b64encode(f.read()).decode("utf-8")
    
css = f"""
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    background: transparent;
}}

@font-face {{
    font-family: 'MyFont';
    src: url(data:font/otf;base64,{font_base64}) format('opentype');
}}

.canvas {{
    width: 1179px;
    height: 2556px;
    margin: 0 auto;
    display: flex;
    justify-content: center;
    color: rgb(255, 255, 255);
    background-color: #171923;
}}

.panel {{
    position: absolute;
    margin-top: 650px;
    margin-left: 40px;
    margin-right: 40px;
    width: 1125px;
    padding: 20px 20px;
    border-radius: 70px;
    background: #2A2C3A;
    display: flex;
    flex-direction: column;
    gap: 30px;
    border: 20px solid #212330;
}}

.card {{
    background: #36394A;
    border-radius: 30px;
    padding: 15px 10px;
}}

.text {{
    padding: 0px 20px;
    font-size: 30px;
    line-height: 45px;
    white-space: pre-line;
    font-family: 'MyFont';
}}
"""

# -------------------------
# Финальный HTML
# -------------------------

html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
{css}
</style>
</head>
<body>

<div class="canvas">
    <div class="panel">
        {cards_html}
    </div>
</div>

</body>
</html>
"""

# -------------------------
# Рендер через Playwright
# -------------------------

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1179, "height": 2556})

    page.set_content(html)

    # Ждём загрузку всех ресурсов
    page.wait_for_load_state("networkidle")

    # Дополнительная пауза для загрузки шрифта
    page.wait_for_timeout(1500)

    page.screenshot(path="schedule.png", full_page=True)

    browser.close()

print("schedule.png")

