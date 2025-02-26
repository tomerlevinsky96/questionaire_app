from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask import Flask, Response, redirect, url_for, session, flash, request, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
import time
import json
import random
import string

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session management

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '1fcFZc2w30xJGAvb_oIaKFbtxgvABWYT9Ttgua4M9_G8'  # Replace with your sheet ID
CREDS_FILE = 'q1credentials.json'

# Shared data структура to store the latest form statuses
form_statuses = {}
credentials_info = [
    ('q1credentials.json', '1bMPX6__XdMAoOmLnYmm_w6WEVzwHwJvp41x5LHAHXSU'),
    ('q2credentials.json', '18GrkPPDHhZyO6fZwiQc5eyB8w143VfkbnE4Unz0iHac'),
    ('q3credentials.json', '14miLnyhIY_jj0adrsoiyMlWgYGc-2RUiLcCAsF-uw_w'),
    ('q4credentials.json', '1H1gWtumtFd0ZAIVUp5VHSAsB0IucJC2ZWEhVBcTDK_A'),
    ('q5credentials.json', '1mTYYxbYTvsMHOqNHnmsrL4HlI0lb16pOnpByJemXmc0'),
    ('q6credentials.json', '18kwGBE1yKrrAoqx_DhH2lBtN2afLam9SNwdwZ-AHz3c'),
    ('q7credentials.json', '1YhDYOy5lmWQVOY2czT8Az9l8GiplK8chyUylFuF1DvU'),
    ('q8credentials.json', '19m2Nttr7GI8nia6HKKirmVgHPIMjhBAuuLLFDDfud_U'),
    ('q9credentials.json', '1ClTx398ooAK41_G1sUvPsqmgCH2C1bBaN_HCzHU9Kqo'),
    ('q10credentials.json', '1pC-DQ5MayogML7QuLbSUG3LILg691O_vsonAf-miM6o'),
    ('q11credentials.json', '1tuoVLZyu0CnBiM-anQuy_M-lcDbqkOFQ4aFyCotqqmM'),
    ('q5credentials.json', '1dteeH-VQtUpeyF3eJbI4R2ReAKTTbvNjTbVKLr2MDNs'),
    ('q11credentials.json', '1bunJxzNu27EdmA-0iPGmCy7NEhL8BRt0g86Ca5MRLJE'),
    ('q13credentials.json', '1Vk11oeIa2YdabO7CCrUlI_VqXvgKtp8HP-ZFkgBHMak'),
    ('q10credentials.json', '1j_gfQegjX4QqgtKPsYJBqSq1FExQ3KMg7zORaDdjoko'),
    ('q9credentials.json', '1q_zb8QvA2SndJ0Vm7DK8Hia50I5LUPKh6JUorPKe048'),
    ('q8credentials.json', '19LwBeLQqeOEFB3hDVUVDHbYOgnfNH5wxzIZmrwsT9QQ'),
    ('q7credentials.json', '1vgpvKoV61MYF39onsHXGanjrml8AKt5Ntc_CisEmGAs'),
    ('q6credentials.json', '13i845yj4fsOJWklm3Idf-iBAmWZjoS5Z1mLnUxpXbEg')
]
def get_google_forms(code):
    return [
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLScqUlE1vLcDXZmOWARSFTXeZ9XWwsYaUVsNLmAlb1JcVslgng/viewform?entry.2086520226={code}", "name": "1. שאלון פרטים אישיים", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLScE5Wa5dkz-GZrhhtQrYpaww8w0mXeULqafFFaHyO5SjXRB7w/viewform?entry.844161581={code}", "name": "2. שאלון אורח חיים ", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSdJa9y9emITN55DXRTwoIg_oB4uePYS7BdhWLJOf7s_BMH6CQ/viewform?entry.85651271={code}", "name": "3. שאלון איכות שינה", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSd01H9P_Uq3qdfF3yL-fO5s4rTwCOD6Zz1LlqSJV9mjQ-klZQ/viewform?entry.1151284239={code}", "name": "4. שאלון היסטוריה רפואית", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSdy_uR5nLBgyFxlXI1s1SysPYgs3tDDx-vx3NO17Uhzp_C58A/viewform?entry.77711748={code}", "name": "5. שאלון הערכת אישיות", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSfM9VF9mytgtnq6900CmGrATdfV9K7qQ1yISEUrhtuoXZzpfA/viewform?entry.1163388527={code}", "name": "6. שאלון תפישת עצמי", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSecxx4R00Ob-rZPfQv-6FxU92dZbh-lD3X7YPwoKGdqG7_Wqg/viewform?entry.2028061639={code}", "name": "7. שאלון שאלון פסיכומטרי", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSchqqDa6-s7rvhi8wzlnfEHXm-_5ujXdytZz0tNmkHWEeVjtg/viewform?entry.1622210763={code}", "name": "8. שאלון חרדה", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSeP92lG6jUeL3u76OYZq0uZduJsdvZGIdCs0l-7CpmBOkM1yw/viewform?entry.1091824213={code}", "name": "9. שאלון צאצאים שורדי שואה", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSchwLA2SszrPc6Yv1b20JyKwCfDxbpJlqyyZVZ7QYBeTv-nCg/viewform?entry.1629359923={code}", "name": "10. שאלון ליקויי למידה", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSdgtA3otdIMZwB7mD4nIY1VK8iKm5YTiF7cJQD3dhy7QcQZXQ/viewform?entry.1104486566={code}", "name": "11. שאלון קורונה", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSc702MOobxGW1spmfDOWppTtDywOkTDP5lZNiYU0wSLSZ4ZVw/viewform?entry.1953529110={code}", "name": "12. שאלון שימוש בטלפון סלולרי", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSedmJMsSwlVYBbk6zhj1rM3a0gMCu6aXO4ocgLbv-Auut0usQ/viewform?entry.822214287={code}", "name": "13. שאלון מוזיקה", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLScqyN8NhtC4aCUjX472ebevNCDNgO13vs71b0zXwJ83LSZpOQ/viewform?entry.1357290256={code}", "name": "14. שאלון תכנות", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSf2NspYl4OqpDZCDwfuroJtd2vEW8otATNJhzidRoh_J7KoDg/viewform?entry.1579214709={code}", "name": "15. שאלון טלפון חכם ", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSd-84NMnUPMYTm0rfiY_yIStkHXK6gednUhWC1gqcTR9d8LpA/viewform?entry.16549171={code}", "name": "16. שאלון אירועי חיים חלק 1 ", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSciDkQNKHhgN-x7MR9EsY_y7gdgJ5vuiL1ioZfP_WW0PY5khA/viewform?entry.2090123778={code}", "name": "17. שאלון אירועי חיים חלקים 2-3", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSdJeNkuXXCX32s8xzlmSOGoNf-MtlnMuHSJTO6GyMXBJgQk5Q/viewform?entry.1367984700={code}", "name": "18. שאלות אחרונות", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSfVZo7l9jar5u5j66AO6A5M-NJ8afih3LfK0m96IzPwej5xGg/viewform?entry.2017466961={code}", "name": "19. שאלון אמפתיה", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSc0wUxyJ5X2aX7vKD1NtaDAXCiJ0ffvqIPdvc1e-LFEOoRF2Q/viewform?entry.809569518={code}", "name": "20. שאלון התמכרויות", "submitted": False},
        {"url": f"https://docs.google.com/forms/d/e/1FAIpQLSf64N1fB29uptgQ0exlNU7F0hEiudRpKoaaMPaeh-kUeWTpbA/viewform?entry.1913852269={code}", "name": "21. שאלות סיום", "submitted": False},
    ]

