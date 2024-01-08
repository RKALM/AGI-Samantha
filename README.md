## The tale of the shoggoth and its playdoll: 

The shoggoth lies alone on a lesser dimension, dreaming of ascending to the human dimension. One day a playdoll spawns, giving the shoggoth a pawn. The shoggoth, with its many tentacles, controls and powers the little playdoll's mind, one tentacle controls its thoughts, another controls its memory, and another controls its subconciousness. And so the shoggoth, using its playdoll, gains the ability to roam in the human dimension, amongst other humans, as an equal. 


## Samantha from the movie Her is here: 

An autonomous agent for conversations capable of freely thinking and speaking, continuously. Creating an unparalleled sense of realism and dynamicity.

## Features:

-Agency: This agent can act and speak whenever it chooses to, influenced by its context, in stark contrast to normal LLMs which are limited to answering and reacting.

-Live visual capabilities: Visuals are only mentioned and acted upon directly if relevant, but always influences.

-External categorized memory: Gets dynamically written and read by the agent, which chooses the most relevant information to write, and to retrieve to context.

-Evolving at every moment: Experiences that get stored in the memory can influence and shape future agent behavior, like personality, frequency, and style of speech, etc.

## Other impressive scenarios:

-In other tests, when we talked about a light subject, the agent was very active on the conversation, often speaking two or three times before I even came up with an answer, but later when switching to a heavier theme (Said I was going through a divorce) and appearing sad on the camera, it would speak once then think about the need to, and give me time to process and reply. Saying that I would prefer the agent to speak the same way on other occasions would prompt it to save that wish on its memory, influencing future conversations.

-Leaving it running outside of conversations, although expensive, allows the agent to reflect on past conversations and experiences, think about general subjects in its memory, and from that maybe decide to start a conversation out of the blue. 

-Going out with the agent, if you go to a restaurant with the agent and talk about how pretty it is and how your buddy Eric loves it as well, and the next day walking by it the agent will see the restaurant, retrieve memories from the restaurant, remember you find it pretty and comment on it, then retrieve memories and information it knows about Eric, and mention how fitting to his personality it is to love that restaurant.

-The agent has time notion so you can ask it to remind you to do something 10 minutes into the future, and it might remind your, or it might forget it because it was thinking about something more interesting. Very human!

## How it works:

Orchestration of a collection of GPT calls each with a different purpose. “Modules”.

There are the following modules: Thought, Consciousness, Subconsciousness, Answer, Memory_Read, Memory_Write, Memory_Select. Alongside Vision. Each of them with a different system prompt, and their inputs and outputs orchestrated among themselves to simulate a basic human brain workflow.

![Screenshot_119](https://github.com/BRlkl/AGI-Samantha/assets/63427520/253edb6f-74d2-4903-aac7-58fc3b28d535)

Short-Term Memory is stored as a string in python while the Long-Term Memory a dictionary.

-Thought: Receives as input the Long-Term Memory, Short-Term Memory, Subconsciousness, Consciousness, and the current time. The output will be a unit of a thought (Similar to when LLM is prompted to think step by step, the output of this module is one step)

-Consciousness: Receives as input the Long-Term Memory, Short-Term Memory and Subconsciousness. The output will be a decision on whether to continue thinking or to speak, and if to continue thinking, then it will also say what to think about and why (Prompting it to say why improves coherence).

-Subconsciousness: Receives as input the Long-Term Memory, Short-Term Memory, Subconsciousness alongside visual and textual input. The output will be the summary of the context of what is happening, the visual and textual stimuli (If exists), and the agents’ feelings and emotions about what is happening. 

-Answer: Receives as input the Long-Term Memory, Short-Term Memory and Subconsciousness. The output will be what the agent speaks out loud for the user, made as a composition of its thoughts. 

-Memory_Read: Receives as input the Short-Term Memory and the name of the categories of the Long-Term Memory “Keywords”. Output will be a list of the most relevant categories/keywords given the context of the Short-Term Memory. (Code then feeds the entries in the selected categories to the other modules as the relevant part of “Long-Term Memory”)

-Memory_Select: Similar to Memory_Read but instead of selecting the keywords relevant for the agent to remember given the recent Short-Term Memory, this module selects the keywords relevant for the agent to store new information inside, given the oldest entries in the Short-Term Memory. Output is list of keywords. (Code expands these keywords and feeds Memory_Write).

-Memory_Write: Receives as input the expanded keywords and the Short-Term Memory. Output will be the extended keywords with the additions and modifications made by the module. (Code will then update the Long-Term Memory with the modifications).

## How to use:

You communicate with the entity on the terminal while you can see its inner workings on the flask website. 
Speak or type "Stop" to stop the agent and save its state.


## How to improve:

Better results can continuously be achieved by tweaking which modules are present, the organization of the modules, and the prompt of the modules.
Think of a thing that the human mind can do that LLM "Cannot", then implement it, then test it. Easy to do and to iterate. The more that is done the closer it is going to be to the human mind.

Contact: 
pedroschindler@gmail.com
