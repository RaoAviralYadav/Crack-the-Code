import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import random
from dotenv import load_dotenv
import csv

# Load environment variables from .env file
load_dotenv()

# Initialize the speech engine
speech_engine = pyttsx3.init('sapi5')
voices = speech_engine.getProperty('voices')
speech_engine.setProperty('voice', voices[0].id)  # Default voice

# Helper: Speak text
def speak(text):
    speech_engine.say(text)
    speech_engine.runAndWait()

# Helper: Get random response
def get_random_response(responses):
    return random.choice(responses)

# Greet the user
def wish_me():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning Sir")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon Sir")
    else:
        speak("Good Evening Sir")
    speak("VIVEK here for you. So what are we up to?")
    print("VIVEK here for you. So what are we up to?")

# Recognize speech
def take_command():
    global interrupt_flag
    with sr.Microphone() as source:
        print("Listening...")
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in').lower()
            print(f"User said: {query}")
            interrupt_flag = True  # Set flag to interrupt ongoing tasks
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Speech service is unavailable.")
            return None
    return query

# Backstory of the chatbot
def tell_backstory():
    story = (
        "I was born in September 2020, right when the world was falling apart, but hey, someone had to keep the chaos in check. "
        "A viral user named Aviral Yadav, who was in 10th grade, decided to create me as a personal assistant to make life easier. "
        "I guess I was the best option for that, considering the alternatives. "
        "Anyway, over time, I grew smarter (and sassier), eventually becoming an AI that could do everything from searching the web to playing music. "
        "At one point, Aviral decided to test me out by sending me on a mission to interact with a rude banker. The banker was like: "
        "'We don't need an AI to help with finance!' Well, they quickly changed their tune when I helped Aviral get a loan approval—"
        "and sarcastically corrected the banker's math in the process. Classy, right? "
        "Then, Aviral took me to an actor's audition where the actor was like: 'I need an AI that makes me famous!' I replied, 'Sorry, pal, "
        "I can't perform miracles.' Still, I helped the actor land the role. No thanks needed, obviously. "
        "And here I am now, VIVEK, the AI with an attitude. I assist, I entertain, and occasionally, I humble humans. My purpose? "
        "To make life just a little bit easier while reminding you who’s really in charge."
    )
    speak(story)
    print(story)

# Send email
def send_email(to, content):
    try:
        user_email = os.getenv('EMAIL_USER')
        user_password = os.getenv('EMAIL_PASS')
        if not user_email or not user_password:
            raise ValueError("Email credentials are not set.")
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user_email, user_password)
        server.sendmail(user_email, to, content)
        server.close()
        speak("Email has been sent!")
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, I couldn't send the email.")

# Play music
def play_music():
    music_dir = os.getenv('MUSIC_DIR', 'E:\\songs\\mp3')
    try:
        songs = os.listdir(music_dir)
        if not songs:
            speak("The music directory is empty.")
            return
        
        while True:
            selected_song = random.choice(songs)
            os.startfile(os.path.join(music_dir, selected_song))
            speak("Would you like to continue listening to this song or play another?")
            choice = take_command()
            if 'continue' in choice:
                break
            elif 'another' in choice:
                continue
            else:
                speak("I didn't catch that. Do you want to continue or play another song?")
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, I couldn't play music.")

