from google.oauth2 import service_account
from googleapiclient.discovery import build
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import lru_cache
import ssl
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from concurrent.futures import ThreadPoolExecutor

import threading
from googleapiclient.errors import HttpError
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session management
code=''
# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = r'credentials.json'  # Update with your credentials file path
SPREADSHEET_IDS = [
    '1bMPX6__XdMAoOmLnYmm_w6WEVzwHwJvp41x5LHAHXSU',
    '18GrkPPDHhZyO6fZwiQc5eyB8w143VfkbnE4Unz0iHac',
    '14miLnyhIY_jj0adrsoiyMlWgYGc-2RUiLcCAsF-uw_w',
    '1H1gWtumtFd0ZAIVUp5VHSAsB0IucJC2ZWEhVBcTDK_A',
    '1mTYYxbYTvsMHOqNHnmsrL4HlI0lb16pOnpByJemXmc0',
    '18kwGBE1yKrrAoqx_DhH2lBtN2afLam9SNwdwZ-AHz3c',
    '1YhDYOy5lmWQVOY2czT8Az9l8GiplK8chyUylFuF1DvU',
    '19m2Nttr7GI8nia6HKKirmVgHPIMjhBAuuLLFDDfud_U',
    '1ClTx398ooAK41_G1sUvPsqmgCH2C1bBaN_HCzHU9Kqo',
    '1pC-DQ5MayogML7QuLbSUG3LILg691O_vsonAf-miM6o',
    '1tuoVLZyu0CnBiM-anQuy_M-lcDbqkOFQ4aFyCotqqmM',
    '1dteeH-VQtUpeyF3eJbI4R2ReAKTTbvNjTbVKLr2MDNs',
    '1bunJxzNu27EdmA-0iPGmCy7NEhL8BRt0g86Ca5MRLJE',
    '1Vk11oeIa2YdabO7CCrUlI_VqXvgKtp8HP-ZFkgBHMak',
    '1j_gfQegjX4QqgtKPsYJBqSq1FExQ3KMg7zORaDdjoko',
    '1q_zb8QvA2SndJ0Vm7DK8Hia50I5LUPKh6JUorPKe048',
    '19LwBeLQqeOEFB3hDVUVDHbYOgnfNH5wxzIZmrwsT9QQ',
    '1vgpvKoV61MYF39onsHXGanjrml8AKt5Ntc_CisEmGAs',
    '13i845yj4fsOJWklm3Idf-iBAmWZjoS5Z1mLnUxpXbEg'
]


credentials_info = [
    ('q1credentials.json', '1bMPX6__XdMAoOmLnYmm_w6WEVzwHwJvp41x5LHAHXSU'),  # Replace with your first sheet ID
    ('q2credentials.json', '18GrkPPDHhZyO6fZwiQc5eyB8w143VfkbnE4Unz0iHac'),
    ('q3credentials.json', '14miLnyhIY_jj0adrsoiyMlWgYGc-2RUiLcCAsF-uw_w'),
    ('q4credentials.json', '1H1gWtumtFd0ZAIVUp5VHSAsB0IucJC2ZWEhVBcTDK_A'),
    ('q5credentials.json', '1mTYYxbYTvsMHOqNHnmsrL4HlI0lb16pOnpByJemXmc0'),
    # Replace with your second sheet ID
]


