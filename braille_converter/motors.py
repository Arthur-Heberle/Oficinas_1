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


# ===== Imports ===== #

from flask import Flask, request
import threading
import RPi.GPIO as GPIO
from smbus2 import SMBus
import time,os
from gtts import gTTS
import pygame
from unidecode import unidecode
from docx import Document
import PyPDF2

#-----------------------------------------------#
#                  CONSTANTS                    #
#-----------------------------------------------#

VEL_STEP = 0.10
TIMEMIN = 0.1
TIMEMAX = 3
ANGLE = 45

PIN1 = 18
PIN2 = 23
PIN3 = 24
PIN4 = 25
PIN5 = 12
PIN6 = 13
PINS = [PIN1, PIN2, PIN3, PIN4, PIN5, PIN6]

RAISE_VEL_BUTTON = 27
REDUCE_VEL_BUTTON = 22
PAUSE_BUTTON = 19
REPLAY_WORD_BUTTON = 17
BUTTONS = [RAISE_VEL_BUTTON, REDUCE_VEL_BUTTON,
           PAUSE_BUTTON, REPLAY_WORD_BUTTON ]

# === Potenciometer Constants === #
# I2C_BUS = 1
# ADDRESS = 0x48  # Endereço do ADS1115

# POINTER_CONVERSION = 0x00
# POINTER_CONFIG     = 0x01

#-----------------------------------------------#
#              SETUP CONFIGURATION              #
#-----------------------------------------------#

# # To use interruption in buttons 
# lock = threading.Lock()   
index = 0                 
time_delay = 0.3        
# paused = False
# back_word = False

GPIO.setmode(GPIO.BCM)       
GPIO.setwarnings(False)

for pin in PINS:
    GPIO.setup(pin, GPIO.OUT)

PWMS = [GPIO.PWM(pin, 50) for pin in PINS] 

for button in BUTTONS:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

# To save the text in memory
class AppMemory:
    def __init__(self):
        self.text = None
        self.words = []
memory = AppMemory()

pygame.init()
pygame.mixer.init()


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
        pwm.ChangeDutyCycle(0)
        pwm.stop()
        time.sleep(0.01)

def reset_pwms(ports):
    i = 0
    for p in ports:
        if(p):
            turn(PWMS[i], 0)
        i+=1

def turn(pwm, angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)  # Time to servo motor turn
    pwm.ChangeDutyCycle(0)

def do_braille_letter(ports):
    i = 0
    for p in ports:
        if(p):
            turn(PWMS[i], ANGLE)
        i+=1

#-----------------------------------------------#
#              BUTTONS FUNCTIONS                #
#-----------------------------------------------#

# def check_buttons():
#     while paused:
#         time.sleep(0.1)
#     if back_word:
#         return True
#     else:
#         return False
    
# def pause_callback(channel):
#     global paused
#     print('Paused button clicked')
#     with lock:
#         paused = not paused   
#     print(f'Paused: {paused}')

# def back_word_callback(channel):
#     global index, back_word
#     with lock:
#         back_word = True
#         if index > 0:
#             index -= 1
#             print(f"Playing back word: {memory.words[index]}")
#         else:
#             print("You are in the first word")

# def raise_vel_callback(channel):
#     global time_delay
#     with lock:
#         if time_delay > TIMEMIN:
#             time_delay -= VEL_STEP
#             print(f"Velocity Raised")
#         else:
#             time_delay = TIMEMIN
#             print('Max velocity already!')
#         print(f"Time between words: {time_delay}s")

# def reduce_vel_callback(channel):
#     global time_delay
#     with lock:
#         if time_delay < TIMEMAX:
#             time_delay += VEL_STEP
#             print(f"Velocity Reduced")
#         else:
#             time_delay = TIMEMAX
#             print('Min velocity already!')
#         print(f"Time between words: {time_delay}s")

# # === Configure Interruptions === #
# try: 
#     print("Setting up button interrupts...")
#     GPIO.add_event_detect(REPLAY_WORD_BUTTON, GPIO.FALLING, callback=back_word_callback,  bouncetime=200)
#     GPIO.add_event_detect(RAISE_VEL_BUTTON,   GPIO.FALLING, callback=raise_vel_callback,  bouncetime=200)
#     GPIO.add_event_detect(REDUCE_VEL_BUTTON,  GPIO.FALLING, callback=reduce_vel_callback, bouncetime=200)
#     GPIO.add_event_detect(PAUSE_BUTTON,       GPIO.FALLING, callback=pause_callback,      bouncetime=200)
# except Exception as e:
#     print('Erro when setting up button interrupts ' + str(e))

