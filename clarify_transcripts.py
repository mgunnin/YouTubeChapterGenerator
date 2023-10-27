import re
import os
import openai
import textwrap
from time import time,sleep


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


openai.api_key = open_file('openaiapikey.txt')


def gpt3_completion(prompt, engine='text-davinci-002', temp=0.7, top_p=1.0, tokens=2000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            #text = re.sub('\s+', ' ', text)
            filename = f'{time()}_gpt3.txt'
            save_file(f'gpt3_logs/{filename}', prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return f"GPT3 error: {oops}"
            print('Error communicating with OpenAI:', oops)
            sleep(1)


if __name__ == '__main__':
    files = os.listdir('transcripts/')
    for file in files:
        if os.path.exists(f'clarified/{file}'):
            print('Skipping:', file)
            continue
        transcript = open_file(f'transcripts/{file}')
        chunks = textwrap.wrap(transcript, 6000)
        output = []
        for chunk in chunks:
            prompt = open_file('prompt_clarify_transcript.txt').replace('<<TRANSCRIPT>>', chunk)
            essay = gpt3_completion(prompt)
            output.append(essay)
        result = '\n\n'.join(output)
        save_file(f'clarified/{file}', result)
        print('\n\n================================================\n\n', result)