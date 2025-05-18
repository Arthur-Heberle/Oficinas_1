'''======================================================================='''
#  
#   Project: Edubra - Educador de Braille
# 
#   This file is has to be in the Raspberry Pi 4.
#   It recieve the text sent by app.py and translate
#   each alphabet letter to braille letter. 
#   The file also create a sound file corresponding
#   to each word in the text, so the user can hear it.
#
#   Autor: Arthur Gabriel P. Heberle
#   Email: a.gp.heberle@gmail.com
#
'''-----------------------------------------------------------------------'''


from flask import Flask, request
from gpiozero import MCP3008
import pyttsx3
import RPi.GPIO as GPIO
import time,os
from gtts import gTTS
# from playsound import playsound
import pygame
from unidecode import unidecode

#-----------------------------------------------#
#                  CONSTANTS                    #
#-----------------------------------------------#

VELPAR = 0.15
VELMIN = 0.3
VELMAX = 2
ANGLE = 20
SLEEP_DURATION = 0.3

PIN1 = 18
PIN2 = 23
PIN3 = 24
PIN4 = 25
PIN5 = 12
PIN6 = 13
PINS = [PIN1, PIN2, PIN3, PIN4, PIN5, PIN6]

BUTTON_RAISE_VEL = 3
BUTTON_REDUCE_VEL = 2
BUTTON_PAUSE = 17
BUTTON_REPLAY_WORD = 4
BUTTONS = [BUTTON_RAISE_VEL, BUTTON_REDUCE_VEL,
           BUTTON_PAUSE, BUTTON_REPLAY_WORD ]

#-----------------------------------------------#
#              SETUP CONFIGURATION              #
#-----------------------------------------------#

GPIO.setmode(GPIO.BCM)       
GPIO.setwarnings(False)

for pin in PINS:
    GPIO.setup(pin, GPIO.OUT)

PWMS = [GPIO.PWM(pin, 50) for pin in PINS]  # Create PWM instance with 50Hz (typical for servos)

for button in BUTTONS:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pot = MCP3008(channel=0) # Responsible to convert potenciometer signal

BRAILLE_ALPHA = {
    'a': [1 , 0,
          0 , 0,
          0 , 0],

    'b': [1 , 0,
          1 , 0,
          0 , 0],

    'c': [1 , 1,
          0 , 0,
          0 , 0],

    'd': [1 , 1,
          0 , 1,
          0 , 0],

    'e': [1 , 0,
          0 , 1,
          0 , 0],

    'f': [1 , 1,
          1 , 0,
          0 , 0],

    'g': [1 , 1,
          1 , 1,
          0 , 0],

    'h': [1 , 0,
          1 , 1,
          0 , 0],

    'i': [0 , 1,
          1 , 0,
          0 , 0],

    'j': [0 , 1,
          1 , 1,
          0 , 0],

    'k': [1 , 0,
          0 , 0,
          1 , 0],

    'l': [1 , 0,
          1 , 0,
          1 , 0],

    'm': [1 , 1,
          0 , 0,
          1 , 0],

    'n': [1 , 1,
          0 , 1,
          1 , 0],

    'o': [1 , 0,
          0 , 1,
          1 , 0],

    'p': [1 , 1,
          1 , 0,
          1 , 0],

    'q': [1 , 1,
          1 , 1,
          1 , 0],

    'r': [1 , 0,
          1 , 1,
          1 , 0],

    's': [0 , 1,
          1 , 0,
          1 , 0],

    't': [0 , 1,
          1 , 1,
          1 , 0],

    'u': [1 , 0,
          0 , 0,
          1 , 1],

    'v': [1 , 0,
          1 , 0,
          1 , 1],

    'w': [0 , 1,
          1 , 1,
          0 , 1],

    'x': [1 , 1,
          0 , 0,
          1 , 1],

    'y': [1 , 1,
          0 , 1,
          1 , 1],

    'z': [1 , 0,
          0 , 1,
          1 , 1],
    
    '0': [0 , 1,
          0 , 1,
          1 , 1],
        
    '1': [1 , 0,
          0 , 0,
          0 , 1],
        
    '2': [1 , 0,
          1 , 0,
          0 , 1],
        
    '3': [1 , 1,
          0 , 0,
          0 , 1],
        
    '4': [1 , 1,
          0 , 1,
          0 , 1],
        
    '5': [1 , 0,
          0 , 1,
          0 , 1],
        
    '6': [1 , 1,
          1 , 0,
          0 , 1],
        
    '7': [1 , 1,
          1 , 1,
          0 , 1],
        
    '8': [1 , 0,
          1 , 1,
          0 , 1],
        
    '9': [0 , 1,
          1 , 0,
          0 , 1],
    
    '.': [0 , 0,
          1 , 1, 
          0 , 1],

    ',': [0 , 0,
          1 , 0,
          0 , 0],

    '?': [0 , 0,
          1 , 0,
          1 , 1],
    
    '!': [0 , 0,
          1 , 1,
          1 , 0],

    '+': [0 , 0,
          1 , 1,
          1 , 0],

    '#': [0 , 1,
          0 , 1,
          1 , 1],
    
    ';': [0 , 0,
          1 , 0,
          1 , 0],
    
    ':': [0 , 0,
          1 , 1,
          0 , 0],
    
    '-': [0 , 0,
          0 , 0,
          1 , 1],
    
    '"': [0 , 0,  #
          0 , 0,  #  PARA NAO DAR BO
          1 , 0], #
    
    '(': [0 , 0,
          1 , 1,
          1 , 1],
    
    ')': [0 , 0,
          1 , 1,
          1 , 1],

    '[': [0 , 0,
          1 , 1,
          1 , 1],
    
    ']': [0 , 0,
          1 , 1,
          1 , 1],
    
    '/': [0 , 1,
          0 , 0,
          1 , 0],
    
    ' ': [0 , 0,
          0 , 0,
          0 , 0],
    
    "'": [0 , 0,
          0 , 0,
          1 , 0],
        
    "@": [0 , 1,
          0 , 1,
          1 , 0],
        
    '<': [1 , 0,
          1 , 0,
          0 , 1],
                  
    '>': [0 , 1,
          0 , 1,
          1 , 0],
            
    '_': [0 , 0,
          0 , 0,
          1 , 1],
                  
    '*': [0 , 0,
          0 , 1,
          1 , 0],
}

