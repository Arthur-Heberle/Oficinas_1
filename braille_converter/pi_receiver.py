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

#-----------------------------------------------#
#                  CONSTANTS                    #
#-----------------------------------------------#

VEL_STEP = 0.05
TIMEMIN = 0.00
TIMEMAX = 3
ANGLE1 = 10
ANGLE2 = 10
ANGLE3 = 10
ANGLE4 = 10
ANGLE5 = 10
ANGLE6 = 10
    
PIN1 = 18
PIN2 = 23
PIN3 = 14
PIN4 = 1
PIN5 = 12
PIN6 = 21

PINS = [PIN1, PIN2, PIN3, PIN4, PIN5, PIN6]

RAISE_VEL_BUTTON = 22
REDUCE_VEL_BUTTON = 17
PAUSE_BUTTON = 19
REPLAY_WORD_BUTTON = 27
BUTTONS = [RAISE_VEL_BUTTON, REDUCE_VEL_BUTTON,
           PAUSE_BUTTON, REPLAY_WORD_BUTTON ]

# === Potenciometer Constants === #
I2C_BUS = 1
ADDRESS = 0x48  # Endereço do ADS1115

POINTER_CONVERSION = 0x00
POINTER_CONFIG     = 0x01

#-----------------------------------------------#
#              SETUP CONFIGURATION              #
#-----------------------------------------------#

# To use interruption in buttons 
lock = threading.Lock()   
index = 0                 
time_delay = 0.5        
paused = False
back_word = False

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
          0 , 0],
        
    '2': [1 , 0,
          1 , 0,
          0 , 0],
        
    '3': [1 , 1,
          0 , 0,
          0 , 0],
        
    '4': [1 , 1,
          0 , 1,
          0 , 0],
        
    '5': [1 , 0,
          0 , 1,
          0 , 0],
        
    '6': [1 , 1,
          1 , 0,
          0 , 0],
        
    '7': [1 , 1,
          1 , 1,
          0 , 0],
        
    '8': [1 , 0,
          1 , 1,
          0 , 0],
        
    '9': [0 , 1,
          1 , 0,
          0 , 0],
    
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

NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

BEFORE_NUMBER = [0 , 1,
                 0 , 1,
                 1 , 1],

BEFORE_UPPER = [0 , 1,
                0 , 0,
                0 , 1],

#-----------------------------------------------#
#                INTRODUCTION                   #
#-----------------------------------------------#

app = Flask(__name__)

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
        turn(pwm, 0)

def stop_pwms():
    for pwm in PWMS:
        pwm.ChangeDutyCycle(0)
        pwm.stop()
        time.sleep(0.01)

def reset_pwms():
    for pwm in PWMS:
        turn (pwm,0)

def turn(pwm, angle):
    duty = 2.5 + (angle / 18.0)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.2)  # Time to servo motor turn
    pwm.ChangeDutyCycle(0)

def do_braille_letter(ports):
    i = 0
    for p in ports:
        if i % 2 == 0:
            print(f"[ {p} , ", end = "" )
        if i % 2 == 1:
            print(f"{p} ]\n")     
        if(p):
            match i:
                case 0:
                    turn(PWMS[i], ANGLE1)
                case 1:
                    turn(PWMS[i], ANGLE2)
                case 2:
                    turn(PWMS[i], ANGLE3)
                case 3:
                    turn(PWMS[i], ANGLE4)
                case 4:
                    turn(PWMS[i], ANGLE5)
                case 5:
                    turn(PWMS[i], ANGLE6)
            
        i+=1

#-----------------------------------------------#
#              BUTTONS FUNCTIONS                #
#-----------------------------------------------#

def check_buttons():
    while paused:
        time.sleep(0.1)
    if back_word:
        return True
    else:
        return False
    
def pause_callback(channel):
    global paused
    print('Paused button clicked')
    with lock:
        paused = not paused   
    print(f'Paused: {paused}')

def back_word_callback(channel):
    global index, back_word
    with lock:
        back_word = True
        if index > 0:
            index -= 1
            print(f"Playing back word: {memory.words[index]}")
        else:
            print("You are in the first word")

def raise_vel_callback(channel):
    global time_delay
    with lock:
        if time_delay - VEL_STEP >= TIMEMIN:
            time_delay -= VEL_STEP
            print(f"Velocity Raised")
        else:
            time_delay = TIMEMIN
            print('Max velocity already!')
        print(f"Time between words: {time_delay}s")

def reduce_vel_callback(channel):
    global time_delay
    with lock:
        if time_delay + VEL_STEP < TIMEMAX:
            time_delay += VEL_STEP
            print(f"Velocity Reduced")
        else:
            time_delay = TIMEMAX
            print('Min velocity already!')
        print(f"Time between words: {time_delay}s")

