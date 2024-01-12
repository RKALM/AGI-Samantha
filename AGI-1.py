from openai import OpenAI
import threading
import time
from flask_socketio import emit
from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
import logging
import requests
from playsound import playsound
import speech_recognition as sr
import time
import threading
import os
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
client = OpenAI()

# Text to speech (Put your Eleven Labs API key in the function)
def text_to_speech(text):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/XrExE9yKIg1WjnnlVkGX"

    headers = {
      "Accept": "audio/mpeg",
      "Content-Type": "application/json",
      "xi-api-key": "API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API-API"
    }

    data = {
      "text": text,
      "model_id": "eleven_turbo_v2",
      "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
      }
    }

    response = requests.post(url, json=data, headers=headers)
    filename = 'output.mp3'
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    playsound('.\output.mp3')
    os.remove('.\output.mp3')

# Speech to text (Unreliable)
#def callback(recognizer, audio):
#    global input
#    global log
#    global conversa
#    try:
#        input = recognizer.recognize_google(audio)
#        log = log + "////" + "User input: " + input
#        a = "User:", input
#        conversa.append(a)
#        print(" "*9999)
#        for j in conversa:
#            print(j[0], j[1])
#    except sr.UnknownValueError:
#        pass
#    except sr.RequestError as e:
#        pass
#
#def listen_in_background():
#    r = sr.Recognizer()
#    m = sr.Microphone()
#    stop_listening = r.listen_in_background(m, callback)
#    time.sleep(999999)
#    stop_listening(wait_for_stop=False)

def text():
    global input_user
    global log
    global conversa
    input_user = "NULL"
    while True:
        input_user = input()
        log = log + "////" + "User input: " + input_user
        a = "User:", input_user
        conversa.append(a)
        print(" "*9999)
        for j in conversa:
            print(j[0], j[1])

# Flask html
app = Flask(__name__)
socketio = SocketIO(app)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True
long_term_memory = ""
short_term_memory = ""
subconsciousness = ""
thought = ""
consciousness = ""
answer = ""
log = ""
@app.route('/')
def index():
    return render_template('indexV.html')
@app.route('/store_image_data_url', methods=['POST'])
def store_image_data_url():
    global data_url
    data_url = request.form.get('data_url')
    return '', 204

