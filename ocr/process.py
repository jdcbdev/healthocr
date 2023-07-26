import openai
from dateutil.parser import parse as parse_date
from celery import shared_task
from healthocr.celery import app
import math

# Set OpenAI key
openai.api_key = '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'

def generate_prompt(text):
    """
    This function generates a suitable prompt for GPT-3 based on the input text.
    It's just an example. You might need to write custom logic based on your use-case.
    """
    # TODO: Update this to suit your use-case
    prompt = f"The following text is a medical document:\n\n{text}\n\nIdentify the name, birthdate, and age from this document."
    return prompt

def parse_gpt3_output(gpt3_output):
    """
    This function extracts name, birthdate, and age from GPT-3 output.
    It's just an example. You might need to write custom logic based on your use-case.
    """
    # TODO: Update this to suit your use-case
    lines = gpt3_output.split('\n')

    name = lines[0].replace("Name:", "").strip()
    birthdate_str = lines[1].replace("Birthdate:", "").strip()
    birthdate = parse_date(birthdate_str.strip())
    
    age_str = lines[2].replace("Age:", "").strip()

    # Extract numeric part from age_str
    age = ''.join(filter(str.isdigit, age_str))
    age = int(age) if age else None

    return name, birthdate, age

@app.task
def extract_info_with_gpt3(text):
    """
    This function takes in text, processes it using GPT-3 and
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
        prompt = generate_prompt(text_chunk)

        # Use the GPT-3 "davinci" model to generate a response
        response = openai.Completion.create(engine="gpt-4", prompt=prompt, max_tokens=8000)  # adjust max tokens as needed

        # Extract info from GPT-3 response
        name, birthdate, age = parse_gpt3_output(response.choices[0].text.strip())
        all_names.append(name)
        all_birthdates.append(birthdate)
        all_ages.append(age)

    # Combine extracted info from all chunks
    # TODO: Add your own logic to combine the info. Here we're just taking the most common ones.
    name = max(all_names, key=all_names.count)
    birthdate = max(all_birthdates, key=all_birthdates.count)
    age = max(all_ages, key=all_ages.count)

    return name, birthdate, age
