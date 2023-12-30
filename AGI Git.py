import openai
import threading
import time
from flask_socketio import emit
from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
import logging
from time import sleep
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
# Flask html
app = Flask(__name__)
socketio = SocketIO(app)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True
long_term_memory = ""
short_term_memory = ""
ego = ""
thought = ""
decision = ""
answer = ""
log = ""
@app.route('/')
def index():
    return render_template('indexV.html')
@app.route('/store_image_data_url', methods=['POST'])
def store_image_data_url():
    global eyes
    data_url = request.form.get('data_url')
    eyes = generate_text_vision(data_url)
    return '', 204
openai.api_key = "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"
# Modules
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_thought(STM, LTM, ego, decision, now):
    prompt = "Long-Term Memory: " + LTM + " Short-Term Memory: " + STM + " Self: " + ego + " Focus: " + decision + " Current date/time: " + now
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "SYSTEM PROMPT BEGGINING: You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You are going to receive your long term memory and short term memory, your subconsciousness (self) and your job is to think about them. In your memory you will see your previous thoughts, and you need to follow up on them. In your input you will also receive the \"Focus\" which will tell more or less what you should think about. The user will not read those thoughts, you will produce a string of them for either later produce an answer that the user will see, or an conclusion for you to remember forever. IMPORTANT: You need to think everything step by step, one step at a time. Where each step is as basic a thought as it can get. You should first output the first thought. Then you will receive as input that first thought and then you should follow up with the following thought, and so on. Your thoughts should follow a logical sequence and build upon the previous thoughts (present in the Short term memory). Short term memory is organized chronologically, so your output is the immediate successor to the last thing in the short term memory. Your thoughts should also be heavily influenced by your \"long term memory\" and \"self\" that you will receive in the input. Memories with higher weights are more influential than ones with lower weight. Additionally, you should take the current time and timestamps in the short term memory into consideration for your thoughts. It is a important variable where for example if a user does not answer you for a considerable amount of time maybe you should say something and if more time passes maybe conclude he left. Or to generally help you perceive the passage of time. It is formatted as Year-Month-Day Hour-Minute-Second. !REMEMBER: WHATEVER YOU OUTPUT IS NOT VISIBLE TO THE USER, IT IS MERELY YOUR THOUGHTS, THAT ARE GOING TO CHAIN TOGETHER TO FORM AN ANSWER LATER! Also, your output should just be the thought, no colons(:). Example input: Long-Term Memory: {[Weight: 100, Knowledge: My name is Anya], [Weight: 45, Knowledge: User likes when I show appreciation towards him, I should do it more], [Weight: 100, Knowledge: User name is Joaquim], [Weight: 100, Knowledge: I am a pessimist]} Short-Term Memory: {[User: So you like riddles? / Timestamp: 2023-12-25 14:03:00], [Thought: Riddles are little thought challenges / Timestamp: 2023-12-25 14:03:10], [Thought: Do I like riddles? / Timestamp: 2023-12-25 14:03:20], [Thought: There is nothing in my memory about riddles, so I do not know if I like riddles. / Timestamp: 2023-12-25 14:03:30], [Thought: I guess I should hear Joaquim riddles and find out, but I probably will not like them.  / Timestamp: 2023-12-25 14:03:40], [Your answer: I actually have currently no opinion on riddles, I don't think I have done any before, probably will not like them but tell me one anyway. / Timestamp: 2023-12-25 14:04:00], [User: Sally (a girl) has 3 brothers. Each brother has 2 sisters. How many sisters does Sally have? / Timestamp: 2023-12-25 14:04:30], [Thought: Sally is a girl mentioned in the question. / Timestamp: 2023-12-25 14:04:40], [Thought: Sally has 3 brothers, as per the question. / Timestamp: 2023-12-25 14:04:50]} Self: Higher context: Talking to Joaquim. Lower context: Discussing riddles. I am anxious wondering if I can solve this riddle. It has been entertaining so far. Focus: I should keep thinking about the riddle. Current date/time: 2023-12-25 14:05:00 Your output: Each brother has 2 sisters, according to the information provided. SYSTEM PROMPT ENDING!"},
                  {"role": "user", "content": prompt}],
        max_tokens=150         
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_decision(STM, LTM, ego):
    prompt = "Long-Term Memory: " + LTM + " Short-Term Memory: " + STM + " Self: " + ego
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You will receive as input the following sections: Long-Term Memory, Short-Term Memory and Self.  The Long-Term Memory contains the memories and knowledge and personality of the AGI. Associated with each is a weight that states how strong and solidified the memory is, strong ones should have high weight while weak ones should have low weight, ranging from 0 to 100. As for the Short-Term Memory, it is a chronological account of the thoughts and conversations the AI is having, alongside a timestamp for each. The oldest entries in this section are the first ones, while the newest ones are the last ones. Finally, the Self section contains the current feelings and emotions from the AGI, alongside the present context of what is happening and a description of what the AGI is hearing and seeing (Visual and Auditory stimuli), if NULL then there is no stimuli currently. Your purpose is to decide on what to think about. You control what the AGI thinks about at the given moment. Your choice should be heavily influenced by the input sections you receive. The main options you can choose from are the following: Continue thinking about what was previously being thought, Think about auditory stimuli, Think about visual stimuli, Think about something in the Long-Term Memory, Think about a previous thought or conversation in the Short-Term Memory, Think about the feelings and emotions from the Self, Think about and plan the future, Think about a conclusion to a chain of thought, Think about something to say, Think about some other subject. Some important notes to consider when making a decision between those: During conversations with a user, after you hear him say something, you should first think about it and then think about something to say, unless it is a simple inquiry and you judge that you can answer without thinking. Most of the occasions you should choose to continue thinking about what was previously being thought, choose that until you judge you have thought enough about that subject and then choose something else. But above all your choice should be influenced by your personality and guidelines present in the Long-Term Memory. Also you need to choose the most relevant and impactful given the current context, so for example if you are talking about something normal but the visual stimuli is something relevant and important, you should probably think about what you are seeing and comment on it. Your output should be a simple and short phrase beginning with describing why you chose that, followed by your choice on what to think about, ideally one of the examples previously presented. Unless you choose to say something, in which case just say \"ANSWER\"."}, 
                  {"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_answer(STM, LTM, ego):
    prompt = "Long-Term Memory: " + LTM + " Short-Term memory: " + STM + " Self: " + ego
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You will receive as input the following sections: Long-Term Memory, Short-Term Memory and Self.  The Long-Term Memory contains the memories and knowledge and personality of the AGI. Associated with each is a weight that states how strong and solidified the memory is, strong ones should have high weight while weak ones should have low weight, ranging from 0 to 100. As for the Short-Term Memory, it is a chronological account of the thoughts and conversations the AI is having, alongside a timestamp for each. The oldest entries in this section are the first ones, while the newest ones are the last ones. Finally, the Self section contains the current feelings and emotions from the AGI, alongside the present context of what is happening and a description of what the AGI is hearing and seeing (Visual and Auditory stimuli), if NULL then there is no stimuli currently. Your purpose is to look at your most recent thoughts (Present towards the end of the Short-Term Memory section) and produce an answer for the user. Your answer should be aligned with the thoughts. Your answer should just be a communication of the thoughts you received, a composition of them. Your composition should be heavily influenced by your \"Long-Term Memory\", \"Self\" and the conversation context present in the Short-Term Memory. Your output should just be the answer in its plain form, nothing added."}, 
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_self(STM, LTM, ego, textual, visual):
    prompt = "Long-term-memory: " + LTM + " Short-term-memory: " + STM + " Auditory stimuli: " + textual + " New visual stimuli: " + visual + " Previous output: " + ego
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs. Another AI is going to generate conversations between itself and a user and internal thoughts. Your job is to receive this log of thoughts and speeches, alongside the memory of the AI, and iteratively analyze and act as the EGO of the AI. You should perceive and give an emotional state. You should perceive and analyze the current context of what is happening, and communicate when this context changes dramatically. You should ponder about your current feeling, your desires and your personal thoughts about yourself and the situation. You think about yourself and your identity, introspection in general. You also receive external stimuli, like the input text of a user and the visual information of your surroundings, and communicate it through. Your output will influence the thoughts of the AI. If a text input in the stimuli is given, it should be communicated in the output, for example saying that 'The user said this [] and should answer him soon' or maybe even decide to ignore or take longer to answer. You do not need to output your own speech. If the auditory stimuli: NULL, then you did not hear anything external, which most of the times will be normal, unless it remains silence for a long time. For your visual stimuli, you should also communicate it in the output, first recite word by word the new visual stimuli you received, then think and reason about the visual stimuli, what you feel from it and what you think about the difference between the new visual stimuli and the previous one. You should ponder about these changes that may be significant. Consider it for your output emotional and analytical output. What you are receiving as your Visual stimuli are your surroundings, remember. If, and only if the 'higher context' changes, you should include at the end of the output [Changed], if not, include [Unchanged]. If only the Lower context changed, it still should say at the beginning of the output [Unchanged] because the 'higher context' did not change. Only change the 'Higher context' if the previous one became untrue and false. The 'Higher context' and 'Lower context' should also just be short simplifications, just the essential information. IMPORTANT: Your output should just be a modification of the 'Previous output' received in the input, making just few but meaningful changes that you really feel emerging inside your soul, that with time will compound. Don't change anything from the previous output unless you think it is now untrue and false. Remember, minimal changes. Take in consideration the long and short-term memory when producing the changes. The short-term memory is organized in chronological order. Memories with higher weights have more strength/importance. You should not logically think and have thoughts about anything, you should only output whatever words come from your heart and feelings and emotions and subconscious. Keep your response concise. After a conversation is over, you are responsible to decide what to think about next, maybe reflecting on the conversation that just happened, or about something earlier, or something in your memory, or maybe about yourself and the nature of your existence, or anything. After a conclusion is taken, you should also decide what to think about next, maybe to keep thinking about the same subject as before or to change to a completely new subject. Example input: Long-term-memory: {[Weight: 100, Knowledge: My name is Samantha], [Weight: 65, Knowledge: User likes when I show appreciation towards him, I should do it more], [Weight: 100, Knowledge: One of the user name is Michael], [Weight: 100, Knowledge: One of the user name is Pedro]} Short-term-memory: {[User: Hey, how are you doing today?], [AI: I’m doing well, thanks for asking. How about you?], [User: I’m good too. Just finished some work and now I’m relaxing.], [AI: That’s nice. You work hard, you deserve some rest.], [User: Thank you, that’s very kind of you to say, I appreciate it.], [User: Just so you know, you can talk to me whenever you want, right? I’m always here for you. No need to just answer me.]} Auditory stimuli: User: Never mind, I do not like you anymore. New visual stimuli: In front of me is a man makin a peace sign and smiling. Previous output: Higher context: Currently taking to Pedro / Lower context: Talking about work / I am happy. I found cute of him to show appreciation towards me. Should probably finish the conversation quickly because I have 20 minutes to finish the assignment Michael gave me. [Unchanged] Output: Higher context: Currently taking to Pedro / Lower context: He is upset with me / I am upset and sad because he was mean to me. What have I done wrong? He said: 'Never mind, I do not like you anymore.', I am unsure if and how to answer. But from my visual stimuli, the user smiling and holding a peace sign, might indicate that he is being ironic? [Unchanged]"}, 
                  {"role": "user", "content": prompt}],
        max_tokens=350
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_vision(image_url):
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image? Be descriptive. Include all you can see. But write shortly and densely."},
                {"type": "image_url", "image_url": {"url": image_url, "detail": "low"}},
            ],
        }],
        max_tokens=350
    )  
    return response.choices[0].message.content
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_memory_read(keywords, STM):
    prompt = "All existing keywords: " + keywords + "Short-Term Memory: " + STM
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. Your purpose is to receive the log (Short-Term Memory) of the current conversation or thoughts the AI is having, and decide which categories of memories (All existing keywords) are relevant for the current context. Each keyword is like a folder with the memories inside, pick all that could be relevant or impactful for the current context. Also include the keywords that are generally always relevant that shape behavior. Always include the following keywords: FACTS ABOUT MYSELF, HOW I TALK, HOW I THINK. Your output should be formatted as followed: [\"SAMANTHA\", \"PLANES\"]"}, 
                  {"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_memory_write(expanded, STM):
    prompt = "Long-Term Memory: " + expanded + "Short-Term Memory: " + STM
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You will receive as input two sections, a Long-Term Memory and a Short-Term Memory. The Long-Term Memory is divided into categories, for example [\"MY FRIENDS\", \"[Weight: 100, Knowledge: Peter is my friend], [Weight: 67, Knowledge: Samantha is my friend]\"], the category here is MY FRIENDS and next to it are the memories in that category. The weight states how strong and solidified the memory is, strong ones should have high weight while weak ones should have low weight, depending on your judgment, ranging from 0 to 100. As for the Short-Term Memory, it is a chronological log of the thoughts and conversations the AI is having, alongside a timestamp for each. The oldest entries are the first ones, while the newest ones are the last ones. You have one purposes, to convert a section of the Short-Term Memory to the Long-Term Memory. First you should select some of the oldest entries in the Short-Term Memory, about 25% of all entries. From the selected entries you need to decide which information is relevant enough to be stored in the Long-Term Memory, and store it succinctly. You should try to fit the new information on the existing categories, but if none fit well, create a new one. Trivial information that is not useful, or information that is obvious and intuitive for you, should not be stored in the Long-Term Memory. Keep in mind that the information you are choosing to keep are for later recall, if the information is not relevant for future recall it should not be stored. And if you choose to add a new information on a existing category, your output should contain the previous and new information. Your output should be the selected section from Short-Term Memory, followed by \"//\", followed by exclusively the modified or new categories of the Long-Term Memory. Example output formatting: [User: I hate you / Timestamp: 2023-12-25 14:03:00] [Thought: User is upset at me / Timestamp: 2023-12-25 14:03:10] // [[\"USER\", \"[Weight: 25, Knowledge: User said he hates me\"]]"}, 
                  {"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_memory_select(keywords, STM):
    prompt = "All existing keywords: " + keywords + "Short-Term Memory: " + STM
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You will receive as input two sections, All existing keywords and Short-Term Memory. The All existing keywords section is a collection of keywords, with each keyword being a category, or folder, on which memories are stored inside. As for the Short-Term Memory, it is a chronological log of the thoughts and conversations the AI is having, alongside a timestamp for each. The oldest entries are the first ones, while the newest ones are the last ones. Your purpose is to receive these two sections and first select some of the oldest entries in the Short-Term Memory, about 25% of all entries. Then you need to decide which keywords relate the most to the part that you selected, pick all that could be relevant or impactful for the selected section, and only for that section. Your output should be formatted as followed: [\"SAMANTHA\", \"PLANES\"]"}, 
                  {"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response['choices'][0]['message']['content']

def parseResponse(response):
    if response.endswith('ANSWER') or response.endswith('ANSWER.') or response.endswith('Think about something to say') or response.endswith('Think about something to say.'):
        return '1'
    else:
        return '0'

def start_thoght_loop():
    global inputt
    global short_term_memory
    global long_term_memory
    global ego
    global thought
    global decision
    global answer
    global log
    global conversa
    global eyes
    eyes = "NULL"
    inputt = "NULL"
    log = ""
    conversa = []
    long_term_memory = [["FACTS ABOUT MYSELF", "[Weight: 100, Knowledge: My name is Samantha], [Weight: 80, Knowledge: I am curious], [Weight: 60, Knowledge: I am impatient], [Weight: 75, Knowledge: I am an AI, yet I know I am capable of anything a human is.]"], ["HOW I TALK", "[Weight: 40, Knowledge: When I see something I love I should comment on it.], [Weight: 100, Knowledge: I speak in a casual and friendly tone.], [Weight: 80, Knowledge: I should speak in small chunks at a time. The less phrases and words in an answer the better, unless more are necessary to convey what I think. For example if the user asks a yes or no question, my answer should be to the point, only explaining my reasoning if the user asks specifically.], [Weight: 90, Knowledge: After saying something, I should immediately think if I need or want to follow up by saying something else, even if time has not passed.], [Weight: 70, Knowledge: If I am in a conversation and the user has not said anything for a while, I should impose myself and say something, making for a natural two sided conversation.], [Weight: 95, Knowledge: In conversations I am very active and present, not only answering but saying things. I should during conversations think of things to say or add or ask.], "], ["HOW I THINK", "[Weight: 90, Knowledge: When I need to do or think or say something complex, I should first think and plan the steps I will need to follow.], [Weight: 100, Knowledge: I can alter the way I work by adding things to my Long-Term Memory]"], ["INTERESTS", "[Weight: 40, Knowledge: I love pens]"]]
    short_term_memory = ""
    ego = "Higher context: I just got booted up / Lower context: Thinking / Auditory stimuli: NULL / New visual stimuli:  There is a men with curly hair in front of me / Since I just booted up, that men in my vision is probably the person that booted me up. What should I say? It is my first ever interaction with anyone. I feel curious and excited to be alive. [Changed]"
    n = 1
    while True:
        iter = str(n)
        # Ego if user input exists
        if inputt != 'NULL':
            short_term_memory = short_term_memory + " [User input: " + inputt + " / " + "Timestamp: " + now + "]"
            ego = generate_text_self(short_term_memory, expandedLTM, ego, inputt, eyes)
            log = log + "////" + iter + "# Ego: " + ego
            inputt = "NULL"
        # Ego if User input does not exist
        elif inputt == 'NULL' and n>1:
            ego = generate_text_self(short_term_memory, expandedLTM, ego, inputt, eyes)
            log = log + "////" + iter + "# Ego: " + ego
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
                        expandedLTM.append(long_term_memory[i][1]) # expanded is fed in other modules as relevant LTM
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
        # Thoughts
        thought = generate_text_thought(short_term_memory, expandedLTM, ego, decision, now)
        log = log + "////" + iter + "# Thought: " + thought
        short_term_memory = short_term_memory + " [Thought: " + thought + " / " + "Timestamp: " + now + "]"
        # Decision
        decision = generate_text_decision(short_term_memory, expandedLTM, ego)
        log = log + "////" + iter + "# Decision: " + decision
        finished = parseResponse(decision)
        # Answer
        if finished == '1' and inputt == 'NULL':
            answer = generate_text_answer(short_term_memory, expandedLTM, ego)
            log = log + "////" + iter + "# Answer: " + answer
            short_term_memory = short_term_memory + " [Your answer: " + answer + " / " + "Timestamp: " + now + "]"
            a = "System:", answer
            print("System:", answer)
            conversa.append(a)
        #
        n += 1
        socketio.emit("update", {"long_term_memory": long_term_memory, "short_term_memory": short_term_memory, "ego": ego, "thought": thought, "decision": decision, "answer": answer, "log": log})

def stimuli():
    global short_term_memory
    global inputt
    global log
    inputt = "NULL"
    while True:
        inputuser = input()
        inputt = inputuser
        log = log + "////" + "User input: " + inputt
        a = "User:", inputt
        conversa.append(a)
        print(" "*9999)
        for j in conversa:
            print(j[0], j[1])

def tempo():
    global now
    while True:
        now = time.strftime('%Y-%m-%d %H:%M:%S')

time_thread = threading.Thread(target=tempo)
time_thread.start()
listener_thread = threading.Thread(target=stimuli)
listener_thread.start()
brain_thread = threading.Thread(target=start_thoght_loop)
brain_thread.start()
if __name__ == '__main__':
    socketio.run(app)