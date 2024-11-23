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

#SERVO ROTATION
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
        cmd = uart.readline().decode('utf-8').strip()  # รับคำสั่ง
        cmd = cmd.replace('-','').replace(' ','') #ลบขีดและเว้นวรรค
        #Reset
        if cmd != '':
            Action = ""
            Brightness = ""
        #PREPARE DATA
        for cmd_index in range(len(cmd)): # หาตัวแบ่งระว่างActionและBrightness
            if cmd[cmd_index].isdigit(): #ถ้าเจอตัวเลข
                Action = cmd[:cmd_index].upper() #ใส่ตัวก่อนหน้าให้Action
                if cmd[cmd_index:].isdigit(): #ถ้าตัวหลังทั้งหมดเป็นตัวเลข
                    Brightness = int(cmd[cmd_index:]) #ใส่ค่าให้Brightness
                break #แบ่งเสร็จก็ออกลูป
            else:#ถ้าไม่มีตัวเลข("ultrasonic","servo")
                Action = cmd[:].upper() #ใส่หมด
        #Show Action, Brightness
        if cmd != '':
            print("Action:",repr(Action))
            print("Brightness:",repr(str(Brightness)))
        #LED START
        #MODE SELECT
        if Action == 'DAC': #DAC Mode
            reset()
            if Brightness == '' or Brightness < 0 or Brightness > 100: #ใส่Brightnessแปลกๆ/ไม่ใส่
                print(f"ERROR!!\nEnter value between 0 - 100")
            else:
                dac_value = round(255*Brightness/100)
                print(Action,"-",Brightness,f"({dac_value})")
                dac.write(dac_value)
        elif Action == 'PWM': #PWM Mode
            reset()
            if Brightness == '' or Brightness < 0 or Brightness > 100: #ใส่Brightnessแปลกๆ/ไม่ใส่
                print(f"ERROR!!\nEnter value between 0 - 100")
            else:
                duty_cycle = round(1023*Brightness/100)
                print(Action,"-", Brightness,f"({duty_cycle})")
                pwm.duty(duty_cycle) # increase the duty cycle by 1
        #LED END
            
        #ULTRASONIC START
        elif Action == 'ULTRASONIC': #PWM Mode
            reset()
            if Brightness != '': #แถมBrightnessมาด้วย
                print(f"Brightness shouldn't have a value ({Brightness}) in {Action}\nBut... ok...")
            while True:
                distance = sensor.distance_cm()
                print('Distance is', distance, 'cm')
                sleep(1)
                if uart.any(): 
                    #if cmd != '' :
                        break
        #ULTRASONIC END
        
        #SERVO START
        elif Action == 'SERVO' and Brightness == '': #PWM Mode
            reset()
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
            print("System STOP")
            reset()
        #Actionมั่ว
        else:#มือว่างอยากกดEnterเล่นก็ไม่มีอะไร
            if cmd != '': #ใส่คำสั่งผิด
                reset()
                print(f"Don't have {cmd} command :)")