SHEET_NAME = 'תגובות לטופס 1'  # Update with the range where user codes are stored
google_forms = [
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLScqUlE1vLcDXZmOWARSFTXeZ9XWwsYaUVsNLmAlb1JcVslgng/viewform?entry.2086520226={code}",
            "name": "1. שאלון פרטים אישיים", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLScE5Wa5dkz-GZrhhtQrYpaww8w0mXeULqafFFaHyO5SjXRB7w/viewform?entry.844161581={code}",
            "name": "2. שאלון  אורח חיים ", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSdJa9y9emITN55DXRTwoIg_oB4uePYS7BdhWLJOf7s_BMH6CQ/viewform?entry.85651271={code}",
            "name": "3. שאלון  איכות שינה", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSd01H9P_Uq3qdfF3yL-fO5s4rTwCOD6Zz1LlqSJV9mjQ-klZQ/viewform?entry.1151284239={code}",
            "name": "4. שאלון  היסטוריה רפואית", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSdy_uR5nLBgyFxlXI1s1SysPYgs3tDDx-vx3NO17Uhzp_C58A/viewform?entry.77711748={code}",
            "name": "5. שאלון  הערכת אישיות", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSfM9VF9mytgtnq6900CmGrATdfV9K7qQ1yISEUrhtuoXZzpfA/viewform?entry.1163388527={code}",
            "name": "6. שאלון  תפישת עצמי", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSecxx4R00Ob-rZPfQv-6FxU92dZbh-lD3X7YPwoKGdqG7_Wqg/viewform?entry.2028061639={code}",
            "name": "7. שאלון שאלון פסיכומטרי", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSchqqDa6-s7rvhi8wzlnfEHXm-_5ujXdytZz0tNmkHWEeVjtg/viewform?entry.1622210763={code}",
            "name": "8. שאלון  חרדה", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSeP92lG6jUeL3u76OYZq0uZduJsdvZGIdCs0l-7CpmBOkM1yw/viewform?entry.1091824213={code}",
            "name": "9.  שאלון צאצאים שורדי שואה", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSchwLA2SszrPc6Yv1b20JyKwCfDxbpJlqyyZVZ7QYBeTv-nCg/viewform?entry.1629359923={code}",
            "name": "10.  שאלון ליקויי למידה", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSdgtA3otdIMZwB7mD4nIY1VK8iKm5YTiF7cJQD3dhy7QcQZXQ/viewform?entry.1104486566={code}",
            "name": "11.  שאלון קורונה", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSc702MOobxGW1spmfDOWppTtDywOkTDP5lZNiYU0wSLSZ4ZVw/viewform?entry.1953529110={code}",
            "name": "12.שאלון שימוש בטלפון סלולרי", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSedmJMsSwlVYBbk6zhj1rM3a0gMCu6aXO4ocgLbv-Auut0usQ/viewform?entry.822214287={code}",
            "name": "13. שאלון מוזיקה", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLScqyN8NhtC4aCUjX472ebevNCDNgO13vs71b0zXwJ83LSZpOQ/viewform?entry.1357290256={code}",
            "name": "14.  שאלון תכנות", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSf2NspYl4OqpDZCDwfuroJtd2vEW8otATNJhzidRoh_J7KoDg/viewform?entry.1579214709={code}",
            "name": "15. שאלון טלפון חכם ", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSd-84NMnUPMYTm0rfiY_yIStkHXK6gednUhWC1gqcTR9d8LpA/viewform?entry.16549171={code}",
            "name": "16.שאלון אירועי חיים חלק 1 ", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSciDkQNKHhgN-x7MR9EsY_y7gdgJ5vuiL1ioZfP_WW0PY5khA/viewform?entry.2090123778={code}",
            "name": "17. שאלון אירועי חיים חלקים 2-3", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSdJeNkuXXCX32s8xzlmSOGoNf-MtlnMuHSJTO6GyMXBJgQk5Q/viewform?entry.1367984700={code}",
            "name": "18.שאלות אחרונות", "submitted": False},
        {
            "url": f"https://docs.google.com/forms/d/e/1FAIpQLSf64N1fB29uptgQ0exlNU7F0hEiudRpKoaaMPaeh-kUeWTpbA/viewform?entry.1913852269={code}",
            "name": "19. שאלות סיום", "submitted": False},
]

def get_google_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def fetch_data(key_file, sheet_id):
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_file,SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    return sheet.get_all_records()
def fetch_data_parallel(sheet_ids):
    all_data = {}  # A dictionary to store the data fetched from each sheet
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda x: fetch_data(*x), credentials_info))

    # Loop through each result and associate it with the corresponding sheet_id
    for sheet_id, data in zip(sheet_ids, results):
        all_data[sheet_id] = data

    return all_data


def check_user_code_in_sheet(code, sheet_ids, sheet_name):
    limited_sheet_ids = sheet_ids[:5]
    all_data = fetch_data_parallel(limited_sheet_ids)
    # Iterate over all fetched data and check for the code
    for idx, sheet_id in enumerate(limited_sheet_ids):
            values = all_data.get(sheet_id, [])
            if not values:
                continue
            data_rows = values[1:]
            for row in data_rows:
                if 'קוד הנבדק' in row and row['קוד הנבדק']:  # Check if the key exists and has a value
                    if row['קוד הנבדק'] == code:
                        google_forms[idx]["submitted"] = True
                        break
                    else:
                        google_forms[idx]["submitted"] = False
                elif 'קוד נבדק' in row and row['קוד נבדק']:  # Check for the other key
                    if row['קוד נבדק'] == code:
                        google_forms[idx]["submitted"] = True
                        break
                    else:
                        google_forms[idx]["submitted"] = False


@app.route("/", methods=["GET", "POST"])
def enter_code():
    if request.method == "POST":
        code = request.form.get("code")
        if code:
            # Check if the code exists in the sheets
            subject_link = f"{request.host_url}subject/{code}"
            return render_template("enter_code.html", subject_link=subject_link)

    return render_template("enter_code.html")


@app.route("/subject/<code>", methods=["GET"])
def subject_page(code):
    # Check submission status on every page load
    check_user_code_in_sheet(code, SPREADSHEET_IDS,SHEET_NAME)

    google_form = [
        {"url": form["url"] + f"{code}", "name": form["name"], "submitted": form["submitted"]}
        for form in google_forms
    ]

    return render_template("subject_page.html", code=code, forms=google_form)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001)