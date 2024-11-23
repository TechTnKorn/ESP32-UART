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
        cmd = uart.readline().decode('utf-8').strip().upper()  # รับคำสั่ง
        #Cleaning
        print("\r\nReceive",cmd) 
        Action = ""
        Brightness = ""
        
        #PREPARE DATA
        if cmd != '': #ถ้ามีค่าส่งมา
            if '-' in cmd: #ถ้ามี '-'
                index = cmd.find('-')
                Action = cmd[:index] #ใส่ตัวก่อนหน้าให้Action
                Brightness = int(cmd[index+1:]) #ตัวหลัง '-' ใส่Brightness
            elif cmd == 'ULTRASONIC' or cmd == 'SERVO' or cmd == 'STOP': #Actionที่ไม่ต้องมี'-'หรือBrightness
                Action = cmd[:]#ใส่หมด
            else: #ถ้าไม่มี'-' คือผิดformat(DAC,PWM)
                print("invalid syntax")

        #LED START
        #MODE SELECT
        if (Action == 'DAC' or Action == 'PWM'): #ถ้าใช้LEBตัวหลังทั้งหมดต้องเป็นตัวเลข
            if Brightness != '': #ถ้าใส่ค่ามา
                if Brightness >= 0 and Brightness <= 100:
                    print("Action:",Action)
                    print("Brightness:",Brightness)
                    if Action == 'DAC': #DAC Mode
                        reset()
                        dac_value = round(255*Brightness/100)
                        print(Action,"-",Brightness,f"({dac_value})")
                        dac.write(dac_value)
                    elif Action == 'PWM': #PWM Mode
                        reset()
                        duty_cycle = round(1023*Brightness/100)
                        print(Action,"-", Brightness,f"({duty_cycle})")
                        pwm.duty(duty_cycle)
                else:
                    print(f"Error 'Brightness' can't be {Brightness}")
                    reset()
        #LED END
            
        #ULTRASONIC START
        elif Action == 'ULTRASONIC' and Brightness == '':#PWM Mode
            reset()
            print("Action:",Action)
            while True:
                distance = sensor.distance_cm()
                print('Distance is', distance, 'cm')
                sleep(1)
                if uart.any(): 
                    break
        #ULTRASONIC END
        
        #SERVO START
        elif Action == 'SERVO' and Brightness == '': #PWM Mode
            reset()
            print("Action:",Action)
            while True:#จากLab8
                for i in range(180):
                    set_angle(servo, i)
                    sleep_ms(3)
                for i in range(180, 0, -1):
                    set_angle(servo, i)
                    sleep_ms(3)
                if uart.any():
                    break
        #SERVO END
                    
        #Actionมั่ว
        else:#มือว่างอยากกดEnterเล่นก็ไม่มีอะไร
            if cmd != '': #ใส่คำสั่งผิด
                reset()
                print(f"Don't have {cmd} command :)\n")
            
                
        
        

