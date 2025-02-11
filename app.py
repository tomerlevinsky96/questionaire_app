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
import threading
from googleapiclient.errors import HttpError
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session management
code=''
# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = r'C:\Users\YanivA21\PycharmProjects\pythonProject58\credentials.json'  # Update with your credentials file path
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


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=30))
@lru_cache(maxsize=1000)
def fetch_sheet_data(sheet, sheet_id, name):
    try:
        print(f"Attempting to fetch data from sheet_id: {sheet_id}, range: {name}")
        result = sheet.values().get(spreadsheetId=sheet_id, range=name).execute()
        print(f"Successfully fetched data from {sheet_id}. Data length: {len(result.get('values', []))}")
        return result.get('values', [])
    except Exception as e:
        print(f"Failed to fetch data from sheet_id: {sheet_id}, range: {name}: {e}")
        raise  # Trigger retry if an exception is raised
    except ssl.SSLError as ssl_error:
        print(f"SSL Error: {ssl_error}")
        # Retry mechanism for SSL error
        print("Retrying after a brief delay...")
        time.sleep(5)
        return fetch_sheet_data(sheet, sheet_id, name)


def fetch_data_parallel(sheet, sheet_ids, sheet_name):
    all_data = {}  # A dictionary to store the data fetched from each sheet
    with ThreadPoolExecutor(max_workers=len(sheet_ids)) as executor:
        future_to_sheet = {
            executor.submit(fetch_sheet_data, sheet, sheet_id, sheet_name): sheet_id for sheet_id in sheet_ids
        }

        # Loop through each future as they complete
        for future in as_completed(future_to_sheet):
            sheet_id = future_to_sheet[future]
            try:
                data = future.result()
                if data:
                    print(
                        f"Data fetched from sheet_id {sheet_id}: {data[:5]}...")  # Print the first 5 rows for debugging
                all_data[sheet_id] = data
            except Exception as e:
                print(f"Error while fetching data for sheet_id {sheet_id}: {e}")

    return all_data


def check_user_code_in_sheet(code, sheet_ids, sheet_name):
        service = get_google_sheets_service()  # Ensure this is returning the correct Google Sheets API service
        sheet = service.spreadsheets()

        print(f"Checking for code: {code}")

        # Fetch data in parallel from all sheets
        while(1):
         try:
          all_data = fetch_data_parallel(sheet, sheet_ids,sheet_name)
          break
         except Exception as e:
            continue
        # Iterate over all fetched data and print all codes from each sheet
        for idx,sheet_id in enumerate(SPREADSHEET_IDS):
           try:
            values = all_data.get(sheet_id, [])
            headers = values[0]
            data_rows = values[1:]
            try:
              code_index = headers.index('קוד הנבדק')
            except Exception as e:
                try:
                    code_index = headers.index('קוד נבדק')
                except Exception as e:
                    continue
            for row in data_rows:
              try:
                if row[code_index] == code:
                   google_forms[idx]["submitted"] = True
                   break
                else:
                   google_forms[idx]["submitted"] = False
              except Exception as e:
                  continue
           except Exception as e:
               continue

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