BAD_CARACTERS = {
                ':': 'DOIS PONTOS', '\\' : 'BARRA', '*' : 'ASTERISCO', '/' : 'BARRA', "'": 'ASPAS SIMPLES',
                '"' : 'ASPAS DUPLAS', ',': 'VIRRGULA', ';' : 'PONTO E VIRGULA', '.' : 'PONTO', '(' : 'ABRE PARENTES', ')' : 'FECHA PARENTES', '[' : 'ABRE CHAVES', ']': 'FECHA CHAVES', '?' : 'PONTO DE INTERROGAÇÃO', '!' : 'PONTO DE EXCLAMAÇÃO', '<' : 'MENOR QUE', '>': 'MAIOR QUE', '{':'ABRE COLCHETES', '}': 'FECHA COLCHETES'}

#-----------------------------------------------#
#                INTRODUCTION                   #
#-----------------------------------------------#

app = Flask(__name__)

class AppMemory:
    def __init__(self):
        self.text = None
        self.words = []
memory = AppMemory()

#-----------------------------------------------#
#               PINS FUNCTIONS                  #
#-----------------------------------------------#

def start_pwms():
    for pwm in PWMS:
        pwm.start(0)
        time.sleep(0.01)
    reset_pwms()

def stop_pwms():
    for pwm in PWMS:
        pwm.stop()
        time.sleep(0.01)

def reset_pwms():
    for pwm in PWMS:
        turn (pwm,0)
        time.sleep(0.1)