def monitor_buttons():
    global paused, back_word, time_delay, index
    last_states = {b: GPIO.input(b) for b in BUTTONS}
    while True:
        for b in BUTTONS:
            current = GPIO.input(b)
            if current == GPIO.LOW and last_states[b] == GPIO.HIGH:
                with lock:
                    if b == PAUSE_BUTTON:
                        paused = not paused
                        print(f"[Button] Pause: {paused}")
                    elif b == REPLAY_WORD_BUTTON:
                        back_word = True
                        if(index == 0):
                            print(f"[Button] You are already in first word!")
                        else:
                            print(f"[Button] Playback Word: {memory.words[index-1]}")
                        index = max(index - 1, 0)
                    elif b == RAISE_VEL_BUTTON:
                        if time_delay - VEL_STEP >= TIMEMIN:
                            time_delay = max(TIMEMIN, time_delay - VEL_STEP)
                            print(f"[Button] Velocity Raised: {time_delay:.2f}s")
                        else:
                            time_delay = TIMEMIN
                            print(f"[Button] Velocity Max Already! {time_delay:.2f}")
                    elif b == REDUCE_VEL_BUTTON:
                        if time_delay + VEL_STEP <= TIMEMAX:
                            time_delay = min(TIMEMAX, time_delay + VEL_STEP)
                            print(f"[Button] Velocity Reduced: {time_delay:.2f}s")
                        else:
                            time_delay = TIMEMAX
                            print(f"[Button] Velocity Min Already! {time_delay:.2f}")
                    
            last_states[b] = current
        time.sleep(0.05)


# === Configure Interruptions === #
try: 
    print("Setting up button interrupts...")
    GPIO.add_event_detect(REPLAY_WORD_BUTTON, GPIO.FALLING, callback=back_word_callback,  bouncetime=200)
    GPIO.add_event_detect(RAISE_VEL_BUTTON,   GPIO.FALLING, callback=raise_vel_callback,  bouncetime=200)
    GPIO.add_event_detect(REDUCE_VEL_BUTTON,  GPIO.FALLING, callback=reduce_vel_callback, bouncetime=200)
    GPIO.add_event_detect(PAUSE_BUTTON,       GPIO.FALLING, callback=pause_callback,      bouncetime=200)
except Exception as e:
    print('Erro when setting up button interrupts ' + str(e))

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
        try:
            volume  = get_volume() # (0.0 - 1.0)
        except:
            volume = 1.0
            print("Could not read potenciometer")

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
                if(carac in word) and carac == word[-1]:
                    word = word.replace(carac, '')

        except Exception as e:
            print(f"Error: {str(e)}")
        
    return word

def create_mp3_words(words, folder):
    for word in words:
        if word and len(word) > 1:
            try:
                if(f"{folder}/output{clean_word(word).upper()}.mp3" in os.listdir(folder)):
                    print(f"File already exists: {folder}/output{clean_word(word).upper()}.mp3")
                    continue
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

def start_conversion(bus):
    # Start convertion in A0 canal (single-shot)
    config = [
        0b11000010,  # MSB: 1=start single-shot, MUX=A0, PGA=±4.096V, mode=single-shot
        0b11100011   # LSB: 860SPS, comparador desativado
    ]
    bus.write_i2c_block_data(ADDRESS, POINTER_CONFIG, config)

def read_conversion(bus):
    # Wait time conversion (~1ms to 860SPS)
    time.sleep(0.0015)
    raw = bus.read_i2c_block_data(ADDRESS, POINTER_CONVERSION, 2)
    value = (raw[0] << 8) | raw[1]
    if value > 0x7FFF:
        value -= 0x10000
    return value

def get_volume():
    try:

        with SMBus(I2C_BUS) as bus:
            start_conversion(bus)
            value = read_conversion(bus)
            time.sleep(0.1)

            if value < 10:
                value = 0
        return min( (value / 26365) , 1 )
    except Exception as e:
        print(f"[WARNING] I2C Volume Read Error: {e}")
        return 1.0

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

        # Save text and words to memory
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
        global time_delay, index, back_word, paused

        data = request.get_json()
        time_delay = data.get('time', 1)

        words = memory.words
        size = len(words)

        while index < size:
            back_word = False

            if check_buttons():
                continue
            
            word = words[index] 
            # Speak word
            if(len(word) > 1):
                speak_online(word, "words")

            if check_buttons():
                continue
            
            if word[0] in NUMBERS:
                speak_online('NUMERO', 'letters')
                do_braille_letter(BEFORE_NUMBER)
            
            # Speak each caracter     
            for c in word:

                if check_buttons():
                    break

                reset_pwms()

                if c in BAD_CARACTERS:
                    speak_online(BAD_CARACTERS[c], 'letters')
                else:
                    if c.isupper():
                        speak_online('MAIUSCULO', 'letters')
                        do_braille_letter(BEFORE_UPPER)
                    speak_online(c,'letters')

                braille_letter = translate_to_braille(c) 
                do_braille_letter(braille_letter)
                time.sleep(time_delay)
            
            if check_buttons():
                continue

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
        reset_pwms()
        index = 0
        back_word = False
        paused = False
    
#=====================================================================================#

if __name__ == '__main__':
    try:
        start_pwms()
        print("[INFO] Starting flask server using thread")
        server_thread = threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000})
        server_thread.daemon = True
        server_thread.start()

        button_thread = threading.Thread(target=monitor_buttons)
        button_thread.daemon = True
        button_thread.start()

        while True:
            time.sleep(1)

    except Exception as e:
        print(f"[ERROR] Ocurred and error: {str(e)}")
    finally:
        print("[INFO] Closing program...")
        pygame.quit()
        reset_pwms()
        destroy_mp3_words(memory.words, 'words')
        GPIO.cleanup()



