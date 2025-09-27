# JoJo clock, displaying days of the week and current time
# each day is lighted by 3 neopixels which will fade In and Out at set times of day
# the fade in and out happens over a 1 hour period
# the clock has a 24/12 hour mode switch
# will auto adjust for Day light saving time based on Aus East coast time zones
# The clock can connect to the web to sync the RTC time using ntptime
# added interrupt to 12/24 hr to change time format immediately instead of waiting till next miniute
# (c) Michael Lamb September 2025
#
import neopixel
import time
from machine import Pin, SoftI2C, deepsleep,
import ds1307
from ht16k33segment import HT16K33Segment
import ntptime

i2c = SoftI2C(scl=Pin(1), sda=Pin(2))
ds = ds1307.DS1307(i2c)
np = neopixel.NeoPixel(Pin(0), 21)

utcoffset = 10
hr24 = Pin(3, Pin.IN, Pin.PULL_UP)
dst1 = 1 # DST date
dst2 = 0 # DST date

i2cb = SoftI2C(scl=Pin(5), sda=Pin(6))

d1 = HT16K33Segment(i2cb)

d1.clear()
d1.rotate()
d1.power_on()
d1.draw()
d1.set_brightness(1)

t = ds.datetime()
wday = t[3]

if t[4] in range (8,21):
    a1 = 30
    a2 = 30
    a3 = 30
else:
    a1 = 0
    a2 = 0
    a3 = 0

def get_dst_dates():
    global sdst, edst
    y1 = t[0]
    N = 2
    # create a new string of last N characters
    y1 = str(y1)[-N:]
    dd1 = 9
    dd2 = 9

    def month_code():
        global m2, m1
        mc = (0,3,3,6,1,4,6,2,5,0,3,5)
        m2 = mc[m1-1]

    leap=0
    y1 = int(y1)
    y2 = (y1+int(y1/4))%7
    print(y2)
    #Find 1st sunday in October
    d1 = 0
    while dd1 != 0:
        if dd1 != 0:
            m2 = 0 #October
            d1= d1+1
            dd1 = ((y2+m2+6+d1)-leap)%7
            sdst = d1
        else:
            print(d1)

    #Find 1st sunday in April
    d1 = 0
    y1e = int(y1)
    y2e = (y1e+int(y1e/4))%7
    while dd2 != 0:
        if dd2 != 0:
            m2 = 6 #April
            d1= d1+1
            dd2 = ((y2e+m2+6+d1)-leap)%7
            edst = d1
        else:
            print(d1)
        
    #print("1st Sun of October in",y1,"is:",sdst)
    #print("1st Sun of April in",y1e,"is:",edst)

def get_time():
    print(ds.datetime())#time.localtime())
    ntptime.settime()
    time_secs = ntptime.time() + 3600*utcoffset#(3600*11)
    #time_secs = (time.mktime(time.localtime())) + 3600*utcoffset#(3600*11)

    print("")
    year, month, day, hour, minute, second, weekday, yearday = time.localtime(time_secs)

    print(f"Date: {day}/{month}/{year}")
    print(f"Time: {hour}:{minute}:{second}")
    now = year, month, day, weekday, hour, minute, second, yearday
    ds.datetime(now)
        
def chk_dst():
    global dst1, dst2, utcoffset
    t = ds.datetime()
    #Check for start of Daylight Savings time   
    print(t[1], "T1")
    if t[1] == 10:# If October
        print(t[2], "T2")
        print(sdst)
        if t[2] == sdst: #is it the 1st sunday
            print(t[4], "T3")
            if t[4] == 2: # is it 2am
                print(dst2)
                if dst2 == 0: #have I already done this
                    utcoffset = 11 # add 1 hour for DST
                    get_time()#rtc_update()
                    dst2 = 1
                    dst1 = 1
                    t = ds.datetime()
                    
     #Check for end of Daylight Savings time
    if t[1] == 4: #is April
        if t[2] == edst: #is the 1st sunday
            print("Hour",t[4])
            if t[4] == 3: #is it 3am
                print(dst1)
                if dst1 == 1: #have I done this already ?
                    print("Hi")
                    utcoffset = 10 # remove 1 hour for EST 
                    get_time()#rtc_update()
                    dst1 = 0
                    dst2 = 0
                    t = ds.datetime()

