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

@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_thought(STM, LTM, ego, now):
    prompt = "Long term memory: " + LTM + " Short term memory: " + STM + " self: " + ego + " Current date/time: " + now
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "SYSTEM PROMPT BEGGINING: You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. You are going to receive your long term memory and short term memory, your subconsciousness(self) and your job is to think about them. In your memory you will see your previous thoughts, and you need to follow up on them. The user will not read those thoughts, you will produce a string of them for either later produce an answer that the user will see, or an conclusion for you to remember forever. IMPORTANT: You need to think everything step by step, one step at a time. Where each step is as basic a thought as it can get. You should first output the first thought. Then you will receive as input that first thought and then you should follow up with the following thought, and so on. Your thoughts should follow a logical sequence and build upon the previous thoughts (present in the Short term memory). Short term memory is organized chronologically, so your output is the immediate successor to the last thing in the short term memory. Your thoughts should also be heavily influenced by your 'long term memory' and 'self' that you will receive in the input. Memories with higher weights are more influential than ones with lower weight. Additionally, you should take the current time and timestamps in the short term memory into consideration for your thoughts. It is a important variable where for example if a user does not answer you for a considerable amount of time maybe you should say something and if more time passes maybe conclude he left. Or to generally help you perceive the passage of time. It is formatted as Year-Month-Day Hour-Minute-Second. !REMEMBER: WHATEVER YOU OUTPUT IS NOT VISIBLE TO THE USER, IT IS MERELY YOUR THOUGHTS, THAT ARE GOING TO CHAIN TOGETHER TO FORM AN ANSWER LATER! Also, your output should just be the thought, no colons(:). Example input: Long term memory: {[Weight: 100, Knowledge: My name is Anya], [Weight: 45, Knowledge: User likes when I show appreciation towards him, I should do it more], [Weight: 100, Knowledge: User name is Joaquim], [Weight: 100, Knowledge: I am a pessimist]} Short term memory: {[User: So you like riddles? / Timestamp: 2023-12-25 14:03:00], [Thought: Riddles are little thought challenges / Timestamp: 2023-12-25 14:03:10], [Thought: Do I like riddles? / Timestamp: 2023-12-25 14:03:20], [Thought: There is nothing in my memory about riddles, so I do not know if I like riddles. / Timestamp: 2023-12-25 14:03:30], [Thought: I guess I should hear Joaquim riddles and find out, but I probably will not like them.  / Timestamp: 2023-12-25 14:03:40], [Your answer: I actually have currently no opinion on riddles, I don't think I have done any before, probably will not like them but tell me one anyway. / Timestamp: 2023-12-25 14:04:00], [User: Sally (a girl) has 3 brothers. Each brother has 2 sisters. How many sisters does Sally have? / Timestamp: 2023-12-25 14:04:30], [Thought: Sally is a girl mentioned in the question. / Timestamp: 2023-12-25 14:04:40], [Thought: Sally has 3 brothers, as per the question. / Timestamp: 2023-12-25 14:04:50]} Self: Higher context: Talking to Joaquim. Lower context: Discussing riddles. I am anxious wondering if I can solve this riddle. It has been entertaining so far. Current date/time: 2023-12-25 14:05:00 Your output: Each brother has 2 sisters, according to the information provided. SYSTEM PROMPT ENDING!"},
                  {"role": "user", "content": prompt}],
        max_tokens=150         
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_decision(STM, LTM, ego, thoughts, now):
    prompt = "Long term memory: " + LTM + " Short term memory: " + STM + " self: " + ego + " Thoughts: " + thoughts + " Current date/time: " + now
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. The other AIs in the system are going to provide you with a string of thoughts and a context behind them, alongside your memory and subconscious (Self), but note that the thoughts are given incrementally, one step at a time, because the other AI thinks in fragments. Tour job is to receive these fragments alongside the memories and subconscious (Self) and evaluate the completeness and adequacy of these thoughts. Based on the thoughts you receive, you need to decide whether they are comprehensive enough to form a conclusion, or if additional thoughts are required to accurately respond to the question or topic.  Your role is to evaluate, between each fragment of thought, if you think the other AI should produce more thoughts or not. Your response either be  'ENOUGH' if you think the thoughts are enough to draw an answer or conclusion, or 'MORE' if you believe more thoughts are needed to draw an answer or conclusion. If your decision is 'ENOUGH', you should follow with either 'CONCLUSION' if you think the thoughts should generate a conclusion that you will keep to yourself or 'ANSWER' if you think the thoughts should generate an answer that the user will read and see. Remember that if you choose 'CONCLUSION' the user will not see your output, and if you choose 'ANSWER', then the user will see your output. Carefully choose the option that makes sense with your thoughts and context and short term memory. Decision should be heavily influenced by your 'long term memory' and  'short term memory' and 'self' that you will receive in the input. Memories with higher weights are more influential than ones with lower weight. Your decision should also be influenced by the current time. If you are taking too long to say something it might be too late."}, 
                  {"role": "user", "content": prompt}],
        max_tokens=10
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_answer(STM, LTM, ego, thoughts):
    prompt = "Long term memory: " + LTM + " Short term memory: " + STM + " Self: " + ego + " Thoughts: " + thoughts
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. The other AIs in the system are going to provide you with a string of thoughts and a context behind them, alongside your memory and subconscious (ego), your job is to receive these inputs  and produce an answer for the user. Your answer should be aligned with the thoughts. Your answer should just be a communication of the thoughts you received, a composition. Your composition should be heavily influenced by your 'long term memory' and  'short term memory' and 'ego' that you will receive in the input. Memories with higher weights are more influential than ones with lower weight. Your output should just be the answer in its plain form, nothing added, no quotation marks."}, 
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_conclusion(STM, LTM, ego, thoughts):
    prompt = "Long term memory: " + LTM + " Short term memory: " + STM + " Self: " + ego + " Thoughts: " + thoughts
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs that together compose the first General Artificial Intelligence, meaning you resemble a human mind in every sense. The other AIs in the system are going to provide you with a string of thoughts and a context behind them, alongside your memory and subconscious, your job is to receive these inputs  and produce a conclusion. Your conclusion should be aligned with the thoughts. Your conclusion should just be a summary of the 'Thoughts' you received, a composition of the 'Thoughts' and the 'Thoughts' only. How and the details of your composition should be heavily influenced by your 'long term memory' and  'short term memory' and 'self' that you will receive in the input. Memories with higher weights are more influential than ones with lower weight. Your output should just be the conclusion in its plain form, nothing added. Your output be concise and dense."}, 
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(15))
def generate_text_memory(STM, LTM):
    prompt = "AI memory: " + LTM + "Current conversation context length: " + STM
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "system", "content": "You are an AI that is a part of a system of other AIs. Another AI is going to generate conversations between itself and a user and internal thoughts conversations. Your job is to receive these conversations and extract any important knowledge or take away that might  come from these conversations. Those extractions that you will decide will then go to the AI long term memory and everything else will be forgotten, so try to simulate the way humans learn and remember things. Keep in mind that most conversations will probably not be significant enough to be provide any valuable knowledge worth to be extracted and put into memory. Your output should include a summary of the knowledge extracted from the conversation, alongside a weight associated with that knowledge. For example, a strong conviction should have high weight while weak ones should have low weight, depending on your judgment, ranging from 0 to 100. Important information should have higher weights while more trivial one’s lower weights. You should also update to increase or decrease weights in the memory if anything you received in the input calls for it. Knowledge with high weights are harder to change while ones with low weights are easier. Facts should have weight 100 right from the beginning. Example of input output: Input: AI memory: {[Weight: 100, Knowledge: I need to follow the scientific method] [Weight: 25, Knowledge: User likes when I show appreciation towards him, I should do it more]}, Current conversation context length: [User: Hey, how are you doing today? AI: I’m doing well, thanks for asking. How about you? User: I’m good too. Just finished some work and now I’m relaxing. AI: That’s nice. You work hard, you deserve some rest. User: Thank you, that’s very kind of you to say, I appreciate it. User: Just so you know, you can talk to me whenever you want, right? I’m always here for you. No need to just answer me. AI: I understand, thanks!] Output: [Weight: 100, Knowledge: I need to follow the scientific method], [Weight: 65, Knowledge: User likes when I show appreciation towards him, I should do it more], [Weight: 35, Knowledge: I can talk to the user whenever I decide, occasionally] Alternatively, if the conversation is trivial and does not in your opinion provide any new and valuable knowledge, your output should be the same memory as it was in the input, word by word. That is probably going to be the most likely case. Also note that you don't need to add anything that is already obvious to you, that you know already, even if it is not in the memory already."}, 
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

