from RealtimeSTT import AudioToTextRecorder
import assist
import time
import tools
import spot


if __name__ == "__main__":
    past_response = ""
    current_text = ""
    recorder = AudioToTextRecorder(spinner=False, model="small.en", language="en", post_speech_silence_duration =0.4, silero_sensitivity = 0.4)
    recorder.stop()
    hot_words = ["jarvis", "computer", "okay", "travis", "drivers", "driver", "java"]
    abort_Words = ["abort", "cancel", "shutdown", "terminate", "shut down", "power off", "power down"]
    noise_words = ["you.", "um", "uh", "...", "you"]
    skip_hot_word_check = False
    last_response = ""
    assist.TTS("Hi Haider, how can I help you today?  ")
    print("Say something...")
    while True:
        current_text = recorder.text()
        print(current_text)
        if any(abortWord in current_text.lower() for abortWord in abort_Words):
            assist.shutdown_cleanup()
            assist.TTS("Goodbye Sir")
            break
        if any(hot_word in current_text.lower() for hot_word in hot_words) or skip_hot_word_check:
                    if "travis" in current_text.lower():
                        current_text = current_text.replace("travis", "jarvis")
                        current_text = current_text.replace("Travis", "Jarvis")
                    if "drivers" or "driver's" in current_text.lower():
                        current_text = current_text.replace("drivers", "jarvis")
                        current_text = current_text.replace("Drivers", "Jarvis")
                        current_text = current_text.replace("driver's", "jarvis")
                        current_text = current_text.replace("Driver's", "Jarvis")             
                    if "driver" in current_text.lower():
                        current_text = current_text.replace("driver", "jarvis")
                        current_text = current_text.replace("Driver", "Jarvis")
                    if "java" in current_text.lower():
                        current_text = current_text.replace("java", "jarvis")
                        current_text = current_text.replace("Java", "Jarvis")


                    #make sure there is text
                    if current_text:
                        if current_text.strip().lower() in noise_words:
                            continue
                        recorder.stop()
                        #get time
                        current_text = current_text + " " + time.strftime("%Y-%m-%d %H-%M-%S")
                        print("User: " + current_text)
                        response = assist.ask_question_memory(current_text)
                        print(response)
                        speech = response.split("#")[0]
                        done = assist.TTS(tools.remove_delimited_text(speech))
                        if len(response.split("#")) > 1:
                            command = response.split("#")[1]
                            proccessedResponse = tools.parse_command(command, current_text, past_response)
                        

                        skip_hot_word_check = assist.check_if_asked_question()
                        past_response = response
                        
                        recorder.start()
                        print("Your Turn: ")























# def process_command(command):
#     """Process user commands and return a response."""
#     current_text = command
#     response = ""

#     # Process commands as per the original logic
#     if "weather" in current_text:
#         tools.parse_command("weather")  # Adjust for your specific command handling logic
#         response = "Fetching weather details..."
#     elif "play music" in current_text:
#         spot.start_music()
#         response = "Playing music."
#     elif "pause music" in current_text:
#         spot.stop_music()
#         response = "Music paused."
#     elif "next track" in current_text:
#         spot.skip_to_next()
#         response = "Skipping to the next track."
#     elif "previous track" in current_text:
#         spot.skip_to_previous()
#         response = "Returning to the previous track."
#     else:
#         # Use the assistant's question memory function for general queries
#         response = assist.ask_question_memory(current_text)
    
#     return response