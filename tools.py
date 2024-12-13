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

def take_screenshot():
    # Save the screenshot directly to the "screenshots" folder
    screenshot_path = "screenshots/screenshot.png"
    
    # Take the screenshot and save it
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    
    print(f"Screenshot saved at: {screenshot_path}")
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
    img = cv2.imread("images/000001.jpg", 0)
    img_resized = resize_with_aspect_ratio(img, height = 800)
    cv2.imshow("Image search result ", img_resized)
    cv2.waitKey(5000)
    cv2.destroyAllWindows()
  
def parse_command(command, user_text):
    if "weather" in command:
        weatherDescription = asyncio.run(get_weather("Wakefield"))
        query = "Weather information: " + str(weatherDescription)
        response = assist.ask_question_memory(query)
        print(response)
        assist.TTS(response)
        return response
    
    if "imagesearch" in command.lower():
        files = os.listdir("./images")
        [os.remove(os.path.join("./images", f))for f in files]
        query = command.split("-")[1]
        imageSearch(query)
    
    if "googlesearch" in command.lower():
        searchQuery = command.split("-")[1]
        AISearchAssistedPrompt = doGoogleSearch(searchQuery)
        response = assist.ask_question_memory(AISearchAssistedPrompt)
        print(response)
        assist.TTS(response)
        return response
    
    if "screenshot" in command.lower():
        screenshot_file = take_screenshot()
        assist.TTS("analysing your screen")
        image_response = assist.upload_image(screenshot_file, "screenshot", user_text)
        print(image_response)
        assist.TTS(image_response)
        
    
    
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
    
    

#search("cat")