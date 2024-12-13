from openai import OpenAI
import time
from pygame import mixer
import os
import base64
from datetime import datetime 


#https://platform.openai.com/playground/assistants

api_key = os.getenv("JARVISAI_OPENAI_KEY")
client = OpenAI(api_key = api_key,
                default_headers={"OpenAI-Beta": "assistants=v2"})
mixer.init()

assistant_id = "asst_V3267AfQigL9SEsWJQ4zdHmN"
thread_id = "thread_HChX8Kr7v3PKq1KpiPYh3ccy"

# Retrieve the assistant and thread
assistant = client.beta.assistants.retrieve(assistant_id)
thread = client.beta.threads.retrieve(thread_id)


session_uploaded_images = []

def shutdown_cleanup():
    ask_question_memory("I am now leaving our conversation, we'll talk later!")
    TTS("Initiating Shutdown Sequence, clearing cache")
    delete_all_uploaded_images()

def delete_all_uploaded_images():
    for image in session_uploaded_images:
        client.files.delete(image)

def upload_image(image_path, purpose, user_text):
    if purpose.lower() == "screenshot": 
        upload_text = ("This is a screenshot of my screen given to you because you used the command #screenshot. You have permision to use this screenshot as you need. You have the ability to analyse the image. Use this image to answer this question from me-  " + user_text + " ")
    elif purpose.lower() == "camera":
        upload_text = ("Here's a photo from my webcam - use it to answer this - " + user_text)
    elif purpose.lower() == "genral":
        upload_text = "this in an image the user has uploaded to you"
        
    # Upload the image file
    with open(image_path, "rb") as image_file:
        file_response = client.files.create(file=image_file, purpose="vision")
    file_id = file_response.id

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": upload_text,
            },
            {
            "type": "image_url",
            "image_url": {
                "url":  f"data:image/jpeg;base64,{base64_image}"
            },
            },
        ],
        }
    ],
    )    
    
    session_uploaded_images.append(file_id)
    
    actual_response_message = response.choices[0].message.content
    
    return actual_response_message

def ask_question_memory(question):
    global thread
    client.beta.threads.messages.create(thread.id, role="user", content=question)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)
    
    while (run_status := client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)).status != 'completed':
        if run_status.status == 'failed':
            return "The run failed."
        time.sleep(1)
    
    
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

def generate_tts(sentence, speech_file_path):
    response = client.audio.speech.create(model="tts-1", voice="echo", input = sentence, speed = 1.4)
    response.stream_to_file(speech_file_path)
    return str(speech_file_path)

def play_sound(file_path):
    mixer.music.load(file_path)
    mixer.music.play()

def TTS(text):
    speech_file_path = generate_tts(text, "speech.mp3")
    play_sound(speech_file_path)
    while mixer.music.get_busy():
        time.sleep(1)
    mixer.music.unload()
    os.remove(speech_file_path)
    return "done"

def check_if_asked_question():
    text =  (client.beta.threads.messages.list(thread_id=thread.id)).data[0].content[0].text.value
    if "?" in text:
        return True
    else:
        return False