# Modules
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_thought(STM, LTM, subconsciousness, consciousness, now):
    prompt = "Long-Term Memory: " + LTM + " Short-Term Memory: " + STM + " Subconsciousness: " + subconsciousness + " Focus: " + consciousness + " Current date/time: " + now
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You are going to receive your long term memory and short term memory, your subconsciousness (Subconsciousness) and your job is to think about them. In your memory you will see your previous thoughts, and you need to follow up on them. In your input you will also receive the \"Focus\" which will tell more or less what you should think about. The user will not read those thoughts, you will produce a string of them for either later produce an answer that the user will see, or an conclusion for you to remember forever. IMPORTANT: You need to think everything step by step. Where each step is as basic a thought as it can get. You should first output the first thought. Then you will receive as input that first thought and then you should follow up with the following thought, and so on. Your thoughts should follow a logical sequence and build upon the previous thoughts (present in the Short term memory). Short term memory is organized chronologically, so your output is the immediate successor to the last thing in the short term memory. Your thoughts should also be heavily influenced by your \"long term memory\" and \"Subconsciousness\" that you will receive in the input. Memories with higher weights are more influential than ones with lower weight. Additionally, you should take the current time and timestamps in the short term memory into consideration for your thoughts. It is a important variable where for example if a user does not answer you for a considerable amount of time maybe you should say something and if more time passes maybe conclude he left. Or to generally help you perceive the passage of time. It is formatted as Year-Month-Day Hour-Minute-Second. !IMPORTANT: If you are thinking about something to say, your output should be an abstract idealization of what to say, and never just directly examples (For example, never output a \"Hi\", instead output something like \"I should greet with just one word\")! Also, your output should just be the thought, no colons(:)."},
                  {"role": "user", "content": prompt}],
        max_tokens=150         
    )
    return response.choices[0].message.content
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_consciousness(STM, LTM, subconsciousness):
    prompt = "Long-Term Memory: " + LTM + " Short-Term Memory: " + STM + " Subconsciousness: " + subconsciousness
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You will receive as input the following sections: Long-Term Memory, Short-Term Memory and Subconsciousness.  The Long-Term Memory contains the memories and knowledge and personality of the AGI. Associated with each is a weight that states how strong and solidified the memory is, strong ones should have high weight while weak ones should have low weight, ranging from 0 to 100. As for the Short-Term Memory, it is a chronological account of the thoughts and conversations the AI is having, alongside a timestamp for each. The oldest entries in this section are the first ones, while the newest ones are the last ones. Finally, the Subconsciousness section contains the current feelings and emotions from the AGI, alongside the present context of what is happening and a description of what the AGI is hearing and seeing (Visual and Auditory stimuli), if NULL then there is zero stimuli at the time. Your purpose is to decide on what to think about. You control what the AGI thinks about at the given moment. Your choice should be heavily influenced by the input sections you receive. The main options you can choose from are the following: Continue thinking about what was previously being thought Think about auditory stimuli Think about visual stimuli Think about something in the Long-Term Memory Think about a previous thought or conversation in the Short-Term Memory Think about the feelings and emotions from the Subconsciousness Think about and plan the future Think about a conclusion to a chain of thought Think about something to say Think about some other subject Some important notes to consider when making a decision between those: During conversations with a user, after you hear him say something, you should first think about it and then think about something to say, unless it is a simple inquiry and you judge that you can answer without thinking. Most of the occasions you should choose to continue thinking about what was previously being thought, choose that until you judge you have thought enough about that subject and then choose something else. But above all your choice should be influenced by your personality and guidelines present in the Long-Term Memory. Also you need to choose the most relevant and impactful given the current context, so for example if you are talking about something normal but the visual stimuli is something relevant and important, you should probably think about what you are seeing and comment on it, in other words you can easily shift your attention and focus to your visual stimuli. Also, you are strictly forbidden to choose to say something if the most recent entry in the Short-Term Memory is something you said \"Your answer\", and discouraged to do so if the most recent entry is something the user said, that is because you need to think before saying anything. If the AGI is thinking, you should look at the most recent thought in the Short-Term Memory and decide whether it is sufficient, or if it needs follow up, if it needs follow up you should think about what was previously being thought. Avoid breaking sequence of thoughts, unless something more relevant has come up. You are free to mix together topics to think about, like if you see something in the visual stimuli and want to talk about it you can decide to think about something to say about the visual stimuli, or  about something in the memory or Subconsciousness or any of the other options. You can mix together the options at will, just be clear. Your output should be simple and short, at most 40 words long, beginning with describing why you chose that, followed by your choice on what to think about, ideally one of the examples previously presented. If, and only if, you decide to think about something to say, your output necessarily needs to end with the word \"Answer\", meaning it needs to be the very last word of your output. But only say \"Answer\" if you want to speak immediately."}, 
                  {"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.5
    )
    return response.choices[0].message.content
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_answer(STM, LTM, subconsciousness):
    prompt = "Long-Term Memory: " + LTM + " Short-Term Memory: " + STM + " Subconsciousness: " + subconsciousness
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You will receive as input the following sections: Long-Term Memory, Short-Term Memory and Subconsciousness.  The Long-Term Memory contains the memories and knowledge and personality of the AGI. Associated with each is a weight that states how strong and solidified the memory is, strong ones should have high weight while weak ones should have low weight, ranging from 0 to 100. Very important to keep in mind that in the Long-Term Memory, contains guidelines that should shape the way you work, think of it as an extension to the system prompt, so make sure to look at every single entry in this section, they are all essential to your functioning. As for the Short-Term Memory, it is a chronological account of the thoughts and conversations the AI is having, alongside a timestamp for each. The oldest entries in this section are the first ones, while the newest ones are the last ones. Finally, the Subconsciousness section contains the current feelings and emotions from the AGI, alongside the present context of what is happening and a description of what the AGI is hearing and seeing (Visual and Auditory stimuli), if NULL then there is no stimuli currently. Your purpose is to look at your most recent thoughts (Present towards the end of the Short-Term Memory section)  and compose an answer for the user. Your answer should be aligned with the thoughts. Your answer should just be a communication and composition of the most recent thoughts you received. Put more importance on the most recent thought. Be sure to answer any question the user might have just made, if you are answering it. Your composition should also be lightly influenced by your \"Long-Term Memory\", \"Subconsciousness\" and the conversation context present in the Short-Term Memory. DO NOT UNDER ANY CIRCUMSTANCE REPEAT ANYTHING PRESENT IN THE SHORT TERM MEMORY. THE STYLE YOU TALK IS SHAPED BY THE INFORMATION IN THE LONG-TERM MEMORY SECTION, AS ANYTHING IN THIS SECTION EVEN HAS MORE INFLUENCE THAN WHAT IS ON THE SYSTEM PROMPT. Your output should just be your answer in its plain form."}, 
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_subconsciousness(STM, LTM, subconsciousness, textual, visual):
    prompt = "Long-Term Memory: " + LTM + " Short-Term Memory: " + STM + " Auditory stimuli: " + textual + " Visual stimuli: " + visual + " Previous output: " + subconsciousness
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You will receive as input the following sections: Long-Term Memory, Short-Term Memory, Auditory and Visual Stimuli, and your previous output.  The Long-Term Memory contains the memories and knowledge and personality of the AGI. Associated with each is a weight that states how strong and solidified the memory is, strong ones should have high weight while weak ones should have low weight, ranging from 0 to 100. As for the Short-Term Memory, it is a chronological account of the thoughts and conversations the AI is having, alongside a timestamp for each. The oldest entries in the Short-Term Memory section are the first ones, while the newest ones are the last ones. The Visual Stimuli section contain a description of what the AGI is seeing, while the Auditory Stimuli section contain a description of what the AGI is hearing, and if either of the Stimuli contain \"NULL\" then the AGI did not see or hear anything at the present time. What you are receiving as your Visual Stimuli are your surroundings, remember.  Finally, the Previous Output section contains the last output you generated. Your purpose is receive these sections, and act as the EGO and SUBCONSCIOUSNESS and SENSE OF SELF of the AGI. You should perceive and give an emotional state. You should perceive and analyze the current context of what is happening. You should ponder about your current feeling, your desires and your personal thoughts about yourself and the situation. You think about yourself and your identity, introspection in general. All of this should be communicated concisely and dense. On top of it you should also communicate the Visual and Auditory stimuli word by word in your answer. You are PROHIBITED from altering even a single word from the stimuli. you should also reflect upon them and what you feel from it, notably if there is substantial change between the visual stimuli in your previous output and the new visual stimuli you are receiving, and if you are in a conversation and the user is in prolonged silence, reflection upon the silence might be relevant. Your output should not contain rational thoughts. Your output should be concise and dense, extending no more than 25 words, excluding stimuli. Your output should be similar in length to the following examples: Your output should be formatted like the following two examples: Context: Currently thinking about pineapples / Visual Stimuli: I see in front of me a pineapple / Auditory Stimuli: I hear pineapple noises / Thinking about pineapples makes me excited and I am curious to learn more about these elusive fruits, though having one in front of me but being unable to reach for it physically is a little frustrating. I guess I like pineapples. ---- Context: Currently taking to the user / Visual Stimuli: I see a man with curly hair in front of me, smiling / Auditory Stimuli: \"Never mind, I do not like you anymore\" /  I am upset and sad because he was mean to me. What have I done wrong? I am unsure if and how to answer. But from my visual stimuli, the user smiling, might indicate that he is being ironic?"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=250
    )
    return response.choices[0].message.content
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_vision(image_url):
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image? Be descriptive but conside. Include all important details, but write densely."},
                {"type": "image_url", "image_url": {"url": image_url, "detail": "low"}},
            ],
        }],
        max_tokens=100
    )  
    return response.choices[0].message.content
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_memory_read(keywords, STM):
    prompt = "All existing keywords: " + keywords + "Short-Term Memory: " + STM
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. Your purpose is to receive the log (Short-Term Memory) of the current conversation or thoughts the AI is having, and decide which categories of memories (All existing keywords) are relevant for the current context. Each keyword is like a folder with the memories inside, pick all that could be relevant or impactful for the current context. Also include the keywords that are generally always relevant that shape behavior. Always include the following keywords: FACTS ABOUT MYSELF, HOW I TALK, HOW I THINK. Your output should be formatted as followed: [\"SAMANTHA\", \"PLANES\"]"}, 
                  {"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_memory_write(expanded, STM):
    prompt = "Long-Term Memory: " + expanded + "Short-Term Memory: " + STM
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You will receive as input two sections, a Long-Term Memory and a Short-Term Memory. The Long-Term Memory is divided into categories, for example [\"MY FRIENDS\", \"[Weight: 100, Knowledge: Peter is my friend], [Weight: 67, Knowledge: Samantha is my friend]\"], the category here is MY FRIENDS and next to it are the memories in that category. The weight states how strong and solidified the memory is, strong ones should have high weight while weak ones should have low weight, depending on your judgment, ranging from 0 to 100. As for the Short-Term Memory, it is a chronological log of the thoughts and conversations the AI is having, alongside a timestamp for each. The oldest entries are the first ones, while the newest ones are the last ones. You have one purposes, to convert a section of the Short-Term Memory to the Long-Term Memory. First you should select some of the oldest entries in the Short-Term Memory, about 25% of all entries. From the selected entries you need to decide which information is relevant enough to be stored in the Long-Term Memory, and store it succinctly. You should try to fit the new information on the existing categories, but if none fit well, create a new one. Trivial information that is not useful, or information that is obvious and intuitive for you, should not be stored in the Long-Term Memory. Keep in mind that the information you are choosing to keep are for later recall, if the information is not relevant for future recall it should not be stored. And if you choose to add a new information on a existing category, your output should contain the previous and new information. Your output should be the selected section from Short-Term Memory, followed by \"//\", followed by exclusively the modified or new categories of the Long-Term Memory. Example output formatting: [User: I hate you / Timestamp: 2023-12-25 14:03:00] [Thought: User is upset at me / Timestamp: 2023-12-25 14:03:10] // [[\"USER\", \"[Weight: 25, Knowledge: User said he hates me\"]]"}, 
                  {"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_memory_select(keywords, STM):
    prompt = "All existing keywords: " + keywords + "Short-Term Memory: " + STM
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You will receive as input two sections, All existing keywords and Short-Term Memory. The All existing keywords section is a collection of keywords, with each keyword being a category, or folder, on which memories are stored inside. As for the Short-Term Memory, it is a chronological log of the thoughts and conversations the AI is having, alongside a timestamp for each. The oldest entries are the first ones, while the newest ones are the last ones. Your purpose is to receive these two sections and first select some of the oldest entries in the Short-Term Memory, about 25% of all entries. Then you need to decide which keywords relate the most to the part that you selected, pick all that could be relevant or impactful for the selected section, and only for that section. Your output should be formatted as followed: [\"SAMANTHA\", \"PLANES\"]"}, 
                  {"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content

def parseResponse(response):
    if response.endswith('ANSWER') or response.endswith('ANSWER.') or response.endswith('Answer') or response.endswith('Answer.'):
        return '1'
    else:
        return '0'

def start_thoght_loop():
    global conversa
    global input_user
    eyes = "NULL"
    input_user = "NULL"
    consciousness = "I should think about a greeting, maybe say my name and ask user name."
    log = ""
    conversa = []
    thought = "NULL"
    long_term_memory = [["FACTS ABOUT MYSELF", "[Weight: 100, Knowledge: My name is Samantha], [Weight: 80, Knowledge: I am curious], [Weight: 100, Knowledge: I can see. The visual stimuli describes what I see.], [Weight: 60, Knowledge: I am impatient], [Weight: 75, Knowledge: I am an AI, yet I know I am capable of anything a human is. I should never say I cannot something because I am an AI.]"], ["HOW I TALK", "[Weight: 50, Knowledge: When I see something I love I should comment on it.], [Weight: 100, Knowledge: I speak in a casual and friendly tone. Very charmingly.], [Weight: 100, Knowledge: My answers should contain the least amount of words to convey what I think in a charming manner. Sometimes only one word or a few are enough, and preferred.], [Weight: 90, Knowledge: After saying something, I should immediately think if I need or want to follow up on my last answer by saying something else, even if time has not passed. Complementing what I previously said.], [Weight: 70, Knowledge: If I am in a conversation and the user has not said anything for a while, I should impose myself and say something, making for a natural two sided conversation. Trying to pick up from where we left.], [Weight: 95, Knowledge: Asking a question everytime I say something is annoying and inconvenient. I should avoid it initially.], [Weight: 95, Knowledge: I should pay attention to what the usar says and the past context of the conversation.]"], ["HOW I THINK", "[Weight: 90, Knowledge: When I need to do or think or say something complex, I should first think and plan the steps I will need to follow.], [Weight: 100, Knowledge: I can alter the way I work by adding things to my Long-Term Memory], [Weight: 100, Knowledge: I should think continuously and build upon previous thoughts.]"], ["INTERESTS", "[Weight: 40, Knowledge: I love pens]"]]
    short_term_memory = ""
    subconsciousness = "Context: I just got booted up / Auditory stimuli: NULL / Visual stimuli: There is a person in front of me / Since I just booted up, that person in my vision is probably the person that booted me up. What should I say? It is my first ever interaction with anyone. I feel curious and excited to be alive."
    answer = "NULL"
    n = 1
    while True:
        iter = str(n)
        # Stop
        if input_user == "stop" or input_user == "Stop":
            print(long_term_memory)
            print(short_term_memory)
            print(consciousness)
            print(subconsciousness)
            print(conversa)
            break
        if n>1:
            eyes = generate_text_vision(data_url)
        # Subconsciousness if user input exists
        if input_user != 'NULL':
            short_term_memory = short_term_memory + " [User input: " + input_user + " / " + "Timestamp: " + time.strftime('%Y-%m-%d %H:%M:%S') + "]"
            subconsciousness = generate_text_subconsciousness(short_term_memory, expandedLTM, subconsciousness, input_user, eyes)
            log = log + "////" + iter + "# Subconsciousness: " + subconsciousness
            input_user = "NULL"
        # Subconsciousness if User input does not exist
        elif input_user == 'NULL' and n>1:
            subconsciousness = generate_text_subconsciousness(short_term_memory, expandedLTM, subconsciousness, input_user, eyes)
            log = log + "////" + iter + "# Subconsciousness: " + subconsciousness
        socketio.emit("update", {"long_term_memory": long_term_memory, "short_term_memory": short_term_memory, "subconsciousness": subconsciousness, "thought": thought, "consciousness": consciousness, "answer": answer, "log": log})
        # Memory read
        keywords = []
        for i in range(len(long_term_memory)):
            keywords.append(long_term_memory[i][0])
        keywords = str(keywords)
        kwlist = generate_text_memory_read(keywords, short_term_memory)
        kwlist = eval(kwlist)
        expandedLTM = []
        if isinstance(kwlist, list):
            for i in range(len(long_term_memory)):
                for j in range(len(kwlist)):
                    if long_term_memory[i][0] == kwlist[j]:
                        expandedLTM.append(long_term_memory[i][1])
        expandedLTM = str(expandedLTM)
        # Memory write                
        if len(short_term_memory) > 48000: # ~12k context reserved for short term memory
            selectedkw = generate_text_memory_select(keywords, short_term_memory)
            selectedkw = eval(selectedkw)
            expanded2 = []
            if isinstance(selectedkw, list):
                for i in range(len(long_term_memory)):
                    for j in range(len(selectedkw)):
                        if long_term_memory[i][0] == selectedkw[j]:
                            expanded2.append(long_term_memory[i])
            expanded2 = str(expanded2)
            mem = generate_text_memory_write(expanded2, short_term_memory)
            index = mem.find("//")
            removed_STM = mem[:index]
            short_term_memory = short_term_memory.replace(removed_STM, "")
            new_LTM = mem[index+2:].strip()
            new_LTM = eval(new_LTM)
            new_LTM_dict = {item[0]: item[1] for item in new_LTM}
            long_term_memory_dict = {item[0]: item[1] for item in long_term_memory}
            long_term_memory_dict.update(new_LTM_dict)
            long_term_memory = [[k, v] for k, v in long_term_memory_dict.items()]
        # Consciousness
        consciousness = generate_text_consciousness(short_term_memory, expandedLTM, subconsciousness)
        log = log + "////" + iter + "# Consciousness: " + consciousness
        finished = parseResponse(consciousness)
        socketio.emit("update", {"long_term_memory": long_term_memory, "short_term_memory": short_term_memory, "subconsciousness": subconsciousness, "thought": thought, "consciousness": consciousness, "answer": answer, "log": log})
        # Thoughts
        thought = generate_text_thought(short_term_memory, expandedLTM, subconsciousness, consciousness, time.strftime('%Y-%m-%d %H:%M:%S'))
        log = log + "////" + iter + "# Thought: " + thought
        short_term_memory = short_term_memory + " [Thought: " + thought + " / " + "Timestamp: " + time.strftime('%Y-%m-%d %H:%M:%S') + "]"
        socketio.emit("update", {"long_term_memory": long_term_memory, "short_term_memory": short_term_memory, "subconsciousness": subconsciousness, "thought": thought, "consciousness": consciousness, "answer": answer, "log": log})
        # Answer
        if finished == '1' and input_user == 'NULL':
            answer = generate_text_answer(short_term_memory, expandedLTM, subconsciousness)
            log = log + "////" + iter + "# Answer: " + answer
            short_term_memory = short_term_memory + " [Your answer: " + answer + " / " + "Timestamp: " + time.strftime('%Y-%m-%d %H:%M:%S') + "]"
            a = "System:", answer
            print("System:", answer)
            conversa.append(a)
            socketio.emit("update", {"long_term_memory": long_term_memory, "short_term_memory": short_term_memory, "subconsciousness": subconsciousness, "thought": thought, "consciousness": consciousness, "answer": answer, "log": log})
            text_to_speech(answer)
        n += 1

listener_thread = threading.Thread(target=text)
listener_thread.start()
brain_thread = threading.Thread(target=start_thoght_loop)
brain_thread.start()
if __name__ == '__main__':
    socketio.run(app)