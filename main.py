from machine import Pin, DAC, PWM, UART
from hcsr04 import HCSR04
from time import sleep,sleep_ms
#LED
dac = DAC(Pin(25)) # create an DAC object acting on a pin (Green)
frequency = 5000
pwm = PWM(Pin(26), frequency) # a frequency of 5000 Hz (Yellow)
#UART
uart = UART(2, 115200) # Create the uart object in port 2, Rx=GPIO 16, Tx=GPIO 17
uart.init(timeout=5000) # set timeout=2000
#ULTRASONIC
sensor = HCSR04(trigger_pin=5, echo_pin=18, echo_timeout_us=20000)
#SERVO
servo = PWM(Pin(14), freq=40)

#RESET SYSTEM
def reset():
    #LED
    dac.write(0)
    pwm.duty(0)
    
#INIT
reset()

#SERVO ROTATION Function
def set_angle(device, angle):
    while angle < 0:
        angle += 180
    while angle > 180:
        angle -= 180
    duty = int(500_000 + angle * 2_000_000 / 180)
    device.duty_ns(duty)

while True:
    if uart.any():
        #SETUP
        cmd = uart.readline().decode('utf-8').strip().upper()  # รับคำสั่ง
        #Cleaning
        print("\r\nReceive",repr(cmd))
        Action = ""
        Brightness = ""
        if '\x08' in cmd : #ถ้าตัวแรกเป็น\x08
            #print("detect \x08")
            while '\x08' in cmd:
                index = cmd.find('\x08')  # หา index ของ backspace
                '''print("index",index)
                for i in range(len(cmd)):
                    print(cmd[i])'''
                if index > 0:  # ถ้ามีตัวอักษรก่อนหน้า
                    # ลบตัวอักษรก่อนหน้าและ backspace
                    cmd = cmd[:index-1] + cmd[index+1:]
                else:  # ถ้า backspace อยู่ที่ตำแหน่งแรก
                    # ลบเฉพาะ backspace
                    cmd = cmd[index+1:]
        cmd = cmd.replace('-','').replace(' ','') #ลบขีดและเว้นวรรค
        if cmd == '':
            print("not detect cmd")
        
        #PREPARE DATA
        for index in range(len(cmd)): # หาตัวแบ่งระว่างActionและBrightness
            if cmd[index].isdigit(): #ถ้าเจอตัวเลข
                Action = cmd[:index] #ใส่ตัวก่อนหน้าให้Action
                Brightness = cmd[index:] #ใส่ค่าที่เหลือให้Brightness
                break #แบ่งเสร็จก็ออกลูป
            else:#ถ้าไม่มีตัวเลข("ultrasonic","servo")
                Action = cmd[:] #ใส่หมด
                
        #Show Action, Brightness
        #if cmd != '':
            #print("Action:",repr(Action))                
                
        #LED START
        #MODE SELECT
        if (Action == 'DAC' or Action == 'PWM'): #ถ้าใช้LEBตัวหลังทั้งหมดต้องเป็นตัวเลข
            print("Action:",repr(Action)) 
            if Brightness != '': #ถ้าใส่ค่ามา
                if Brightness.isdigit(): #เป็นตัวเลขทั้งหมดรึป่าว
                    Brightness = int(Brightness) #แปลงเป็นตัวเลข
                    print("Brightness:",repr(str(Brightness)))
                    if Brightness >= 0 and Brightness <= 100: #ใส่Brightnessแปลกๆ
                        if Action == 'DAC': #DAC Mode
                            reset()
                            dac_value = round(255*Brightness/100)
                            print(Action,"-",Brightness,f"({dac_value})")
                            dac.write(dac_value)
                        elif Action == 'PWM': #PWM Mode
                            reset()
                            duty_cycle = round(1023*Brightness/100)
                            print(Action,"-", Brightness,f"({duty_cycle})")
                            pwm.duty(duty_cycle) # increase the duty cycle by 1
                    else:#ถ้าเลขเกิน
                        print(f"Enter value between 0 - 100")
                        reset()
                else: #ถ้าเป็นตัวอักษร
                    print(f"Enter value between 0 - 100")
                    reset()
            else: #ถ้าไม่ใส่
                print(f"Enter value between 0 - 100")
                reset()
        #LED END
            
        #ULTRASONIC START
        elif Action == 'ULTRASONIC': #PWM Mode
            reset()
            print("Action:",repr(Action)) 
            if Brightness != '': #แถมBrightnessมาด้วย
                print(f"Brightness shouldn't have a value ({Brightness}) in {Action}\nBut... ok...")
            while True:
                distance = sensor.distance_cm()
                print('Distance is', distance, 'cm')
                sleep(1)
                if uart.any(): 
                    break
        #ULTRASONIC END
        
        #SERVO START
        elif Action == 'SERVO': #PWM Mode
            reset()
            print("Action:",repr(Action)) 
            if Brightness != '': #แถมBrightnessมาด้วย
                print(f"Brightness shouldn't have a value ({Brightness}) in {Action}\nBut... ok...")
            while True:
                for i in range(180):
                    set_angle(servo, i)
                    sleep_ms(3)
                for i in range(180, 0, -1):
                    set_angle(servo, i)
                    sleep_ms(3)
                if uart.any():
                    break
        #SERVO END
                    
        #STOP
        elif Action == 'STOP' and Brightness == '': #PWM Mode
            print("Action:",repr(Action)) 
            print("System STOP")
            reset()
        
        #Actionมั่ว
        else:#มือว่างอยากกดEnterเล่นก็ไม่มีอะไร
            if cmd != '': #ใส่คำสั่งผิด
                reset()
                print(f"Don't have {cmd.upper()} command :)")
                print("Restart")