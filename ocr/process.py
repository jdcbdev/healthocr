import openai
from dateutil.parser import parse as parse_date
from celery import shared_task
from healthocr.celery import app
import math
from .models import MedicalRecord

# Set OpenAI key
openai.api_key = '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'

def generate_prompt(text):
    prompt = f"The text is a medical document:\n\n{text}\n\nIdentify name, birthdate, and age from this document."
    return prompt

def parse_gpt3_output(gpt3_output):
    lines = gpt3_output.split('\n')

    name = None
    birthdate = None
    age = None

    for line in lines:
        if "Name:" in line:
            name = line.replace("Name:", "").strip()
        elif "Birthdate:" in line:
            birthdate_str = line.replace("Birthdate:", "").strip()
            birthdate_str = birthdate_str.replace("(DD/MM/YYYY)", "").strip()  # Remove date format hint
            birthdate = parse_date(birthdate_str)
        elif "Age:" in line:
            age_str = line.replace("Age:", "").strip()
            age = ''.join(filter(str.isdigit, age_str))
            age = int(age) if age else None

    return name, birthdate, age

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
    for text_chunk in text_chunks:
        # Generate a suitable prompt for GPT-3 based on the input text
        messages = [
            {"role": "system", "content": "The text is a medical document."},
            {"role": "user", "content": text_chunk},
            {"role": "assistant", "content": "Identify name, birthdate, and age from this document."},
        ]

        # Use the GPT-3 "davinci" model to generate a response
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=2000)

        # Extract info from GPT-3 response
        name, birthdate, age = parse_gpt3_output(response['choices'][0]['message']['content'].strip())
        all_names.append(name)
        all_birthdates.append(birthdate)
        all_ages.append(age)

    # Combine extracted info from all chunks
    name = max(set(all_names), key=all_names.count)
    birthdate = max(set(all_birthdates), key=all_birthdates.count)
    age = max(set(all_ages), key=all_ages.count)

    # Update the MedicalRecord with the extracted data
    record = MedicalRecord.objects.get(id=record_id)
    record.name = name
    record.birthdate = birthdate
    record.age = age
    record.save()

    return name, birthdate, age
