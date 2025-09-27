# week_day_clock
a clock with 1.2 inch high adafruit Led display it also includes panels for each day of the week which light up for the current day, the lighted panel will fade to black over an hour to indicate bed time

The Hardware used in this project is listed below:
1 - ESP32-C3 super mini
1 - Adafruit 1.2" 7 4 digit 7 segment display (HT16k33 controller)
1 - DS1307 realtime clock
21 - Neopixel modules
1 - 2 position slide switch
1 - 3x7cm Double Side Prototype DIY Universal Printed Circuit PCB Board

The code is written in Micropython, during boot the code is paused for 5 seconds to allow a chance for the 12/24 hr switch to bechanged so the clock can enter setup mode
The clock will automaticlly adjust for daylight saving time (the time zone / DST used in the clock is Australia east coast time)
