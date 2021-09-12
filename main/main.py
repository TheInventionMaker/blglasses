#MAIN PROGRAM FOR THE GLASSES
import signal
import sys
import RPi.GPIO as GPIO
from gpiozero import Button
import pyttsx3
import subprocess
import time
import board
import digitalio
import adafruit_lis3dh
import VL53L1X
import asyncio
import TCA9548A
import datetime
import wikipedia
import os
import wolframalpha
import requests
import threading
import spidev



i2c = board.I2C()
int1 = digitalio.DigitalInOut(board.D6)  # Set this to the correct pin for the interrupt!
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
lis3dh.set_tap(1, 120)
shaken = True
   
engine = pyttsx3.init() # object creation
rate = engine.getProperty('rate')   # getting details of current speaking rate
engine.setProperty('rate',170)
engine.setProperty('volume',1.0)


GPIO.setwarnings(False)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, GPIO.LOW)
GPIO.output(27, GPIO.LOW)
time.sleep(1)


TCA9548A.I2C_setup(0x70,0)
tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open()
tof.set_timing(66000, 70)
tof.start_ranging(3)  # Start ranging
distance_in_mm = tof.get_distance()

TCA9548A.I2C_setup(0x70,1)
tof2 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof2.open()
tof2.set_timing(66000, 70)
tof2.start_ranging(3)  # Start ranging
distance_in_mm = tof2.get_distance()

TCA9548A.I2C_setup(0x70,2)
tof3 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof3.open()
tof3.set_timing(66000, 70)
tof3.start_ranging(3)  # Start ranging
tof3.get_distance()

spi_ch = 0
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000

sidewalkDetecting = False
pastSidewalk = False
objectDetection = subprocess.Popen(["python3","TFLite_detection_webcam.py", "--model=Sample_TFLite_model"])
pastVolume = 0.0
sleep = 10
updateNeeded = False
btn = Button(17)
confirmBtn = Button(5)

settingOptions = ["Disable Image Recognition","Change Image Distance","Change Image Sensitivity",
"Disable Navigation","Disable Vibration","Change Nav Distance","Change Vibration Distance","Disable Smart Assistant",
"Change voice speed","Change sleep time","Change Wifi","System Report (Only do this if you are seated)","Exit"]

settingSelection = 9
scrollValue = 0
settingsEntered = False
usingScroll = False
units = ""
imgRecog = True
imgSens = 75
imgDist = 48
navigation = False
vibDist = 48
smartEnabled = True
voiceSpeed = 170
navDist = 48
stopVibration = True
btn.hold_time = 2
notUpdating = True

def sidewalkDetection():
    p1 = subprocess.Popen(["python3","classify_picamera.py","--model","SidewalkModel/model.tflite","--labels","SidewalkModel/labels.txt"])
async def forward():
	global tof
	TCA9548A.I2C_setup(0x70, 0)
	if tof.get_distance() <= 1220:
		GPIO.output(27, GPIO.HIGH)
	else:
		GPIO.output(27, GPIO.LOW)
	await asyncio.sleep(0.15)
async def left():
	global tof2
	TCA9548A.I2C_setup(0x70, 1)
	if tof2.get_distance() <= 1220:
		GPIO.output(22, GPIO.HIGH)
	else:
		GPIO.output(22, GPIO.LOW)
	await asyncio.sleep(0.15)
async def main():
	global tof3
    
	TCA9548A.I2C_setup(0x70, 2)
    
	await asyncio.gather(forward(), left())
def distsTest():
    global tof, tof2, tof3
    TCA9548A.I2C_setup(0x70, 0)
    d1 = tof.get_distance()
    
   # print(d1, d2, d3)
    if d1 <= navDist * 25.4:
        return True
    return False
def max_element_index(items):
    max_index, max_value = None, None
    for index, item in enumerate(items):
        if item > max_value:
             max_index, max_value = index, item
    return max_index
def navigationF():
    global tof, tof2, tof3
    TCA9548A.I2C_setup(0x70, 0)
    d1 = tof.get_distance()
    TCA9548A.I2C_setup(0x70, 1)
    d2 = tof2.get_distance()
    TCA9548A.I2C_setup(0x70, 2)
    d3 = tof2.get_distance()
    available = ["Forward","Left","right"]
    dists = [d1,d2,d3]

    return available[dists.index(max(dists))]

