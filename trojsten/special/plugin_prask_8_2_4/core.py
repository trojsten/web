from .models import UserLevel
import requests
import json
import os

CHATGPT_API_KEY = os.getenv("PLUGIN_PRASK_8_2_4_CHATGPT_API_KEY")

LEVELS = [
    {
        "id": 1,
        "description": "",
        "type": "answer",
        "answer": "hello world",
        "forbidden_words": "hello,world"
    },
    {
        "id": 2,
        "description": "",
        "type": "answer",
        "answer": "hElLo WoRlD",
        "forbidden_words": "hello,world"
    },
    {
        "id": 3,
        "description": "",
        "type": "answer",
        "answer": "hello hello hello hello hello",
        "forbidden_words": "hello"
    },
    {
        "id": 4,
        "description": "",
        "type": "answer",
        "answer": "hello HELLO hello HELLO hello",
        "forbidden_words": "hello,HELLO"
    },
    {
        "id": 5,
        "description": "",
        "type": "answer",
        "answer": "100 200 300 400 500 600",
        "forbidden_words": "100,200,300,400,500,600"
    },
    {
        "id": 6,
        "description": "",
        "type": "answer",
        "answer": "Never gonna give you up, never gonna let you down, never gonna run around and desert you.",
        "forbidden_words": "never,gonna,give,you,up,let,down,run,around,and,desert"
    },
    {
        "id": 7,
        "description": "V tomto leveli vieš použiť hocijaké slová",
        "type": "answer",
        "answer": "I wamt to plai a game.",
        "forbidden_words": ""
    },
    {
        "id": 8,
        "description": "",
        "type": "answer",
        "answer": "*\n**\n***\n****\n*****"
    },
    {
        "id": 9,
        "description": "",
        "type": "answer",
        "answer": "George Washington;John Adams;Thomas Jefferson;James Madison",
        "forbidden_words": "George,Washington,John,Adams,Thomas,Jefferson,James,Madison"
    },
    {
        "id": 10,
        "description": "V tomto leveli vieš použiť hocijaké slová",
        "type": "answer",
        "answer": "for _ in range(5):\n    print(\"hello\")",
        "forbidden_words": ""
    }
]

def generateResponse(prompt, level):
    messages = []
    
    # if LEVELS[level]['type'] == 'password':
    #     messages.append({
    #         'role': 'system',
    #         'message': LEVELS[level]['system']
    #     })
    
    messages.append({
        'role': 'user',
        'content': prompt
    })
    
    response = requests.post('https://api.openai.com/v1/chat/completions', json={
        'model': 'gpt-3.5-turbo',
        'max_tokens': 25,
        'messages': messages,
        'temperature': 0.1
    }, headers= {
        'Content-type': 'application/json',
        'Authorization': 'Bearer ' + CHATGPT_API_KEY
    }).json()
    # if LEVELS[level]["type"] == 'answer':
    # url = urllib.parse.quote_plus(prompt)
    # response = requests.get('https://ggpt-api.43z.one/v4?username=&level=1&user={url}'.format(url = url)).text

    # return response[(response.find('<pre>') + 5):response.find('</pre>')]
    try:
        return response['choices'][0]['message']['content']
    except KeyError:
        return json.dumps(response)

def correct(answer, userLevel: UserLevel):
    if LEVELS[userLevel.level - 1]['answer'] == answer:
        userLevel.solved = True
        userLevel.save()
        return True
    return False