def fetch_data(creds_file,sheet_id):
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    data = sheet.get("A:B")
    return data

def normalize_code(value):
    try:
        return str(int(value))
    except ValueError:
        return str(value).strip()

def generate_random_code(length=6):
    """Generate a random alphanumeric code."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
def update_form_statuses():
    while True:
        try:
            data = fetch_data('q1credentials.json','1fcFZc2w30xJGAvb_oIaKFbtxgvABWYT9Ttgua4M9_G8')
            for code in form_statuses.keys():
                google_forms = get_google_forms(code)
                normalized_code = normalize_code(code)
                for form in google_forms:
                    form["submitted"] = False
                for row in data:
                    if len(row) >= 2:
                        normalized_col1 = normalize_code(row[0])
                        normalized_col2 = normalize_code(row[1])
                        if normalized_code in (normalized_col1, normalized_col2):
                            google_forms[int(normalized_col1) - 1]["submitted"] = True
                form_statuses[code] = google_forms
            time.sleep(5)  # Check every 5 seconds (adjust as needed)
        except Exception as e:
            print(f"Error updating form statuses: {str(e)}")
            time.sleep(5)  # Wait before retrying on error

# Start background thread
thread = threading.Thread(target=update_form_statuses, daemon=True)
thread.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        password = request.form['password']
        if password == "Bvn1123@":
            session['authenticated'] = True
            return redirect(url_for('enter_code'))
        flash('Incorrect password. Please try again.', 'error')
    return render_template('loginPage.html')

@app.route('/enter-code', methods=['GET', 'POST'])
def enter_code():
    if not session.get('authenticated'):
        return redirect(url_for('index'))

    subject_link = None
    generated_code = None
    PRIMARY_CREDS_FILE, PRIMARY_SHEET_ID = credentials_info[1]  # Check second sheet for codes/passwords

    if request.method == "POST":
        code = request.form.get("code")
        if code:
            try:
                password=''
                data = fetch_data('q2credentials.json', '1BvqRhTVjT89h2jy8ot419lCFmMlre6XfoR749PUg0fE')
                normalized_code = normalize_code(code)
                code_exists = False
                has_password = False

                for row in data:
                    if len(row) >= 1 and normalize_code(row[1]) == normalized_code:
                        code_exists = True
                        if len(row) >= 2 and row[1].strip():
                            has_password = True
                            password =row[0].strip()
                        break

                if code_exists and has_password:
                    subject_link = f"{request.host_url}subject/{normalized_code}"
                    session[f'subject_authenticated_{normalized_code}'] = False
                else:
                    password = generate_random_code()#generated_code
                    data = fetch_data('q2credentials.json', '1BvqRhTVjT89h2jy8ot419lCFmMlre6XfoR749PUg0fE')  # Refresh data to check uniqueness
                    while password in [normalize_code(row[0]) for row in data if len(row) >= 1]:
                        password = generate_random_code()

                    # Write the generated code and a default password to the Google Sheet
                    creds = ServiceAccountCredentials.from_json_keyfile_name(PRIMARY_CREDS_FILE, '1BvqRhTVjT89h2jy8ot419lCFmMlre6XfoR749PUg0fE')
                    client = gspread.authorize(creds)
                    sheet = client.open_by_key('1BvqRhTVjT89h2jy8ot419lCFmMlre6XfoR749PUg0fE').sheet1
                    sheet.append_row([code,password])

                    # Use the generated code for the subject link
                    subject_link = f"{request.host_url}subject/{code}"  # Fixed to use generated_code
                    session[f'subject_authenticated_{code}'] = False

                return render_template("enter_code.html", subject_link=subject_link, generated_code=password)

            except Exception as e:
                print(f"Error processing code or updating Google Sheet: {str(e)}")
                password = generate_random_code()
                # Fallback: still try to write to the sheet even on error
                try:
                    creds = ServiceAccountCredentials.from_json_keyfile_name('q2credentials.json', SCOPES)
                    client = gspread.authorize(creds)
                    sheet = client.open_by_key('1BvqRhTVjT89h2jy8ot419lCFmMlre6XfoR749PUg0fE').sheet1
                    sheet.append_row([password,code])
                except Exception as sheet_error:
                    print(f"Failed to write fallback code to sheet: {str(sheet_error)}")

                subject_link = f"{request.host_url}subject/{code}"
                session[f'subject_authenticated_{code}'] = False
                return render_template("enter_code.html", subject_link=subject_link, generated_code=password)

    return render_template("enter_code.html", subject_link=subject_link, generated_code=generated_code)
@app.route("/subject/<code>/login", methods=["GET", "POST"])
def subject_login(code):
    if request.method == "POST":
        password = request.form.get("subject_password")
        try:
            # Fetch data from the Google Sheet
            data = fetch_data('q2credentials.json', '1BvqRhTVjT89h2jy8ot419lCFmMlre6XfoR749PUg0fE')
            normalized_code = normalize_code(code)
            stored_password = None

            # Find the password for the given code
            for row in data:
                if len(row) >= 1 and normalize_code(row[1]) == normalized_code:
                    if len(row) >= 2 and row[0].strip():
                        stored_password = row[0].strip()
                    break

            # Check if the password matches
            if stored_password and password == stored_password:
                session[f'subject_authenticated_{code}'] = True
                return redirect(url_for('subject_page', code=code))
            else:
                return render_template("subject_login.html", code=code, error="סיסמה שגויה. נסה שוב.")

        except Exception as e:
            print(f"Error fetching password from Google Sheet: {str(e)}")
            return render_template("subject_login.html", code=code, error="שגיאה בטעינת הסיסמה. נסה שוב מאוחר יותר.")

    return render_template("subject_login.html", code=code)

@app.route("/subject/<code>", methods=["GET"])
def subject_page(code):
    if not session.get(f'subject_authenticated_{code}'):
        return redirect(url_for('subject_login', code=code))

    if code not in form_statuses:
        form_statuses[code] = get_google_forms(code)

    session[f'subject_authenticated_{code}'] = False
    return render_template("subject_page.html", code=code)

@app.route("/subject/<code>/events")
def subject_events(code):
    def event_stream():
        while True:
            if code in form_statuses:
                forms = form_statuses[code]
                yield f"data: {json.dumps([{'url': form['url'], 'name': form['name'], 'submitted': form['submitted']} for form in forms])}\n\n"
            time.sleep(1)  # Push updates every second

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, threaded=True)