def turn(pwm, angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    # time.sleep(0.3)  # Time to servo motor turn

def clean_pwm_duty(pwm):  
    pwm.ChangeDutyCycle(0)
    time.sleep(0.1)
    
#-----------------------------------------------#
#                AUDIO FUNCTIONS                #
#-----------------------------------------------#   

def speak_offline(txt):
    # This function is only for tests, 
    # it is actually not used

    engine = pyttsx3.init()
    engine.say(txt)
    engine.runAndWait()

def speak_online(txt,folder):
    if(txt == ''):
        return 
    
    txt = clean_word(txt)
    file_path = f"{folder}/output{txt.upper()}.mp3"
    print("Trying to load:", file_path)
    try:
        volume = pot.value  # Read potentiometer value (0.0 - 1.0)
        pygame.mixer.music.set_volume(volume)  # Set volume
        print(f"Potentiometer volume: {volume:.2f}")

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    except FileNotFoundError:
        print(f"Error: file not found")
    except Exception as e:
        print(f"Error: {str(e)}")

def clean_word(word):
    
    word = word.strip()
    word = unidecode(word)

    if(len(word)>1):
        try:    
            for carac in BAD_CARACTERS:
                if(carac in word):
                    if(carac == word[-1]):
                        word = word.replace(carac, '')
        except Exception as e:
            print(f"Error: {str(e)}")
        
    return word

def create_mp3_words(words, folder):
    for word in words:
        if( len(word) > 1):
            if not word:
                continue
           
            try:
                tts = gTTS(text=word, lang="pt")
                word = clean_word(word)
                tts.save(f"{folder}/output{word.upper()}.mp3")
            except Exception as e: 
                print(str(e))
                continue

def destroy_mp3_words(words, folder):
    for word in words:
        if( len(word) > 1):
            if not word:
                continue

            word = clean_word(word)
            try:
                os.remove(f"{folder}/output{word.upper()}.mp3")
            except FileNotFoundError:
                print(f"Error: file not found: {folder}/output{word.upper()}.mp3")
            except Exception as e:
                print(f"Error: {str(e)}")


#-----------------------------------------------#
#              BUTTONS FUNCTIONS                #
#-----------------------------------------------#

def buttons_response(time, i):
    step = 0.05
    elapsed = 0
    clicked = False
    response = [time, i, False]
    while elapsed < SLEEP_DURATION and not clicked:
        time.sleep(step)
        response = verify_buttons(time)
        clicked = response[2]
        elapsed += step

    # time = response[0]
    # i = response[1]
    # return [time, i]

    return [response[0],response[1]]

def verify_buttons(time, i):
    clicked = True
    if GPIO.input(BUTTON_PAUSE) == GPIO.HIGH:
        pause()
    elif GPIO.input(BUTTON_RAISE_VEL) == GPIO.HIGH:
        time = raise_vel(time)
    elif GPIO.input(BUTTON_REDUCE_VEL) == GPIO.HIGH:
        time = reduce_vel(time)
    elif GPIO.input(BUTTON_REPLAY_WORD) == GPIO.HIGH:
        i -=2
    else:
        clicked = False

    return [time,i,clicked]

def raise_vel(time):
    if time - VELPAR > VELMIN:
        return time - VELPAR
    return VELMIN

def reduce_vel(time):
    if time + VELPAR < VELMAX:
        return time + VELPAR
    return VELMAX

def pause():
    time.sleep(0.5)
    on = True
    while on:
        if GPIO.input(BUTTON_PAUSE) == GPIO.HIGH:
            on = False

#-----------------------------------------------#
#               BRAILLE FUNCTIONS               #
#-----------------------------------------------#

def words_to_braille(words):
    # Used only if you want to translate the words to braille
    # (not used in this file)
    ports = []
    for word in words:
        for letter in word:
            ports.append(translate_to_braille(letter))
        ports.append([0,0,0,0,0,0])
    
    return ports

def translate_to_braille(c):
    return BRAILLE_ALPHA.get(c, [0, 0, 0, 0, 0, 0])

def do_braille_letter(ports):
    i = 0
    for p in ports:
        if(p):
            turn(PWMS[i], ANGLE)
        i+=1

    time.sleep(0.3)  # Time to servo motor turn
    i = 0
    for p in ports:
        if(p):
            clean_pwm_duty(PWMS[i])
        i+=1

#-----------------------------------------------#
#                 SERVER ROUTES                 #
#-----------------------------------------------#

@app.route('/receive-text', methods=['POST'])
def receive_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        words = data.get('words', '')
        print(f"Received text: {text}\n")
        print(f'Recieved words: {words}\n')

        # Save text and words
        memory.text = text
        memory.words = words
        
        create_mp3_words(words, "words")

        return "Text received", 200
    except Exception as e:
        print(f"Error aa: {str(e)}")
        return "Error", 500

@app.route('/run-text', methods=['POST'])
def say_text():
    try:
        pygame.mixer.init()
        start_pwms()

        data = request.get_json()
        t = data.get('time', 1) # Get the time between letters

        words = memory.words
        size = len(words)

        for i in range(0, size):
            
            word = words[i] 

            if(len(word) > 1):
                speak_online(word, "words")
                        
            for c in word:
                reset_pwms()

                if c in BAD_CARACTERS:
                    speak_online(BAD_CARACTERS[c], "letters")
                else:
                    speak_online(c, 'letters')

                braille_letter = translate_to_braille(c) 
                do_braille_letter(braille_letter)
                time.sleep(t)

                # response = buttons_response(t, i) # Check buttons
                # t = response[0]
                # if response[1] < i: # 
                #    i = response[1]
                #    break
                

        return "Runned!", 200
    except Exception as e:
        print(f"Error aa: {str(e)}")
        return "Error", 500
    finally:
        print('Cleaning stuff')
        pygame.quit()
        stop_pwms()
        GPIO.cleanup()
        destroy_mp3_words(memory.words, 'words')
    
#=====================================================================================#

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Ensure port matches PI_PORT in app.py
