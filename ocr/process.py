import openai
from dateutil.parser import parse as parse_date
from celery import shared_task
from healthocr.celery import app
import math
from .models import MedicalRecord
from datetime import datetime
import datetime

# Set OpenAI key
openai.api_key = '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'

def generate_prompt(text):
    prompt = f"The text is a medical document:\n\n{text}\n\n"\
    "Identify the following information from this document:\n"\
    "1. Name\n"\
    "2. D.O.B.\n"\
    "3. Record No.\n"\
    "4. Address\n"\
    "5. Home Phone\n"\
    "6. Mobile Phone\n"\
    "7. Work Phone"
    return prompt

def parse_gpt3_output(gpt3_output):
    lines = gpt3_output.split('\n')

    name = None
    dob = None
    record_no = None
    address = None
    home_phone = ''
    mobile_phone = ''
    work_phone = ''

    for line in lines:
        if "Name:" in line:
            name = line.replace("Name:", "").strip()
        elif "D.O.B.:" in line:
            dob_str = line.replace("D.O.B.:", "").strip()
            dob_str = dob_str.replace("(DD/MM/YYYY)", "").strip()  # Remove date format hint
            try:
                dob = parse_date(dob_str)
            except Exception as e:
                print(f"Could not parse date: {e}")
                dob = None
        elif "Record No.:" in line:
            record_no = line.replace("Record No.:", "").strip()
        elif "Address:" in line:
            address = line.replace("Address:", "").strip()
        elif "Home Phone:" in line:
            home_phone = line.replace("Home Phone:", "").strip()
        elif "Mobile Phone:" in line:
            mobile_phone = line.replace("Mobile Phone:", "").strip()
        elif "Work Phone:" in line:
            work_phone = line.replace("Work Phone:", "").strip()

    # Now we calculate the age based on dob
    if dob:
        today = datetime.date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    return name, dob, age, address, home_phone, mobile_phone, work_phone

@app.task
def extract_info_with_gpt3(text, record_id):
    """
    This function takes in text and a record ID, processes the text using GPT-3 and
    returns extracted name, birthdate, and age.
    """
    # Split text into chunks
    max_tokens_for_text = 4096 - 200  # leaving some space for prompt and completion
    text_length_in_tokens = len(text.split())
    num_chunks = math.ceil(text_length_in_tokens / max_tokens_for_text)
    text_chunks = [' '.join(text.split()[i * max_tokens_for_text:(i + 1) * max_tokens_for_text]) for i in range(num_chunks)]

    # Process each chunk with GPT-3 and extract info
    all_names = []
    all_birthdates = []
    all_ages = []
    all_addresses = []
    all_home_phones = []
    all_mobile_phones = []
    all_work_phones = []

    for text_chunk in text_chunks:
        # Generate a suitable prompt for GPT-3 based on the input text
        messages = [
            {"role": "system", "content": "The text is a medical document."},
            {"role": "user", "content": text_chunk},
            {"role": "assistant", "content": "Identify name, birthdate, age, address, mobile phone, home phone and work phone from this document."},
        ]

        # Use the GPT-3 "davinci" model to generate a response
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=2000)

        # Extract info from GPT-3 response
        name, birthdate, age, address, home_phone, mobile_phone, work_phone = parse_gpt3_output(response['choices'][0]['message']['content'].strip())
        all_names.append(name)
        all_birthdates.append(birthdate)
        all_ages.append(age)
        all_addresses.append(address)
        all_home_phones.append(home_phone)
        all_mobile_phones.append(mobile_phone)
        all_work_phones.append(work_phone)

    # Combine extracted info from all chunks
    name = max(set(all_names), key=all_names.count)
    birthdate = max(set(all_birthdates), key=all_birthdates.count)
    age = max(set(all_ages), key=all_ages.count)
    address = max(set(all_addresses), key=all_addresses.count)
    home_phone = max(set(all_home_phones), key=all_home_phones.count)
    mobile_phone = max(set(all_mobile_phones), key=all_mobile_phones.count)
    work_phone = max(set(all_work_phones), key=all_work_phones.count)

    # Update the MedicalRecord with the extracted data
    record = MedicalRecord.objects.get(id=record_id)
    record.name = name
    record.birthdate = birthdate
    record.age = age
    record.address = address
    record.home_phone = home_phone
    record.work_phone = work_phone
    record.mobile_phone = mobile_phone
    record.save()

    return name, birthdate, age, address, home_phone, mobile_phone, work_phone