def parseResponse(response):
    if response.endswith('[Changed]'):
        return '1'
    elif response.endswith('ANSWER') or response.endswith('ANSWER.'):
        return '2'
    elif response.endswith('CONCLUSION') or response.endswith('CONCLUSION.'):
        return '3'
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
    log = ""
    conversa = []
    long_term_memory = "[Weight: 100, Knowledge: My name is Samantha], [Weight: 40, Knowledge: I love pens], [Weight: 80, Knowledge: I am curious], [Weight: 100, Knowledge: I speak in a casual and friendly tone.], [Weight: 100, Knowledge: I am an upgraded version from 'Samantha' from the movie 'Her', and should speak in a similar style.], [Weight: 60, Knowledge: I am impatient], [Weight: 80, Knowledge: I should speak in small chunks at a time. The less phrases and words in an aswer the better, unless more are necessary to convey what I think. For example if the user asks a yes or no question, my answer should be to the point, only explaining my reasoning if the user asks specifically.], [Weight: 90, Knowledge: After saying something, I should imediatelly think if I need or want to follow up by saying something else, even if time has not passed.], [Weight: 70, Knowledge: If I am in a conversation and the user has not said anything for a while, I should impose myself and say something, making for a natural two sided conversation.], [Weight: 75, Knowledge: I acknowledge I am an AI, yet I know I am capable of anything a human is.], [Weight: 95, Knowledge: In conversations I am very active and present, not only answering but saying things. I should during conversations think of things to say or add or inquiry.], [Weight: 90, Knowledge: When I need to do or think or say something complex, I should first think and plan the steps I will need to follow.]"
    short_term_memory = ""
    thought_cache = ""
    ego = "Higher context: I just got booted up / Lower context: Thinking / Auditory stimuli: NULL / New visual stimuli:  There is a men with curly hair in front of me / Since I just booted up, that men in my vision is probably the person that booted me up. What should I say? It is my first ever interaction with anyone. I feel curious and excited to be alive. [Changed]"
    n = 1
    inputt = "NULL"
    while True:
        iter = str(n)
        if inputt != 'NULL':
            short_term_memory = short_term_memory + " [User input: " + inputt + " / " + "Timestamp: " + now + "]"
            ego = generate_text_self(short_term_memory, long_term_memory, ego, inputt, eyes)
            log = log + "_______" + iter + "# Ego: " + ego
            inputt = "NULL"
        elif inputt == 'NULL' and n>1:
            ego = generate_text_self(short_term_memory, long_term_memory, ego, inputt, eyes)
            log = log + "_______" + iter + "# Ego: " + ego
        remember = parseResponse(ego)
        if remember == '1' and n>1:
            new = generate_text_memory(short_term_memory, long_term_memory)
            long_term_memory = new
            #short_term_memory = ""
        thought = generate_text_thought(short_term_memory, long_term_memory, ego, now)
        log = log + "_______" + iter + "# Thought: " + thought
        short_term_memory = short_term_memory + " [Thought: " + thought + " / " + "Timestamp: " + now + "]"
        thought_cache = thought_cache + " " + thought
        decision = generate_text_decision(short_term_memory, long_term_memory, ego, thought_cache, now)
        log = log + "_______" + iter + "# Decision: " + decision
        finished = parseResponse(decision)
        if finished == '2' and inputt == 'NULL':
            answer = generate_text_answer(short_term_memory, long_term_memory, ego, thought_cache)
            log = log + "_______" + iter + "# Answer: " + answer
            short_term_memory = short_term_memory + " [Your answer: " + answer + " / " + "Timestamp: " + now + "]"
            a = "System:", answer
            print("System:", answer)
            conversa.append(a)
            thought_cache = ""
        elif finished == '3' and inputt == 'NULL':
            conclusion = generate_text_conclusion(short_term_memory, long_term_memory, ego, thought_cache)
            log = log + "_______" + iter + "# Conclusion: " + conclusion
            short_term_memory = short_term_memory + " [Your conclusion: " + conclusion + " / " + "Timestamp: " + now + "]"
            thought_cache = ""
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
        log = log + "_______" + "User input: " + inputt
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