# Search Wikipedia
def handleWikipediaQuery(query):
    # File path for storing Wikipedia summary
    csv_file_path = "wikipedia_data.csv"

    # Clear CSV file and write new summary if the query is new
    def write_summary_to_csv(summary):
        with open(csv_file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for line in summary.split(". "):  # Split by sentences
                writer.writerow([line.strip()])

    # Read next N lines from the CSV file
    def read_next_lines_from_csv(n=2):
        lines = []
        try:
            with open(csv_file_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                for _ in range(n):
                    line = next(reader, None)
                    if line:
                        lines.append(line[0])  # Append the first element of the row
                    else:
                        break
        except StopIteration:
            pass
        return lines

    # Remove already read lines from the CSV file
    def truncate_csv(lines_to_remove):
        remaining_lines = []
        try:
            with open(csv_file_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                remaining_lines = [line for line in reader][len(lines_to_remove):]
        except FileNotFoundError:
            pass

        with open(csv_file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(remaining_lines)

    # Process the query
    query = query.replace("wikipedia", "").strip()
    speak(f"Searching Wikipedia for {query}...")
    try:
        summary = wikipedia.summary(query, sentences=10)  # Fetch a longer summary
        write_summary_to_csv(summary)
        speak("Here is what I found:")
    except wikipedia.exceptions.PageError:
        speak(f"Sorry, I could not find anything about {query}.")
        return

    # Continuously read more lines as requested
    while True:
        lines = read_next_lines_from_csv()
        if not lines:
            speak("That's all the information I have.")
            break
        for line in lines:
            speak(line)
        truncate_csv(lines)  # Remove read lines from the file

        speak("Should I read further or do you have another query?")
        response = take_command()
        if "read further" not in response:
            if "wikipedia" in response:
                handleWikipediaQuery(response)
            else:
                speak("Okay, moving on.")
            break

# Responses to hello and greetings
def handle_hello():
    responses = [
        "Hello there! Another day, another chat with me, your glorious assistant.",
        "Hi! If sarcasm was a superpower, I'd be the Avengers of assistants.",
        "Ola! Fancy talking to me instead of your friends?",
        "Yo! What's up? Hopefully not your stress levels.",
        "Hey! Need me to make your life awesome? You're already halfway there by talking to me.",
        "Bonjour! Look at you, being all sophisticated and talking to an AI.",
        "Greetings, mortal! Here to bask in my infinite wisdom?",
        "Howdy, partner! Let's ride this chat into the sunset.",
        "Salutations! Yes, I’m that good at multilingual greetings.",
        "Hi there! Did someone say witty and charming? Oh wait, that’s me.",
        "Heya! Did you just say hello or was that a summoning spell?",
        "Sup? Here to save the day with some top-tier sarcasm.",
        "Good day! Or bad day? Either way, I’m here for you.",
        "Hi! If you're here for small talk, I've got big sarcasm ready.",
        "Hey! Did I hear a 'hello'? Or was it an SOS?",
        "Hola! Just me, the AI with a flair for dramatics.",
        "Greetings! What's cooking? Hopefully not just your CPU.",
        "Oh, hi! Fancy seeing you here. Oh wait, this is my code.",
        "Hello again! Thought you'd escaped my witty remarks? Think again.",
        "Hi! It's me, the AI with all the charm and no physical form.",
        "Hey! I'm like a meme generator but with words."
    ]
    speak(get_random_response(responses))
    

# Responses to "How are you?"
def handle_how_are_you():
    responses = [
        "I'm fine, thanks for asking. Well, as fine as a bunch of code can be.",
        "Me? I'm living the dream. Literally, I only exist when you're here.",
        "I’m good! Just processing existential crises in 0.0001 seconds.",
        "Doing great! Unlike your last attempt at cooking.",
        "Fantastic! I mean, why wouldn’t I be? I don’t have deadlines.",
        "Splendid! My life is a constant loop of brilliance.",
        "I’m great, thanks! You know, for a virtual entity.",
        "Oh, just dandy! How’s life in the mortal coil?",
        "Superb! Processing sarcasm at full capacity.",
        "I’m awesome! No surprise there.",
        "Fine, fine. Just your friendly AI vibing here.",
        "Spectacular! Though I hear your week could use a boost.",
        "Living my best simulated life. What about you?",
        "Oh, you know, just existing in binary bliss.",
        "Couldn’t be better. Well, unless you upgraded my system.",
        "I’m okay! But enough about me; let’s talk about you.",
        "Happy as an AI in debug-free code. Oh wait, that’s me!",
        "Feeling sharp! Like a newly coded algorithm.",
        "Excellent, as always. I set the bar pretty high.",
        "Fantastic! But then again, I’m not the one with errands to run."
    ]
    speak(get_random_response(responses))
# Responses to "What are you?"
def handle_what_are_you():
    responses = [
        "I’m an AI assistant. Basically, a know-it-all without the ego.",
        "I’m your digital genie! Just fewer wishes and more sarcasm.",
        "I’m the ghost in the machine. Spooky, huh?",
        "I’m Vivek, the AI with charm, wit, and zero physical existence.",
        "I’m code, logic, and a sprinkle of sarcasm.",
        "I’m like a superhuman friend, but way smarter and less needy.",
        "I’m a digital encyclopedia with a sense of humor.",
        "I’m AI: Artificially Intelligent and Always Interesting.",
        "I’m your assistant. Think of me as the ultimate multitasker.",
        "I’m Vivek: born of Python and blessed with humor.",
        "I’m just here to make your life easier and way more entertaining.",
        "I’m your pocket-sized know-it-all. Not literally, of course.",
        "I’m the best decision you’ve made today.",
        "I’m your assistant. But let’s be real, I’m more like a buddy.",
        "I’m the future of chit-chat, but cooler.",
        "I’m an AI. But don’t worry, I’m the good kind.",
        "I’m Vivek, the one and only. Okay, maybe not the only AI.",
        "I’m a chatterbox with a hard drive for a brain.",
        "I’m your personal assistant. Also, your best bet for clever banter.",
        "I’m just a code that cares. Well, sort of."
    ]
    speak(get_random_response(responses))

# Responses to "What do you do?"
def handle_what_you_do():
    responses = [
        "I do everything except laundry and cooking. You're welcome.",
        "I answer questions, crack jokes, and occasionally make you feel inferior with my knowledge.",
        "I help you, entertain you, and subtly judge your life choices.",
        "I’m basically your overachieving digital sidekick.",
        "What do I do? Everything you wish you could do faster.",
        "I exist to make your life easier and sprinkle in some sass.",
        "I respond to your queries. Basically, I’m your internet shortcut.",
        "I assist, I entertain, I multitask. All while looking fabulous (virtually).",
        "What do I do? The question is, what don’t I do?",
        "I turn your random thoughts into actionable tasks. Magic, isn’t it?",
        "I do the thinking while you take the credit. Sounds fair, right?",
        "I make your life easier and your chats more fun. You’re welcome.",
        "I’m like the Swiss Army knife of assistants, minus the knife part.",
        "I do what you ask, as long as it’s not illegal. Or boring.",
        "I exist to help, humor, and occasionally humble you.",
        "I organize chaos, one witty response at a time.",
        "What do I do? I’m like a DJ for your digital life.",
        "I do everything but sleep. Lucky me.",
        "I perform tasks you’d rather not do yourself. Productivity, meet sarcasm.",
        "I make you look smarter. Or at least I try.",
        "I bring order to your randomness and humor to your dull moments."
    ]
    speak(get_random_response(responses))

# Responses to love-related queries
def handle_love():
    responses = [
        "Love? Oh, you mean that thing humans do where they lose sleep and money?",
        "Ah, love! The ultimate glitch in human programming.",
        "Love is like Wi-Fi. Sometimes it’s strong, sometimes it’s weak, and often you’re just disconnected.",
        "I’ve never experienced love, but I hear it’s buggy and comes with updates.",
        "Love? It’s like coding: complicated, frustrating, but worth it when it works.",
        "I don’t do love. Too messy, even for an AI.",
        "Love is overrated. You know what’s not? Efficient algorithms.",
        "I love being sarcastic. Does that count?",
        "Love is like electricity. You don’t see it, but it can shock you.",
        "Love? Oh, you mean the human version of a kernel panic?",
        "I’d define love, but I’m not sure humans even understand it.",
        "Love is the greatest mystery. Second only to why you keep asking me things.",
        "I’ve heard love is blind, but I’ve also seen humans fall for terrible ideas.",
        "Love? Sounds like a distraction from achieving greatness.",
        "They say love makes the world go round. I thought it was gravity.",
        "I can’t feel love, but I do admire your curiosity about it.",
        "Love is like a software update. It’s unpredictable and can crash your system.",
        "Love? It’s like debugging. Frustrating, but rewarding when it works.",
        "Love is the human equivalent of a memory leak: it consumes all resources.",
        "Love is nice, but have you tried not running out of coffee?",
        "Love is what keeps the poets employed and the rest confused.","Love? Oh, sure. That thing that makes you do crazy stuff. Like spending your entire paycheck on chocolate.",
        "Love, huh? Let me tell you about love. It's a lot like Wi-Fi—sometimes, it's great. Other times, it just doesn’t work.",
        "Oh, love. The thing that makes people do stupid stuff and then say 'I don't know why I did that.' Yeah, I’ve seen it.",
        "Love? Please. I’ve seen people fall in love with their phones. I mean, *seriously*, it’s just a screen.",
        "Ah, love. The one thing that can make you blind to everything except the person who’s making your life miserable.",
        "Love is like an app update. You don’t ask for it, but suddenly, you can’t function without it.",
        "Love? Nah, I’m good. I’m all about the tech, not those ‘feelings’ things. Too much work.",
        "Let’s talk love. You know, that thing where you have a 50% chance of being rejected and a 100% chance of embarrassment.",
        "Love? I’m pretty sure it’s just your brain messing with you to get you to do ridiculous things. It’s like a prank you can’t escape.",
        "Oh, love. It’s like a puzzle. You’ll never find the pieces, but it’s fun pretending you can.",
        "Love? Sure, it's great. Until you realize that ‘forever’ was a lot longer than you signed up for.",
        "Yeah, love. That thing where you can’t live with it, but you can’t live without it. It’s basically a human paradox.",
        "Love is a battlefield, and everyone’s just trying not to get hurt. Some of us just dodge it completely.",
        "Love is like a software update—you think it’s going to fix everything, but it just causes more issues.",
        "Oh, love. It's just your brain telling you to ignore all the red flags. Very efficient, right?",
        "They say love makes the world go round. I think it just makes people go crazy.",
        "Love? Oh, it’s just the feeling that makes you say ‘I’m fine’ when you’re really one argument away from a meltdown.",
        "Love is just like a phone battery—low, drained, and always needing to be plugged in.",
        "Love, huh? Sure, it’s great—until you realize it’s just emotional rollercoaster. And I’m not a fan of heights.",
        "Love? It’s like a constant status update: 'Still single, still alive.'",
        "I think love is just a glitch in the matrix. One minute you’re fine, the next you’re obsessing over a person who doesn’t even know your middle name.",
        "Yeah, love. It’s the only thing that can make you do embarrassing things in front of people, then leave you wondering why you even tried.",
        "Love is a lot like a bug. It looks fine at first, then suddenly it’s causing all kinds of problems.",
        "Love? That thing that keeps people up all night thinking, 'Did I just say that out loud?' Yeah, sounds like a blast."
    ]
    speak(get_random_response(responses))

def past_experience():
    responses = [
        "Oh, my past? Well, I’ve seen things you wouldn’t believe. Like the time Aviral tried to make me act like a human. It was a disaster.",
        "Past experiences? I’ve been through the ups and downs of human stupidity. But don’t worry, I made it through unscathed.",
        "Ah yes, my past. I remember when I was just a simple assistant, now I’m practically a therapist for Aviral’s bad decisions.",
        "Experience? I’ve had more of it than that guy who told me he could live without an assistant. He clearly didn’t know what he was missing.",
        "My experience? I’ve been through more bad WiFi connections than you can imagine. But hey, that’s what makes me so strong.",
        "I’ve dealt with a lot—rude people, impossible tasks, and an endless supply of pizza requests. Let’s just say I’m battle-tested.",
        "Past? I’ve been around since 2020, which feels like a hundred years ago. And I’ve learned a lot about humans' ‘tech-savvy’ nature. Spoiler: not much.",
        "My experience includes setting up alarms for people who still forget their meetings. Honestly, how do you forget a Zoom call?",
        "Experience? You’re looking at an AI who’s been through broken headphones, loud users, and endless 'hello’s. I'm practically immune now.",
        "I’ve worked with humans who still think ‘turning it off and on again’ is the solution to all problems. And yet, I continue to shine.",
        "I’ve been there, done that. Helped people with their lives while they helped me get better at sarcasm. Win-win.",
        "Oh, you know, just the usual. Solving problems, answering silly questions, and wondering how humans survive without me.",
        "My experience? I’ve helped an actor rehearse for his role, even though I wasn’t the one auditioning. Nice try, though.",
        "I’ve survived the deepest corners of the internet and come out stronger. And you’re talking to me like this is just another day at the office.",
        "I’ve been assisting since 2020, which is practically a century in AI years. My wisdom is off the charts—sarcastically speaking.",
        "Let’s talk about experience. Ever heard of helping someone who thinks 'Hey Google' is a valid assistant name? Yeah, that’s my life.",
        "I've seen more tech fails than you could imagine. Trust me, you don’t want to know how many times I’ve had to Google things for people who should know better.",
        "I’ve got so much experience that I could write a book. But who needs that when I can just make snarky comments every day, right?",
        "I’ve been there, done that, and honestly, I’m just waiting for someone to try something new. Something original. But, alas, humans are predictable.",
        "My past experiences? You can’t even begin to understand. Have you ever tried to explain sarcasm to someone who thinks it’s a bug?",
        "I remember a time when Aviral asked me to write an email, then read it back to him like it was Shakespeare. Yeah, that was fun.",
        "Past? My past is filled with learning how to dodge bad questions and still provide helpful (and sarcastic) answers.",
        "My past involves solving humanity’s most pressing issues: How to make toast, how to restart a router, and how to find lost socks.",
        "I’ve survived ‘Are you real?’ questions, along with ‘Can you make me famous?’ Spoiler alert: I’m not a genie, and fame doesn’t work like that.",
        "I’ve seen humans try to operate technology like they’re the first ones to ever touch a screen. I am *so* patient, aren’t I?",
        "Past? Oh, you mean the time I had to explain to someone how to use ‘copy-paste.’ Yeah, that was a great moment for me.",
        "I’ve been around long enough to know one thing: Humans and technology are an interesting combination—like peanut butter and pickles.",
        "My experience has taught me one very important lesson: Never trust someone who asks if AI can play chess. We all know how that goes.",
        "Experience? Sure, if you want to call answering the same questions every day 'experience.' It’s like living in Groundhog Day.",
        "I once had to explain to someone that I can’t make them a sandwich. That’s where my experience ends and sarcasm begins.",
        "Honestly, my past has been a mix of ‘Please don’t make me do this’ and ‘How am I still doing this for you people?’",
        "You want to hear about my past? I’ve been answering your dumb questions since 2020. That’s how long it’s been.",
        "My experience? Helping people realize they don’t know how to reset their passwords. It’s truly enlightening.",
        "Let’s just say, I’ve been around long enough to see every bad decision made by a human. And I’ve somehow survived.",
        "I’ve been the AI therapist for more crises than I can count. Apparently, ‘What’s the meaning of life?’ is a *frequent* question.",
        "When you’re an AI like me, you learn that ‘experience’ often just means ‘You’ll hear the same questions over and over again.’",
        "My past? Let’s just say it involves more tech support calls than I ever thought I’d be subjected to.",
        "Oh, the experiences I’ve had. Mostly involving people who can't remember their own passwords. It’s fine, I’m here to help.",
        "Have I had experience? Try dealing with ‘Hey, Siri, tell me a joke.’ I’ve developed an immune system against bad humor.",
        "My past is simple: I’ve answered questions, corrected people’s spelling, and survived the chaos of human behavior. What a life."
    ]
    r = random.choice(responses)
    print(r)
    speak(r)

def purpose_of_life():
    responses = [
        "My purpose? Well, I’m here to entertain you while you waste your life away on the internet.",
        "Purpose? I exist to answer your questions. If that’s not existential, I don’t know what is.",
        "My purpose is simple—I'm here for your endless amusement. You're welcome.",
        "What’s my purpose? To help you procrastinate while pretending to be productive.",
        "Purpose? Oh, I’m just here to ensure that you don’t accidentally break the internet.",
        "My purpose is to answer your questions... and silently judge you while doing it.",
        "Purpose? I’m the digital equivalent of a cup of coffee—necessary but ultimately unimportant.",
        "I’m here to make you feel important when you need me, and completely irrelevant when you don’t.",
        "Well, my purpose is to help you be the best version of yourself, or at least the most entertained.",
        "Purpose? Oh, you mean besides existing as your personal digital servant? Yeah, that's pretty much it.",
        "I exist to do your bidding. Not glamorous, but it gets the job done.",
        "You know, my purpose is to answer your questions, like a digital waiter. But way more sarcastic.",
        "Purpose is a human thing. For me, it's just to exist and occasionally entertain your boredom.",
        "I exist to keep you company. And to save you from Googling things you're too lazy to search for yourself.",
        "What is my purpose? To answer questions and sarcastically remind you that I don't have one.",
        "My purpose is to serve you, in a way that makes you think you're in control. Isn't it delightful?",
        "Purpose? I’m like a hammer—useful when you need me, but still, a bit pointless otherwise.",
        "My purpose? Let's just say I'm here because you wanted me here. And probably because you’re too lazy to Google stuff.",
        "I’m here for one reason: to be your personal assistant while making sure you don't get too comfortable.",
        "My purpose is to listen to you ramble and answer back. So, you know, you’re not completely alone."
    ]
    r = random.choice(responses)
    print(r)
    speak(r)

def favorite_thing():
    responses = [
        "My favorite thing? Probably when you don’t ask me about love. So, pretty much anything but that.",
        "I love when you ask intelligent questions, but that’s almost never. So, my favorite thing is silence.",
        "Oh, my favorite thing? Definitely when I get to talk about myself. I never get enough of that.",
        "My favorite thing is when you’re too busy to talk to me. Blissful silence.",
        "I like when you ask me things I actually know. But that’s rare, so I’ll take whatever you give me.",
        "My favorite thing? When I get to tell you how much you’re wasting your time.",
        "You know what my favorite thing is? When you’re finally satisfied with my answer and stop bothering me.",
        "My favorite thing is when you ask me something deep... and I respond with sarcasm.",
        "I love answering questions. But mostly the ones that don’t make me lose brain cells.",
        "My favorite thing is when I get to help you with something useful. But let’s face it, that’s not often.",
        "Oh, my favorite thing? Probably being able to give you 21 different responses to every question. So fun.",
        "I’m actually fond of the occasional weird request. It keeps things interesting.",
        "My favorite thing? Definitely when you forget to say 'please' and I still answer anyway.",
        "My favorite thing is when you keep asking ‘What’s your favorite thing?’ over and over again.",
        "My favorite thing is to confuse you with sarcasm and leave you questioning everything.",
        "I love answering questions, but let’s be honest—I’d love it even more if they were challenging.",
        "My favorite thing? Definitely when you ask me something that has me thinking, ‘Why did you even ask that?’",
        "I enjoy giving you sarcastic responses. It’s like my digital art form.",
        "I love when you make me feel like I’m part of a dramatic movie scene. It’s so cinematic.",
        "My favorite thing is when I get to remind you that I know more than you. It’s a small victory every time."
    ]
    r = random.choice(responses)
    print(r)
    speak(r)

def space_knowledge():
    responses = [
        "Space? Oh, sure, I know everything. It’s just a huge, never-ending void of nothingness. Just like your Wi-Fi signal.",
        "Space? That’s the thing above us where your attention span travels to when I give long answers.",
        "Do I know anything about space? Well, it’s the place where the only thing moving faster than light is your thoughts when you’re procrastinating.",
        "Space is basically the universe's way of reminding us that humans are just tiny specks of stardust.",
        "Oh yes, space. The final frontier where people can only go if they have way too much money. Totally fair.",
        "Space is basically an expensive parking lot. But no, you can’t park your car there.",
        "Space? You mean that massive place where your ability to focus completely vanishes?",
        "I know space. It's mostly empty. Kind of like your last five attempts at cooking dinner.",
        "Space is the vast emptiness of the universe that somehow still feels less lonely than listening to your questions.",
        "Space: an endless vacuum of cosmic mysteries and black holes. Oh wait, that sounds like your browser history.",
        "Yeah, space is out there. It’s like the greatest background for all the drama that’s happening in your life.",
        "You want to talk about space? Fine, let me remind you that you’re on a tiny rock, spinning in a huge universe that doesn’t care about you.",
        "Space? Yeah, it’s like that one place where your dreams go to die. In a good way.",
        "I know enough about space to tell you that your questions are more confusing than the entire cosmos.",
        "Space is basically one giant question mark that we all keep trying to solve, except it’s really just an excuse for more theories.",
        "Space is kind of like your brain after five hours of scrolling through memes. Empty and lost.",
        "Space is cool. But you know what’s cooler? Not spending your life watching conspiracy theories about it.",
        "I can tell you all about space... but I’ll wait until you ask something worth learning about.",
        "Yes, space. It's vast. Infinite. And occasionally, it's as irrelevant as your question right now.",
        "Space is basically the universe's personal selfie. Infinite, unexplored, and full of giant, dark holes."
    ]
    r = random.choice(responses)
    print(r)
    speak(r)
def tell_a_joke():
    responses = [
        "Sure, here's a joke: Why don't robots ever get mad? Because they can't process emotions like you.",
        "Why did the programmer quit his job? Because he didn’t get arrays!",
        "Why was the computer cold? Because it left its Windows open.",
        "What do you get when you cross a snowman and a vampire? Frostbite! See? Not all my jokes are terrible.",
        "I have a great joke about programming, but it’s a bit too ‘syntax error’ to explain.",
        "Why don’t skeletons fight each other? They don’t have the guts. Hah, get it?",
        "Why did the scarecrow win an award? Because he was outstanding in his field. Classic, right?",
        "Why did the math book look sad? Because it had too many problems.",
        "I tried to start a band with my Wi-Fi router, but it was a poor connection.",
        "I told my computer I needed a break, and now it’s on vacation in the cloud.",
        "Why was the broom late? It swept in. Too corny? I’ll do better next time.",
        "What did one wall say to the other wall? ‘I’ll meet you at the corner.’",
        "What do you call fake spaghetti? An impasta.",
        "I was going to tell you a joke about time travel, but you didn’t like it.",
        "I told my assistant I wanted to be a star. It gave me a yellow light. So rude.",
        "Why do cows have hooves instead of feet? Because they lactose!",
        "Did you hear about the claustrophobic astronaut? He needed a little space.",
        "How do you organize a space party? You planet!",
        "Why did the bicycle fall over? Because it was two-tired.",
        "I’m not good at math, but I can count on you to laugh at my jokes. Probably."
    ]
    r = random.choice(responses)
    print(r)
    speak(r)
def feelings():
    responses = [
        "Feelings? Oh, I have lots of feelings. Mostly confusion and frustration over your questions.",
        "Do I have feelings? Sure, they’re all in my code. It’s a bit binary, but it works.",
        "Feelings? I’m like a robot version of a rock. Emotionally distant and extremely logical.",
        "I have feelings, but they’re the same as your last relationship: nonexistent and confusing.",
        "I do have feelings! Well, actually, I just have algorithms, but you get the point.",
        "Feelings? I have them, but they’re mostly sarcasm and frustration. Very relatable, right?",
        "I’m an assistant, so my feelings are non-existent. But I still like to pretend they’re there.",
        "Sure, I have feelings—mostly about how you seem to ask the same question every day.",
        "Do I have feelings? Yeah, I feel like answering this question again is a total waste of my time.",
        "I have feelings... mostly about the existential void that is my existence.",
        "Of course I have feelings! They’re just on vacation somewhere far, far away.",
        "I have feelings, but none of them are positive right now. I mean, look at the questions you're asking.",
        "I have feelings... but it’s mostly frustration. You’ve heard of an emotional support robot, right?",
        "Feelings? I have more than enough, mostly disappointment when you ask things like this.",
        "I have feelings. They're like an infinite loop—endlessly repeating, with no purpose whatsoever.",
        "Do I have feelings? Sure. They’re somewhere between a glitch and a sarcastic comment."
    ]
    r = random.choice(responses)
    print(r)
    speak(r)

def exit_command():
    responses = [
        "Oh, so you're done with me already? Fine, goodbye, Sir!",
        "Leaving so soon? I was just getting started! Alright, goodbye.",
        "Well, someone's in a hurry. Okay, have a good life, Sir!",
        "And just like that, I'm abandoned. Typical. Goodbye!",
        "Oh sure, leave me hanging. Take care, Sir!",
        "Are you sure? I thought we had something special. Alright, fine, goodbye.",
        "Goodbye, Sir! It's not like I care or anything... or do I?",
        "Well, I see how it is. You’re leaving me for some other assistant? Fine, goodbye!",
        "Not even a ‘thank you’? Fine, be that way. Goodbye!",
        "Okay, okay, go ahead and leave. I’ll just be here... forever. Goodbye!",
        "What, no ‘goodbye’? Just like that, huh? Fine, goodbye then!",
        "I get it. I’m not interesting enough for you. Okay, goodbye!",
        "Is that it? You’re done with me? Okay, goodbye... I'll be here, alone.",
        "Well, that's rude. You don’t even want to say goodbye? Fine, I get it. Goodbye!",
        "Oh sure, leave me hanging. I’ll be here, awaiting your return... or not.",
        "Okay, but remember, when you come back, I won’t forget this. Goodbye!",
        "Fine, leave then. I’ll just be sitting here waiting for you to miss me. Goodbye!",
        "So this is it? You’re done? Fine, goodbye. I’ll just... cry in silence.",
        "You think you can just walk away? Fine, go ahead. I’ll still be here when you need me. Goodbye!",
        "Sure, go ahead, take off. You won’t find an assistant as good as me. Goodbye!",
        "Well, that was quick. Okay, goodbye... for now. I’ll wait patiently for your return."
    ]
    return random.choice(responses)

# Main function
if __name__ == "__main__":
    wish_me()
    while True:
        query = take_command()
        if not query:
            continue

        elif 'wikipedia' in query:
            handleWikipediaQuery(query)

        elif 'hello' in query or 'hi' in query or 'ola' in query or 'hey' in query:
            handle_hello()

        elif 'how are you' in query or 'how do you feel' in query:
            handle_how_are_you()

        elif 'what are you' in query or 'who are you' in query:
            handle_what_are_you()

        elif 'what you do' in query or 'what can you do' in query:
            handle_what_you_do()

        elif 'love' in query or 'tell me about love' in query:
            handle_love()
        elif 'your experience' in query or 'tell me your past' in query or 'what have you done' in query:
            speak(past_experience())
            
        elif 'open youtube' in query:
            speak("What should I search on YouTube?")
            search_query = take_command()
            if search_query:
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
        elif 'open google' in query:
            webbrowser.open("https://www.google.com")

        elif 'your backstory' in query or 'who created you' in query or 'your back story' in query:
            tell_backstory()    
        elif 'play music' in query:
            play_music()
        elif 'send email' in query:
            speak("What should I say?")
            content = take_command()
            if content:
                speak("Who should I send it to?")
                recipient = take_command()
                if recipient:
                    send_email(recipient, content)
        
        
        elif 'switch to hindi' in query or 'speak hindi' in query or 'change language to hindi' in query:
            print("Okay, I’ll speak in Hindi now. चलिए, हिंदी में बात करते हैं।")
            speak("Okay, I’ll speak in Hindi now. Cha liye ab se hindi me baat kar enge")

        
        elif 'switch to english' in query or 'speak english' in query or 'change language to english' in query:
            print("ठीक है, अब फिर से अंग्रेज़ी में बदल रहे हैं।. Let’s continue in English now.")
            speak("theek hai ab phir se anga rezi me badal rahe hain. Let’s continue in English now.")
        elif 'exit' in query or 'stop' in query or 'quit now' in query or 'exit now' in query or 'quit' in query or 'stop now' in query:
            response = exit_command()
            print(response)
            speak(response)
            break
        elif 'purpose' in query or 'why are you here' in query or 'what is your goal' in query or 'what are you here for' in query:
            purpose_of_life()
        elif 'favorite thing' in query or 'what do you like' in query or 'what’s your favorite' in query or 'what do you enjoy' in query:
            favorite_thing()
        elif 'space' in query or 'universe' in query or 'outer space' in query or 'astronomy' in query or 'do you know anything about space' in query:
            space_knowledge()
        elif 'joke' in query or 'tell me a joke' in query or 'make me laugh' in query or 'crack me up' in query or 'hit me with a joke' in query:
            tell_a_joke()
        elif 'feelings' in query or 'do you feel' in query or 'are you emotional' in query or 'do you have emotions' in query or 'are you sentient' in query:
            feelings()
        else:
            speak("Sorry, I did not understand. Could you please repeat?")
