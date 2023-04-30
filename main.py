# *****************************************************************************
# * | File        :   Pico_ePaper-7.5-B.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-05-27
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin, SPI
import framebuf
import utime
import time
import urequests as requests
import network

# Display resolution
EPD_WIDTH       = 800
EPD_HEIGHT      = 480

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

class EPD_7in5_B:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        

        self.buffer_black = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = framebuf.FrameBuffer(self.buffer_black, self.width, self.height, framebuf.MONO_HLSB)
        self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)

    def WaitUntilIdle(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 0):   # Wait until the busy_pin goes LOW
            self.delay_ms(20)
        self.delay_ms(20) 
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(0x12) # DISPLAY REFRESH
        self.delay_ms(100)      #!!!The delay here is necessary, 200uS at least!!!
        self.WaitUntilIdle()
        
    def init(self):
        # EPD hardware init start     
        self.reset()
        
        self.send_command(0x06)     # btst
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x28)        # If an exception is displayed, try using 0x38
        self.send_data(0x17)
        
#         self.send_command(0x01)  # POWER SETTING
#         self.send_data(0x07)
#         self.send_data(0x07)     # VGH=20V,VGL=-20V
#         self.send_data(0x3f)     # VDH=15V
#         self.send_data(0x3f)     # VDL=-15V
        
        self.send_command(0x04)  # POWER ON
        self.delay_ms(100)
        self.WaitUntilIdle()

        self.send_command(0X00)   # PANNEL SETTING
        self.send_data(0x0F)      # KW-3f   KWR-2F  BWROTP 0f   BWOTP 1f

        self.send_command(0x61)     # tres
        self.send_data(0x03)     # source 800
        self.send_data(0x20)
        self.send_data(0x01)     # gate 480
        self.send_data(0xE0)

        self.send_command(0X15)
        self.send_data(0x00)

        self.send_command(0X50)     # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x11)
        self.send_data(0x07)

        self.send_command(0X60)     # TCON SETTING
        self.send_data(0x22)

        self.send_command(0x65)     # Resolution setting
        self.send_data(0x00)
        self.send_data(0x00)     # 800*480
        self.send_data(0x00)
        self.send_data(0x00)
        
        return 0;

    def Clear(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        self.send_command(0x10)
        for i in range(0, wide):
            self.send_data1([0xff] * high)
                
        self.send_command(0x13) 
        for i in range(0, wide):
            self.send_data1([0x00] * high)
                
        self.TurnOnDisplay()
        
    def ClearRed(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        self.send_command(0x10) 
        for i in range(0, wide):
            self.send_data1([0xff] * high)
                
        self.send_command(0x13) 
        for i in range(0, wide):
            self.send_data1([0xff] * high)
                
        self.TurnOnDisplay()
        
    def ClearBlack(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        self.send_command(0x10) 
        for i in range(0, wide):
            self.send_data1([0x00] * high)
                
        self.send_command(0x13) 
        for i in range(0, wide):
            self.send_data1([0x00] * high)
                
        self.TurnOnDisplay()
        
    def display(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        # send black data
        self.send_command(0x10) 
        for i in range(0, wide):
            self.send_data1(self.buffer_black[(i * high) : ((i+1) * high)])
            
        # send red data
        self.send_command(0x13) 
        for i in range(0, wide):
            self.send_data1(self.buffer_red[(i * high) : ((i+1) * high)])
            
        self.TurnOnDisplay()


    def sleep(self):
        self.send_command(0x02) # power off
        self.WaitUntilIdle()
        self.send_command(0x07) # deep sleep
        self.send_data(0xa5)

def px(d):
    if d == 1:
        return 0xFF
    else:
        return 0x00

def blit_image(fbuffer, img, x, y, w, h):
    fbuffer.fill_rect(x, y, w, h, 0xFF)
    for i in range(int(w/8)):
        for j in range(h):
            byt = img[j * int(w/8) + i]
            for k in range(8):
                if ((byt >> k) & 1) == 1:
                    fbuffer.pixel(x + (8 * i) + (8 - k), y + j, 0x00)

#STOPNUM = 3656
STOPNUM = 2999
DIRECTION = "North Bound"

# connect to wifi
ssid = "Elon's iPhone"
password = "Faris123"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    sleep(1)

epd = EPD_7in5_B()
# test
# connected
def getArrivalTimes():
    result = requests.get(url="http://new.grtcbustracker.com/bustime/eta/getStopPredictionsETA.jsp"
        + "?agency="
        + "&route=all"
        + "&stop=%d" % STOPNUM
        # + "&direction=%s" % DIRECTION
    )

    xm = result.text.split("\n")
    xml = [d for d in xm if len(d) > 1]

    inEntry = False
    stack = []
    curMinute = "" # pt or pu
    curRoute = "" # rn
    curDirection = "" # fd
    for line in xml:
        if "</pre>" in line:
            stack.append([curMinute, curRoute, curDirection])
            continue
        if "<fd>" in line:
            curDirection = line.replace("<fd>", " ").replace("</fd>", " ").strip()
            continue
        if "<rn>" in line:
            curRoute = line.replace("<rn>", " ").replace("</rn>", " ").strip()
            continue
        if "<pt>" in line:
            curMinute = line.replace("<pt>", " ").replace("</pt>", " ").strip()
            continue
        if "<pu>" in line:
            if curMinute.isdigit() == False:
                curMinute = line.replace("<pu>", " ").replace("</pu>", " ").strip()
            continue
    return stack

def getTimeAndTemp():
    result = requests.get(url="http://new.grtcbustracker.com/bustime/map/getTimeAndTemp.jsp")

# epd.Clear()


# epd.imageblack.text("Waveshare", 5, 10, 0x00)
# epd.imagered.text("Pico_ePaper-7.5-B", 5, 40, 0xff)
# epd.imageblack.text("Raspberry Pico", 5, 70, 0x00)

# epd.imageblack.vline(10, 90, 60, 0x00)
# epd.imageblack.vline(120, 90, 60, 0x00)
# epd.imagered.hline(10, 90, 110, 0xff)
# epd.imagered.hline(10, 150, 110, 0xff)
# epd.imagered.line(10, 90, 120, 150, 0xff)
# epd.imagered.line(120, 90, 10, 150, 0xff)

# epd.imageblack.rect(10, 180, 50, 80, 0x00 )
# epd.imageblack.fill_rect(70, 180, 50, 80,0x00 )
# epd.imagered.rect(10, 300, 50, 80, 0xff )
# epd.imagered.fill_rect(70, 300, 50, 80,0xff )


# START every minute
# framebuf clear
while True:
    begin = time.time()
    try:
        ArrivalStack = getArrivalTimes()
    except Exception as e:
        ArrivalStack = []

    # epd.TurnOnDisplay()
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0x00)
    # image
    fb = []
    with open("img.bin", "rb") as f:
        fb = f.read()
    blit_image(epd.imageblack, fb, 0, 20, 400, 200)
    # Text
    epd.imageblack.text("Stop #%d" % STOPNUM, 5, 250, 0x00)
    start_y = 260
    print(ArrivalStack)
    for i, x in enumerate(ArrivalStack):
        if x[0].isdigit():
            epd.imageblack.text("Route %s (%s): %s Minutes" % (x[1], x[2], x[0]), 5, start_y + (10*i), 0x00)
        else: # assume this means the bus is due
            epd.imageblack.text("Route %s (%s): %s" % (x[1], x[2], x[0][:1].upper() + x[0][1:].lower()), 5, start_y + (10*i), 0x00)
    epd.imageblack.text("Stop #%d" % STOPNUM, 5, 250, 0x00)
    if len(ArrivalStack) == 0:
        epd.imageblack.text("No Arrivals", 5, 260, 0x00)

    epd.display()
    epd.delay_ms(5000)

    end = time.time()
    print("Time Taken: %d" % (end - begin))
    # epd.sleep()
    # D Y N A M I C time
    time.sleep(60 - (end - begin))






