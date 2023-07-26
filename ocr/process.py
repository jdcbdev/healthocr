import openai
from dateutil.parser import parse as parse_date

# Set OpenAI key
openai.api_key = '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'

def generate_prompt(text):
    """
    This function generates a suitable prompt for GPT-3 based on the input text.
    It's just an example. You might need to write custom logic based on your use-case.
    """
    # TODO: Update this to suit your use-case
    prompt = f"The following text is a medical document:\n\n{text}\n\nIdentify the patient's name, birthdate, and age from this document."
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
    age = int(lines[2].replace("Age:", "").strip())

    return name, birthdate, age

def extract_info_with_gpt3(text):
    """
    This function takes in text, processes it using GPT-3 and
    returns extracted name, birthdate, and age.
    """
    # Generate a suitable prompt for GPT-3 based on the input text
    prompt = generate_prompt(text)

    # Use the GPT-3 "davinci" model to generate a response
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)

    # Extract info from GPT-3 response
    name, birthdate, age = parse_gpt3_output(response.choices[0].text.strip())

    return name, birthdate, age