#-----------------------------------------------#
#                AUDIO FUNCTIONS                #
#-----------------------------------------------#   

def speak_online(txt, folder):
    if(txt == ''):
        return 
    
    txt = clean_word(txt)
    file_path = f"{folder}/output{txt.upper()}.mp3"
    print("Trying to load:", file_path)
    try:

        # volume = get_volume() # (0.0 - 1.0)
        # pygame.mixer.music.set_volume(volume)  # Set volume
        # print(f"Potentiometer volume: {volume:.2f}")

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
                if(carac in word) and carac == word[-1]:
                    word = word.replace(carac, '')

        except Exception as e:
            print(f"Error: {str(e)}")
        
    return word

def create_mp3_words(words, folder):
    for word in words:
        if word and len(word) > 1:
            try:
                tts = gTTS(text=word, lang="pt")
                word = clean_word(word)
                tts.save(f"{folder}/output{word.upper()}.mp3")
            except Exception as e: 
                print(str(e))
                continue

def destroy_mp3_words(words, folder):
    for word in words:
        if word and len(word) > 1:

            word = clean_word(word)
            try:
                os.remove(f"{folder}/output{word.upper()}.mp3")
            except FileNotFoundError:
                print(f"Error: file not found: {folder}/output{word.upper()}.mp3")
            except Exception as e:
                print(f"Error: {str(e)}")

#-----------------------------------------------#
#               BRAILLE FUNCTIONS               #
#-----------------------------------------------#

def translate_to_braille(c):
    return BRAILLE_ALPHA.get(c, [0, 0, 0, 0, 0, 0])

#-----------------------------------------------#
#                 SERVER ROUTES                 #
#-----------------------------------------------#

def extract_text_from_file(file_path, extension):
    if extension == 'txt':
        with open(file_path, 'r') as f:
            return f.read()
    elif extension == 'docx':
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif extension == 'pdf':
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''.join([page.extract_text() for page in reader.pages])
            tmp = ''
            for word in text.split('\n'):
                tmp += word
            text = tmp            
            return text
    return ""

def get_words(text):
    lines = text.split('\n')
    i =0 
    aux = []
    for line in lines:
        aux.append(line.split(' '))
        i+=1
    words = []
    for i in aux:
        for j in i:
            words.append(j)
    return words    

def receive_text():
    try:


        # Save text and words to memory
        memory.words = get_words(extract_text_from_file('meu_arquivo', 'txt'))
        
        # create_mp3_words(memory.words, "words")

        return "Text received", 200
    except Exception as e:
        print(f"Error aa: {str(e)}")
        return "Error", 500

def say_text():
    try:
        # global time_delay, index, back_word, paused
        global time_delay, index
        start_pwms()

        words = memory.words
        size = len(words)

        while index < size:
            back_word = False

            # while paused:
            #     time.sleep(0.1)
            # if back_word:
            #     continue

            # if check_buttons():
            #     continue
            
            word = words[index] 
            # Speak word
            # if(len(word) > 1):
            #     speak_online(word, "words")

            # if check_buttons():
            #     continue
            reset_pwms()
            # Speak each caracter     
            for c in word:

                # if check_buttons():
                #     break


                # if c in BAD_CARACTERS:
                #     speak_online(BAD_CARACTERS[c], 'letters')
                # else:
                #     speak_online(c,'letters')

                braille_letter = translate_to_braille(c) 
                do_braille_letter(braille_letter)
                time.sleep(time_delay)
                reset_pwms()
            
            # if check_buttons():
            #     continue

            index += 1

        return "Runned!", 200
    except KeyboardInterrupt:
        print("Interrupted by user")
        return "Error", 500
    except Exception as e:
        print(f"Error aa: {str(e)}")
        return "Error", 500
    finally:
        print('Cleaning stuff')
        stop_pwms()

    
#=====================================================================================#

if __name__ == '__main__':
    try:
        receive_text(['ola', 'mundo!'])
    except Exception as e:
        print(f"Ocurred an error when trying to run server: {str(e)}")
    finally:
        pygame.quit()
        GPIO.cleanup()