#
#
#SMART
#ASSISTANT
#
#    
def smartAssistant():
    global engine
    engine.say("Listening...")
    engine.runAndWait()
    output = subprocess.check_output(['arecord','-l'])
    result = "plughw:" + str(output).split("card ",1)[1][0]
    process = subprocess.Popen(["arecord","-D",result,"-c1","-r","16000","-f","S32_LE","-t","wav","-V","mono","audioFile.wav","-q"])
    while GPIO.input(4) == GPIO.HIGH:
        pass
    os.kill(process.pid, signal.SIGINT)
    translated = str(subprocess.check_output(["python3","audio_transcribe.py"]))
    print()
    print("BUTTONUP")
    if "Google Speech Recognition could not understand audio" in translated:
            say("I couldn't quite catch that.")
            print("$done")
    elif "Could not request results from Google Speech Recognition service;" in translated:
            say("Voice recognition needs an internet connection to function.")
            print("$done")
    else:
            print("I heard: " + translated[2:len(translated) - 3])
            response = translated[2:len(translated) - 3]
            assistant(response)
            print("$done")

def onWord(name, location, length):
    if location > 10:
        engine.stop()
def sayFunc(phrase):
    engine = pyttsx3.init()
    engine.setProperty('rate', voiceSpeed)
    engine.say(phrase)
    print(phrase)
    engine.runAndWait()
def say(phrase):
    engine = pyttsx3.init()
    engine.connect('started-word', onWord)
    engine.say(phrase)
    print(phrase)
    engine.runAndWait()

#CREDIT TO: https://towardsdatascience.com/how-to-build-your-own-ai-personal-assistant-using-python-f57247b4494b

def speak(word):
    if len(word) > 50:
        print(word)
        say(word)
    else:
        print(word)
        say(word)
def assistant(statement):
    if "exit" in statement or "quit" in statement or "nevermind" in statement or "goodbye" in statement or "ok bye" in statement or "stop" in statement:
        speak('shutting down')
        quit()
    elif 'wikipedia' in statement.lower():
        speak('Searching Wikipedia...')
        statement =statement.replace("wikipedia", "")
        results = wikipedia.summary(statement, sentences=3)
        speak("According to Wikipedia")
        speak(results)
    elif 'battery' in statement.lower():
        speak('The battery is at 100%')
    else:
        if 'time' not in statement:
        	sayFunc("Loading results...")
        app_id="Paste your unique ID here "
        client = wolframalpha.Client('73H672-35Q9UL72QG')
        res = client.query(statement)
        try:
            if 'time' in statement:
            	speak("The time is " + next(res.results).text)
            else:
                speak(next(res.results).text)
        except StopIteration:
            statement =statement.replace("wikipedia", "")
            results = wikipedia.summary(statement, sentences=3)
            speak(results)

#
# POT
#

def close(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, close)

def get_adc(channel):
    if channel != 0:
        channel = 1

    msg = 0b11
    msg = ((msg << 1) + channel) << 5
    msg = [msg, 0b00000000]
    reply = spi.xfer2(msg)

    adc = 0
    for n in reply:
        adc = (adc << 8) + n

    # Last bit (0) is not part of ADC value, shift to remove it
    adc = adc >> 1

    # Calculate voltage form ADC value
    # considering the soil moisture sensor is working at 5V
    voltage = (5 * adc) / 1024

    return voltage




    
async def timer():
     await asyncio.gather(
        asyncio.create_task(async_foo())
    )
# timer is scheduled here
def async_foo():
    global sleep
    global shaken, updateNeeded
    for _ in range(0,sleep):
        time.sleep(1)
    shaken = False
    print("Going to sleep...")
    print(objectDetection.poll())
    objectDetection.terminate()
    print(objectDetection.poll())
    if(os.path.isfile("blglasses/main")):
        os.chdir("blglasses/main")
    response = requests.get("https://api.github.com/repos/TheInventionMaker/blglasses/releases/latest")
    version = response.json()["tag_name"]
    if(os.path.isfile(version + '.txt')):
        updateNeeded = False
    else:
        say("Update found and will proceed once you plug in the glasses.")
        updateNeeded = True
        
        
