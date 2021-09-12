#Checks to make sure that everything is OK
import subprocess
import RPi.GPIO as GPIO
from gpiozero import Button
import pyttsx3
import time
import subprocess
import os
import signal
import spidev
import sys




def main():
    buttons = False
    for arg in sys.argv[1:]:
        if arg == "buttons":
            buttons = True
    print(buttons)
    engine = pyttsx3.init() # object creation
    engine.setProperty('rate',170)
    engine.setProperty('volume',1.0)
    if buttons:
        btn = Button(17)
        confirmBtn = Button(5)
    def say(phrase):
        engine = pyttsx3.init()
        engine.say(phrase)
        print(phrase)
        engine.runAndWait()
    if buttons:
        GPIO.setwarnings(False)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(27, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)
    say("Welcome to the system check. Please go to an open area. Notes that all features will be temporarily disabled until the check is complete.")
    time.sleep(2)
    #Camera test
    say("Testing camera")
    failed3 = False
    try:
        subprocess.check_output(["raspistill","-o","test.png"],stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        say("ERROR: Camera not working")
        failed3 = True
    if not failed3:
        say("Camera is working")

    #Distance sensor teset
    say("For the distance sensor test, please make sure that every distance sensor is clear, besides the interior one.")
    time.sleep(1)
    failed2 = False
    try:
        subprocess.check_output(["python3","distTest.py"],stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        say("ERROR: 1 or more distance senors are not being recognized")
        failed2 = True
    if not failed2:
        output = subprocess.check_output(['python3','distTest.py'])
        dists = str(output).split(",")
        print(dists)
        fails = 0
        for dist in dists:
            if "front" in dist:
                if "-1185" in dist:
                    say("ERROR: Front distance sensor is not properly reading.")
                    fails += 1
            elif "left" in dist:
                if "-1185" in dist:
                    say("ERROR: Left distance sensor is not properly reading.")
                    fails += 1
            elif "right" in dist:
                if "-1185" in dist:
                    say("ERROR: Right distance sensor is not properly reading.")
                    fails += 1
        if fails == 0:
            say("All distance sensors working")

    #LIS3DH Test
    failed = False
    try:
        subprocess.check_output(["python3","acelTest.py"],stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        say("ERROR: Accelerometer not working")
        failed = True
    if not failed:
        say("Accelerometer working")

        

    output = subprocess.check_output(['arecord','-l'])
    if "sndrpii2scard" in str(output):
        say("Mic found")
        #Testing Microphone quality.
        say("Please say hello within the next 3 seconds.")
        output = subprocess.check_output(['arecord','-l'])
        result = "plughw:" + str(output).split("card ",1)[1][0]
        process = subprocess.Popen(["arecord","-D",result,"-c1","-r","16000","-f","S32_LE","-t","wav","-V","mono","audioFile.wav","-q"])
        time.sleep(3)
        os.kill(process.pid, signal.SIGINT)
        translated = str(subprocess.check_output(["python3","audio_transcribe.py"]))
        if "Google Speech Recognition could not understand audio" in translated:
                say("ERROR: No audio response recognized.")
        elif "Could not request results from Google Speech Recognition service;" in translated:
                say("Voice recognition needs an internet connection to function.")
        else:
                say("Microphone is functioning.")
    else:
        say("ERROR: Mic not found. Recording check will be skipped.")


    if buttons:
        say("Button test. Click All 3 buttons at once within the next 3 seconds.")
        time.sleep(2)
        if GPIO.input(4) == GPIO.HIGH:
            say("Assistant button working")
        else:
            say("ERROR: Assistant button not found")
        if btn.value == 1:
            say("N button working.")
        else:
            say("ERROR: N button not found")
        if confirmBtn.value == 1:
            say("Y button working.")
        else:
            say("ERROR: Y button not found")


    #Potentiometer check
    spi_ch = 0

    # Enable SPI
    spi = spidev.SpiDev(0, spi_ch)
    spi.max_speed_hz = 1200000
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

    adc_0 = get_adc(0)
    say("Please move the scroll wheel to any position within 3 seconds.")
    time.sleep(3)
    adc_1 = get_adc(1)
    if adc_0 != adc_1:
        say("scroll wheel is working.")
    else:
        say("ERROR: Scroll wheel not functioning.")

    say("All 3 vibration motors will now be activated")
    GPIO.output(22, GPIO.HIGH)
    GPIO.output(27, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(22, GPIO.LOW)
    GPIO.output(27, GPIO.LOW)
    say("All vibration motors turned off.")

    say("System check is finished.")
if __name__ == "__main__":
    main()