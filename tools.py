import python_weather
import asyncio
import assist
from icrawler.builtin import GoogleImageCrawler
import os
import spot
import cv2
import time
from googlesearch import search
from datetime import datetime 
import pyautogui
from PIL import Image
from pynput.keyboard import Key,Controller

def volumeUp(keyboard):
    for i in range(8):
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        time.sleep(0.06)

def volumeDown(keyboard):
    for i in range(8):
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)
        time.sleep(0.06)

def remove_delimited_text(input_text):
    result = []  
    current_pos = 0  
    
    while True:
        start = input_text.find("{{{", current_pos)
        
        if start == -1:  
            result.append(input_text[current_pos:])
            break
        
        result.append(input_text[current_pos:start])
        
        end = input_text.find("}}}", start)
        
        if end == -1:  #
            print(f"Warning: Unclosed delimiter at position {start}")
            result.append(input_text[start:])
            break
        
        current_pos = end + 3
    
    return ''.join(result)

def extract_delimited_text(input_text):
    current_pos = 0
    extracted_texts = []
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    files = os.listdir("saved_text")
    number_of_files = len(files)
    
    output_file = os.path.join("saved_text", ("saved_text_file_" + str(number_of_files + 1) + "_" + str(timestamp) )) 
    
    while True:
        # Find the opening delimiter
        start = input_text.find("{{{", current_pos)
        if start == -1:  # No more opening delimiters found
            break
            
        # Find the closing delimiter
        end = input_text.find("}}}", start + 3)
        if end == -1:  # No matching closing delimiter
            print(f"Warning: Found unopened tripple curly bracks at position {start}")
            break
            
        # Extract the text between delimiters
        extracted_text = input_text[start + 3:end]
        extracted_texts.append(extracted_text)
        
        # Move position to after the closing delimiter
        current_pos = end + 3
    
    # If we found any delimited text, save it to file
    if extracted_texts:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                # Join extracted texts with newlines between them
                f.write("\n".join(extracted_texts))
            assist.TTS("File successfully saved")
            return True
        except IOError as e:
            print(f"Error writing to file: {e}")
            return False
    else:
        print("No delimited text found in the input")
        return False

def take_screenshot():
    # Save the screenshot directly to the "screenshots" folder
    screenshot_path = "screenshots/screenshot.png"
    compressed_path = "screenshots/screenshot_compressed.jpg"
    
    # Take the screenshot and save it
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)

    # Resize the screenshot to lower resolution
    width, height = screenshot.size
    new_width, new_height = width // 2, height // 2  # Reduce by 50%
    screenshot = screenshot.resize((new_width, new_height))

    print(f"Screenshot saved at: {screenshot_path}")
    
    img = Image.open(screenshot_path)
    img = img.convert("RGB")  # Convert to RGB for JPEG compatibility
    img.save(compressed_path, "JPEG", quality=70)  # Adjust quality (1-100)
    
    print(f"Screenshot saved and compressed at: {compressed_path}")
    
    
    return screenshot_path

def perform_web_search(query, num_results=3):
    try:
        results = list(search(query, num_results=num_results, advanced=True))
        return [{'title': r.title, 'description': r.description, 'url': r.url} for r in results]
    except Exception as e:
        print(f"Error performing web search: {e}")
        return []

def doGoogleSearch(searchQuery):
    print(f"Performing web search for: {searchQuery}")
    assist.TTS(f"Performing web search for: {searchQuery}")
    searchResults = perform_web_search(query = searchQuery)
    if searchResults:
        search_info = "\n".join([f"Title: {r['title']}\nDescription: {r['description']}" for r in searchResults])
    searchAIinput = (f"Here are the search results for '{searchQuery}':\n\n{search_info}\n\nPlease provide a response based on this information. Do not refference the results or links to them. Just explain them")
    return searchAIinput

def resize_with_aspect_ratio(img, width=None, height=None):
    h, w = img.shape[:2]
    if width is None and height is None:
        return img
    if width is None:
        scale = height / h
        width = int(w * scale)
    else:
        scale = width / w
        height = int(h * scale)
    return cv2.resize(img, (width, height))

async def get_weather(city_name):
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        weather = await client.get(city_name)
        return weather

def imageSearch(query):
    GoogleCrawler = GoogleImageCrawler(storage = {"root_dir": r"./images"})
    GoogleCrawler.crawl(keyword = query, max_num = 1)
    
    time.sleep(4)
    
    img = cv2.imread("images/000001.jpg", 0)
    try:
        img_resized = resize_with_aspect_ratio(img, height = 800)
        cv2.imshow("Image search result ", img_resized)
        cv2.waitKey(5000)
        cv2.destroyAllWindows()
    except:
        assist.TTS("Apologies Sir, I could not find a suitable picture for you.")
  
def parse_command(command, user_text, response):
    if "weather" in command:
        weatherDescription = asyncio.run(get_weather("Wakefield"))
        query = "Weather information: " + str(weatherDescription)
        response = assist.ask_question_memory(query)
        print(response)
        assist.TTS(response)
        return response
    
    elif "imagesearch" in command.lower():
        files = os.listdir("./images")
        [os.remove(os.path.join("./images", f))for f in files]
        query = command.split("-")[1]
        imageSearch(query)
    
    elif "googlesearch" in command.lower():
        searchQuery = command.split("-")[1]
        AISearchAssistedPrompt = doGoogleSearch(searchQuery)
        response = assist.ask_question_memory(AISearchAssistedPrompt)
        print(response)
        assist.TTS(response)
        return response
    
    elif "screenshot" in command.lower():
        screenshot_file = take_screenshot()
        assist.TTS("analysing your screen")
        image_response = assist.upload_image(screenshot_file, "screenshot", user_text)
        print(image_response)
        assist.TTS(image_response)
    
    elif "saveimage" in command.lower():
        extensions = ['.png', '.jpg', '.jpeg', '.webp']
        
        files = os.listdir("saved_images")
        number_of_files = len(files)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        save_name = "saved_image" + str(number_of_files + 1) + "_" + str(timestamp)
        
        for ext in extensions:
            try:
                full_path = "images/000001" + ext 
                img_to_save = Image.open(full_path)
                img_to_save.save("saved_images/" + save_name + ext)
            except (FileNotFoundError, Image.UnidentifiedImageError):
                continue
        
        if img_to_save is None:
            print("Can't find image to save")
            assist.TTS("Apologies Sir, I could not find an image in cache to save.")
        else:
            print("Image saved to " + "saved_images/" + save_name + ext)
            assist.TTS("Certainly Sir, I have saved that image for you.")
    
    elif "savetext" in command.lower():
        extract_delimited_text(response)
        






    ######### spotify commands ##########
    if ("play" in command) and ("music" in command):
        spot.start_music()
        print("resuming music playback")
        assist.TTS("resuming music playback")
    
    if (("music" in command) and ("stop" in command)) or (("music" in command) and ("pause" in command)):
        spot.stop_music()
        print("pausing music playback")
        assist.TTS("pausing music playback")
    
    if (("next" in command) and ("music" in command)) or (("skip" in command) and ("music" in command)):
        spot.skip_to_next()
        print("skipping song")
        assist.TTS("skipping song")
        
    if (("previous" in command) and ("music" in command)) or (("rewind" in command) and ("music"in command)):
        spot.skip_to_previous()
        print("previous song")
        assist.TTS("rewinding it")
    
    if (("info" in command) and ("music" in command)):
        spotify_info = spot.get_current_playing_info()
        query = "Music information: " + str(spotify_info)
        response = assist.ask_question_memory(query)
        print(response)
        assist.TTS(response)
        return response
    
    