thr = threading.Thread(target=async_foo, args=(), kwargs={})
thr.start() 
def settings():
    global navDist, sleep, voiceSpeed, smartEnabled, vibDist, stopVibration, navigation, settingsEntered, settingOptions, settingSelection, imgRecog, objectDetection, imgSens, imgDist, usingScroll, units
    if settingSelection == 0:
        if imgRecog:
            speak("Image recognition disabled.")
            settingOptions[settingSelection] = "Enable Image recognition"
            imgRecog = False
            objectDetection.terminate()
        else:
            speak("Image recognition enabled.")
            settingOptions[settingSelection] = "Disable Image recognition"
            imgRecog = True
            objectDetection = subprocess.Popen(["python3","TFLite_detection_webcam.py", "--model=Sample_TFLite_model"])
    elif settingSelection == 1:
        speak("Use scroll wheel to change from " + str(imgDist) + "inches. Click Y to finish.")
        usingScroll = True
        units = "inches"
    elif settingSelection == 2:
        speak("Use scroll wheel to change from " + str(imgSens) + "percent. Click Y to finish.")
        usingScroll = True
        units = "percent"
    elif settingSelection == 3:
        if navigation:
            speak("Navigation disabled.")
            settingOptions[settingSelection] = "Enable navigation"
            navigation = False
        else:
            speak("Navigation enabled.")
            settingOptions[settingSelection] = "Disable navigation"
            navigation = True
    elif settingSelection == 4:
        speak("Use scroll wheel to change from " + str(navDist) + "inches. Click Y to finish.")
        usingScroll = True
        units = "inches"
    elif settingSelection == 5:
        if stopVibration:
            speak("vibration enabled.")
            settingOptions[settingSelection] = "Disable vibration"
            stopVibration = False
        else:
            speak("vibration disabled.")
            settingOptions[settingSelection] = "Enable vibration"
            stopVibration = True
    elif settingSelection == 6:
        speak("Use scroll wheel to change from " + str(vibDist) + "inches. Click Y to finish.")
        usingScroll = True
        units = "inches"
    elif settingSelection == 7:
        if smartEnabled:
            speak("Smart Assistant disabled.")
            settingOptions[settingSelection] = "Enable smart assistant"
            smartEnabled = False
        else:
            speak("Smart Assistant enabled.")
            settingOptions[settingSelection] = "Disable smart assistant"
            smartEnabled = True
    elif settingSelection == 8:
        speak("Use scroll wheel to change from " + str(voiceSpeed) + ". Click Y to finish.")
        usingScroll = True
        units = "0"
    elif settingSelection == 9:
        speak("Use scroll wheel to change from " + str(sleep) + "minutes. Click Y to finish.")
        usingScroll = True
        units = "minutes"
    elif settingSelection == 10:
        speak("Wifi needs to be implemented at a later date.")
    elif settingSelection == 11:
        objectDetection.terminate()
        subprocess.run(["python3","systemCheck.py"])
        settingsEntered = False
        objectDetection = subprocess.Popen(["python3","TFLite_detection_webcam.py", "--model=Sample_TFLite_model"])
        time.sleep(3)
    else:
        settingsEntered = False
        speak("Exited settings")
def shook():
    global shaken, objectDetection
    if shaken == False:
        print("Wakened!")
        shaken = True
        thr = threading.Thread(target=async_foo, args=(), kwargs={})
        thr.start() 
        if objectDetection.poll() is not None and imgRecog:
            objectDetection = subprocess.Popen(["python3","TFLite_detection_webcam.py", "--model=Sample_TFLite_model"])

def update():
    global notUpdating
    os.chdir(os.path.expanduser("~"))
    updater = subprocess.Popen(["python3","updater.py"])
    notUpdating = False