def clock(pin):
    global dtest, t,zz
    zz=ds.datetime()
    t5 = zz[5]
    if hr24.value() == 0:
        if zz[0] != 0:
            t14 = zz[4]
            t5 = zz[5]
            
            if t14 >= 13:
                t14 = t14-12
                #print("t14=",t14)
                
            if zz[4] in range (0,10): # in the AM time is given with a 0 for single digit time, PM time just single digit is displayed
                t3 = str(t14)
                t3 = (str(0)+t3)
                a1 = int(str(t3)[0])
                if a1 == 0:
                    if zz[4] >=13:
                        a1 = " "
                a2 = int(str(t3)[1])
            else:
                if len(str(t14)) ==1:
                    a1 = " "#int(str(t14)[0])
                    a2 = int(str(t14)[0])
                else:
                    a1 = int(str(t14)[0])
                    a2 = int(str(t14)[1])
                    
    else:
        a1 = int(str(zz[4])[0])
        a2 = int(str(zz[4])[1])
        
    if t5 in range (0,10):
        t4 = str(t5)
        t4 = (str(0)+t4)
        a3 = int(str(t4)[0])
        a4 = int(str(t4)[1])
    else:
        a3 = int(str(t5)[0])
        a4 = int(str(t5)[1])
        
    drawn = 10
    for attempt in range (drawn):
        try:
            d1.set_character(str(a1), 0)
            d1.set_number(a2, 1)
            d1.set_number(a3, 2)
            d1.set_number(a4, 3)
            d1.set_colon()
            d1.draw()
            drawn = 0
        except:
            drawn = drawn -1
            f=open("/config/syslog.txt","a")
            f.write("d1 error","\n")#for tup in t:
            for tup in t: #write date / time string to file
                f.write(str(tup))
                f.write(", ")
            f.write("\n")
            f.close()

def week_day():
    global wday,a ,b, c
    t = ds.datetime()#t = time.localtime()
    #Neopixel address for each day
    if t[3] == 6: # Sunday
        a = 0
        b = 1
        c = 2
    if t[3] == 5: # Saturday
        a = 3
        b = 4
        c = 5
    if t[3] == 4: # Friday
        a = 6
        b = 7
        c = 8
    if t[3] == 3: # Thursday
        a = 9
        b = 10
        c = 11
    if t[3] == 2: # Wednesday
        a = 12
        b = 13
        c = 14
    if t[3] == 1: # Tuesday
        a = 15
        b = 16
        c = 17
    if t[3] == 0: # Monday
        a = 18
        b = 19
        c = 20

    np = neopixel.NeoPixel(Pin(0), 21)
    np[a] = (a1, a2, a3) # setting to neopixel colors and brightness
    np[b] = (a1, a2, a3)
    np[c] = (a1, a2, a3)
    np.write()
    wday = t[3]

def getup():
    global a1,a2, a3
    if a1 <= 30:
        a1 = a1+ 1
        a3 = a1
        if a1 >= 15:
            a2 = a2+2
        time.sleep(.5)
        np[a] = (a1, a2, a3) # setting 1st to neopixel colors and brightness
        np.write()
        np[b] = (a1, a2, a3) # setting 2nd to neopixel colors and brightness
        np.write()
        np[c] = (a1, a2, a3) # setting 3rd to neopixel colors and brightness
        np.write()

def bedtime():
    global a1,a2, a3, np
    if a1 >= 1:
        a1 = a1- 1
        a3 = a1
        #a2 = a1
        if a1 >= 15:
            a2 = a2-2
        else:
            a2 = 0
        time.sleep(.5)
        np[a] = (a1, a2, a3) # setting to neopixel colors and brightness
        np.write()
        np[b] = (a1, a2, a3) # setting to neopixel colors and brightness
        np.write()
        np[c] = (a1, a2, a3) # setting to neopixel colors and brightness
        np.write()
        #print(np[a])

#monitors 24/12 hr switch for change and then run the clock display update to reflect the change
hr24.irq(trigger=Pin.IRQ_FALLING, handler=clock)
week_day()
get_dst_dates()

while True:
    t= ds.datetime()
    clock(hr24)
    al2 = 60 - t[6]
    if t[3] != wday:
        week_day()
            
    time.sleep(al2)
    #run bedtime and getup def on even miniutes only
    if t[4] in range (20,21):
        if t[5] % 2 == 0:
            bedtime()
            #print(np[a])
            
        else:
            print("Odd Minute")
            
    if t[4] in range (7,8):
        if t[5] % 2 == 0:
            getup()
            #print(np[a])
            
        else:
            print("Odd Minute")

    # Set the LED display brightness        
    if t[4] not in range (7,21):
        d1.set_brightness(1) #set display to day time#set display to lowest setting setting
        np[a] = (0,0,0)
        np[b] = (0,0,0)
        np[c] = (0,0,0)
        np.write()
    else:
        d1.set_brightness(8) #set display to lowest setting
        #d1.set_brightness(0) # turn display off
        #np[a] = (0,0,0) #making sure all neopixel are off after bed time
        #np[b] = (0,0,0)
        #np[c] = (0,0,0)
        #np.write()
        
    chk_dst() # check if it is daylight savings time or not
    # at midnight of the 1st of the month time sync with NTP servers
    if t[2] == 1 and t[4] == 0 and t[5] == 0:
        get_time()
