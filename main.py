# define constants
RTCAddr = 0x6f
SEC = 0x00
MIN = 0x01
HOUR = 0x02
TIMEZONE = 2
sys_secs=0
sys_mins=0
sys_hours=0
secs_diff=0
hours=0
ldr=0
mins=0
secs=0
count=0
dismissed_before = False
monitor = True
reset=False
freq=1
V0 = 0
V1 = 1
V2 = 2
values = [0]*3

import blynklib
BLYNK_AUTH='GYAcd_nXdOOIl9uFBgDMVgYyaVNoKFCQ'
blynk=blynklib.Blynk(BLYNK_AUTH)
#blynk.connect()
READ_PRINT_MSG = "[READ_VIRTUAL_PIN_EVENT] Pin: V{}"
import RPi.GPIO as GPIO
import random
import time
import adc
GPIO.setmode(GPIO.BOARD)

# set buttons
GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

chan_list=(11,13)
GPIO.setup(chan_list, GPIO.OUT)
GPIO.output(13, 1)
GPIO.output(11, 0)


def dismiss(channel):
    print("dismissed")
    GPIO.output(11, 0)

def reset(channel):
    print("reset")
    global secs
    global sys_secs
    global sys_mins
    global sys_hours
    global secs_diff
    sys_mins=0
    sys_hours=0
    sec_diff=secs_diff%60
    if (sys_secs>0):
        secs_diff=sys_secs+secs_diff+1

def start_or_stop(channel):
    global monitor
    if monitor==True:
        monitor=False
    elif monitor==False:
        monitor=True

def frequency(channel):
    global freq
    freqs=[1,2,5]
    if freq == freqs[0]:
        freq = freqs[1]
    elif freq == freqs[1]:
        freq = freqs[2]
    elif freq == freqs[2]:
        freq = freqs[0]

def hexCompensation(units):
    unitsU = units%0x10
    if (units>= 0x50):
        units=50+unitsU
    elif (units>=0x40):
        units=40+unitsU
    elif (units>=0x30):
        units=30+unitsU
    elif (units>=0x20):
        units=20+unitsU
    elif (units>=0x10):
        units=10+unitsU
    return units

from smbus2 import SMBus, i2c_msg
GPIO.add_event_detect(29, GPIO.RISING, callback=dismiss, bouncetime=200)
GPIO.add_event_detect(31, GPIO.RISING, callback=reset, bouncetime=200)
GPIO.add_event_detect(33, GPIO.RISING, callback=start_or_stop, bouncetime=200)
GPIO.add_event_detect(37, GPIO.RISING, callback=frequency, bouncetime=200)

def main():
    with SMBus(1) as bus:
        global hours_initial
        global secs_diff
        global mins_initial
        bus.write_byte_data(RTCAddr,SEC,0x80)
	hours_initial=hexCompensation(bus.read_byte_data(RTCAddr,HOUR))
        mins_initial=hexCompensation(bus.read_byte_data(RTCAddr,MIN))
        secs_diff=hexCompensation(bus.read_byte_data(RTCAddr,SEC)-0x80)
        global sys_hours
        global sys_mins
        global hours
        global ldr
	global values
        global mins
        global secs
        global sys_secs
        global dismissed_before
        global count
        global monitor
        global freq
	global V0
	global V1
	global V2
 
        print '+------------------------------------------------------------+'
        print '|RTC time      |System time   |Humidity|Temp  |Light  |DAC   |'
        print '|--------------|--------------|--------|------|-------|------|'
        while True:
            hours=hexCompensation(bus.read_byte_data(RTCAddr,HOUR))
            mins=hexCompensation(bus.read_byte_data(RTCAddr,MIN))
            secs=bus.read_byte_data(RTCAddr,SEC)
            secs=hexCompensation(secs-0x80)
            if (secs>=sys_secs):
                sys_secs=secs-secs_diff
            elif (secs<sys_secs):
                sys_secs=(60-secs_diff)+secs
            if sys_secs>=60:
                sys_secs=0
                sys_mins=sys_mins+1
            if sys_mins>=60:
                sys_mins=0
                sys_hours=sys_hours+1
            blynk.connect()
            if monitor==True:
	        ldr = adc.readadc(0)
	        blynk.virtual_write(0,ldr)
                temp = adc.readadc(1)
	        blynk.virtual_write(1, "%.1f"%temp)
                humid = "%.1f"%adc.readadc(2)
	        blynk.virtual_write(2,humid)
		DAC = (float(ldr)/1023)*adc.readadc(2)
		blynk.virtual_write(4, "%.2f"%DAC)
                if ((DAC<0.65)or(DAC>2.65)) and (dismissed_before==False):
                    print("alarm sounded")
                    blynk.notify("alarm sounded")
                    GPIO.output(11, 1)
                    dismissed_before=True
                    count = 0
                elif ((DAC<0.65)or(DAC>2.65)) and (dismissed_before==True) and (count >= 180):
                    print("alarm sounded")
                    blynk.notify("alarm sounded")
                    GPIO.output(11, 1)
                    count = 0
                blynk.virtual_write(3, 'clr')
                blynk.virtual_write(3, "RTC time   System time\n")
                blynk.virtual_write(3,'%2s'%hours,':','%2s'%mins,':','%2s'%secs,'%3s'%' ','%2s'%sys_hours,':','%2s'%sys_mins,':','%2s'%sys_secs,'\n')
                print '|','%2s'%hours,':','%2s'%mins,':','%2s'%secs,'|','%2s'%sys_hours,':','%2s'%sys_mins,':','%2s'%sys_secs,'|','%6s'%humid,'|','%.1f'%temp,'|','%5s'%ldr,'|','%.2f'%DAC,'|'
            elif monitor==False:
                blynk.virtual_write(0,'N/A')
                blynk.virtual_write(1,'N/A')
                blynk.virtual_write(2,'N/A')
                blynk.virtual_write(4,'N/A')
                blynk.virtual_write(3, 'clr')
                blynk.virtual_write(3, 'RTC time   System time\n')
                blynk.virtual_write(3, '%2s'%hours,':','%2s'%mins,':','%2s'%secs,'%3s'%' ','%2s'%sys_hours,':','%2s'%sys_mins,':','%2s'%sys_secs,'\n')
                print '|','%2s'%hours,':','%2s'%mins,':','%2s'%secs,'|','%2s'%sys_hours,':','%2s'%sys_mins,':','%2s'%sys_secs,'|','%6s'%' ','|','%4s'%' ','|','%5s'%' ','|','%4s'%' ','|'
            count=count+1
            time.sleep(freq)

if __name__== "__main__":
    # make sure the GPIO is stopped correctly
    try:
        while True:
	    blynk.run()
            main()
    except KeyboardInterrupt:
        print("SYSTEM QUIT")
#        turn off GPIO
        GPIO.cleanup()
#    except e:
#        GPIO.cleanup()
#        print("some other error occured")
#        print(e.message)