while notUpdating:
    try:
        if updateNeeded:
            notUpdating = False
        #TEMP CHECK
        output = subprocess.check_output(['vcgencmd','measure_temp'])
        output = str(str(output)[7:len(str(output)) - 5])
        if float(output) > 85:
            if float(output) > 95:
                speak("Shut down immediately.")
            else:
                speak("Temperature too high. Sleeping until temperature goes down.")
                shaken = False
        elif float(output) > 80:
            shaken = True
        #SLEEP CHECK
        if lis3dh.shake(shake_threshold=15):
            shook()
                
        if shaken:
            pass

        #DISTANCE
        if sidewalkDetecting == False:
            if shaken == True and stopVibration == False:
                asyncio.run(main())
            else:
                GPIO.output(22, GPIO.LOW)
                GPIO.output(27, GPIO.LOW)
        elif pastSidewalk == False:
            pastSidewalk = True
            sidewalkDetection()

        if shaken and navigation:
            if distsTest():
                say("Navigate " + navigationF())
        #FEATURES
        if GPIO.input(4) == GPIO.HIGH:
            shook()
            if smartEnabled:
                print("Smart Assistant activated")
                smartAssistant()

        if settingsEntered and btn.value == 1 and confirmBtn.value == 1:
            
            speak("Exited Settings.")
            btn.wait_for_release()
            settingsEntered = False
        if btn.value == 1:
            
            if settingsEntered == False:
                settingsEntered = True
                speak("Settings. Hold both buttons to exit")
            
            btn.wait_for_release()
            settingSelection += 1
            if settingSelection == len(settingOptions) - 1:
                settingSelection = -1
            speak(settingOptions[settingSelection])
            shook()
       # print(confirmBtn.value)
        if confirmBtn.value == 1 and settingsEntered:
            if usingScroll == False:
                settings()
            else:
                usingScroll = False
                if settingSelection != 7:
                    speak("Changed to " + str(int(scrollValue)) + units)
                if settingSelection == 1:
                    imgDist = scrollValue
                elif settingSelection == 2:
                    imgSens = scrollValue
                elif settingSelection == 4:
                    navDist = scrollValue
                elif settingSelection == 6:
                    vibDist = scrollValue
                elif settingSelection == 8:
                    voiceSpeed = scrollValue * 3
                    engine.setProperty('rate',int(voiceSpeed))
                    speak("Changed to " + str(int(voiceSpeed)))
                elif settingSelection == 9:
                    sleep = scrollValue * 60
            
        #Settings should go here
        adc_1 = get_adc(1)
        if usingScroll and round(round(adc_1, 2) / 5.0 * 100.0,0) != scrollValue:
            scrollValue = round(round(adc_1, 2) / 5.0 * 100.0,0)
            if units == "0":
                if int(scrollValue * 3) > 100:
                    engine.setProperty('rate',int(scrollValue * 3))
                    speak(str(int(scrollValue * 3)))
                else:
                    speak("100")
                    engine.setProperty('rate',int(100))
            else:
                speak(str(int(scrollValue)))
       # print("V ADC Channel 1:", round(round(adc_1, 2) / 5.0 * 100.0,0), "V")
        if usingScroll == False and pastVolume != round(round(adc_1, 2) / 5.0 * 100.0 / 10.0,0):
            shook()
            pastVolume = round(round(adc_1, 2) / 5.0 * 100.0 / 10.0,0)
            engine.setProperty('rate',250)
            engine.setProperty('volume',round(adc_1, 2) / 5.0)
            if int(round(round(adc_1, 2) / 5.0 * 100.0,0)) != 0:
                engine.say(str(int(round(round(adc_1, 2) / 5.0 * 100.0 / 10.0,0) * 10)))
                engine.runAndWait()
            else:
                engine.setProperty('volume',0.5)
                engine.say("Volume Off")
                engine.runAndWait()
            engine.setProperty('rate',voiceSpeed)

            
        #Code here to check if the user is currently 'asleep' or not
        #if not asleep, run image recognition
        #else, cancel image recognition
        #Run image classification for sidewalk if not asleep
        #If sidewalk detected, run the side script

    except KeyboardInterrupt:
        GPIO.output(22, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        print("program executed")
        break

say("Updating...")
update()
#Currently supported features
#Working right now:
# - Wake and sleep detection
# - Distances sensors
# - Walking Stick Detection
# - Speaker & headphones
# - Mic
# - Smart Assistant
# - Button detection
# - Vibration motors
# - Image Recognition that stops when slept
# - Sidewalk detection using opencv fiters
# - Potentiometer
# - Volume Changer
# - Settings (except for wifi)
# - Temperature Warning
# - System Report
# - Room navigation using distance sensors

#Not yet working:
# - Wifi Switching
# - Auto switching for headphones
# - System check (Not fully done)
# - Sidewalk detection using classification
# - Custom Object recognition
# - Sidewalk people & other objects
# - Battery management
# - Updater script
# - Github repo
