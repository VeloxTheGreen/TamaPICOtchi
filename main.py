from machine import I2C, Pin
from machine_i2c_lcd import I2cLcd
from time import sleep, sleep_ms
from lcd_multisprites import *
from random import randint

# misc
field = 0
a = 0
manure_switch = 0
move_row = 0
state = 0
switch = 0
prev_field = 0
baby_switch = 0
count = 0
hunger = 0

#Pin initialisierung
btn1 = Pin(0, Pin.IN, Pin.PULL_UP)
btn2 = Pin(14, Pin.IN, Pin.PULL_UP)
btn3 = Pin(9, Pin.IN, Pin.PULL_UP)

#LCD initialisierung
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq= 100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.clear()

#Button-handler
def button1_handler(pin):
    global state
    if state == 0:
        state = 1
        lcd.display_off()
        lcd.backlight_off()
    else:
        state = 0
        lcd.display_on()
        lcd.backlight_on()

def button2_handler(pin):
    lcd.move_to(0, 1)
    lcd.putstr(" ")
    sleep(0.5)
    lcd.putstr(" ")

def button3_handler(pin):
    global switch
    lcd.custom_char(0, meat_bitmap1)
    lcd.move_to(1, 0)
    if meatmon.get_meat_state() == 0:
        lcd.putstr(" ")
        meatmon.set_meat_state(1)
    else:
        lcd.putstr(meatmon.meat_chr)
        meatmon.set_meat_state(0)
        switch = 0

btn1.irq(trigger=Pin.IRQ_FALLING, handler=button1_handler)
btn2.irq(trigger=Pin.IRQ_FALLING, handler=button2_handler)
btn3.irq(trigger=Pin.IRQ_FALLING, handler=button3_handler)
#class tamagotchi##########################################
class Tamagotchi:
    def __init__(self, baby_main, baby_ani):
        baby_generator = randint(1, 4)
        if baby_generator == 1:
            lcd.custom_char(6, botamon_main)
            lcd.custom_char(7, botamon_ani)
        elif baby_generator == 2:
            lcd.custom_char(6, yuramon_main)
            lcd.custom_char(7, yuramon_ani)
        elif baby_generator == 3:
            lcd.custom_char(6, punimon_main)
            lcd.custom_char(7, punimon_ani)
        elif baby_generator == 4:
            lcd.custom_char(6, zurumon_main)
            lcd.custom_char(7, zurumon_ani)
        
        self.baby_main = baby_main
        self.baby_ani = baby_ani
    
    def check_if_dead(self, switch):
        if switch == 3 or meatmon.get_meat_state() == 1:
            if chargebar2.change_bar() == True: # tamagotchi is dead
                lcd.move_to(0, 0)
                lcd.putstr("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                return True
        food.change_icon()
        return False
#class meat################################################
class Meat:
    def __init__(self, meat_state):
        self.meat_chr = chr(0)
        self.meat_state = meat_state
        
    def get_meat_state(self):
        return self.meat_state
    def set_meat_state(self, new_state):
        self.meat_state = new_state
    
    def change_state(self, switch):
        global hunger
        global manure_switch
        if self.meat_state == 0:
            if switch == 0:
                lcd.custom_char(0, meat_bitmap2)
                if hunger == 3:
                    lcd.custom_char(3, charge_bitmap2)
                    hunger = 2
                switch = 1
            elif switch == 1:
                lcd.custom_char(0, meat_bitmap3)
                if hunger == 2:
                    lcd.custom_char(3, charge_bitmap3)
                    hunger = 1
                switch = 2
            elif switch == 2:
                lcd.custom_char(0, meat_bitmap4)
                if hunger == 1:
                    lcd.custom_char(3, charge_bitmap4)
                    hunger = 0
                count = 0
                sleep(0.3)
                lcd.move_to(manure_switch, 1)
                lcd.putstr(manure)
                if manure_switch == 0:
                    manure_switch = 1
                else:
                    manure_switch = 0
                switch = 3
            food.change_icon()
        return switch
#class chargebar###########################################
class Chargebar:
    def __init__(self, bar_number, char):
        self.bar_number = bar_number
        self.chargebar_chr = char
        
    def change_bar(self):
        global hunger
        if hunger == 0:
            lcd.custom_char((self.bar_number+1), charge_bitmap3)
            hunger = 1
        elif hunger == 1:
            lcd.custom_char((self.bar_number+1), charge_bitmap2)
            hunger = 2
        elif hunger == 2:
            lcd.custom_char((self.bar_number+1), charge_bitmap1)
            hunger = 3
        elif hunger == 3:
            return True
        return False
#class Food Icon###########################################
class Food_Icon:
    def __init__(self):
        self.food_generator = randint(1, 3)
        
        if self.food_generator == 1:
            lcd.custom_char(5, pizza1)
        elif self.food_generator == 2:
            lcd.custom_char(5, toast1)
        else:
            lcd.custom_char(5, banana1)
    
    def change_icon(self): #changes food level
        global hunger
        if hunger == 0:
            if self.food_generator == 1:
                lcd.custom_char(5, pizza1)
            elif self.food_generator == 2:
                lcd.custom_char(5, toast1)
            else:
                lcd.custom_char(5, banana1)
        elif hunger == 1: # barely gone
            if self.food_generator == 1:
                lcd.custom_char(5, pizza2)
            elif self.food_generator == 2:
                lcd.custom_char(5, toast2)
            else:
                lcd.custom_char(5, banana2)
        elif hunger == 2: #almost gone
            if self.food_generator == 1:
                lcd.custom_char(5, pizza3)
            elif self.food_generator == 2:
                lcd.custom_char(5, toast3)
            else:
                lcd.custom_char(5, banana3)
        elif hunger == 3: # no food
            if self.food_generator == 1:
                lcd.custom_char(5, pizza4)
            elif self.food_generator == 2:
                lcd.custom_char(5, toast4)
            else:
                lcd.custom_char(5, banana4)
#manure####################################################
lcd.custom_char(1, manure_bitmap1)
manure = chr(1)
#setup charges#############################################        
lcd.custom_char(2, charge_bitmap4)
lcd.custom_char(3, charge_bitmap4)
chargebar1 = Chargebar(1, chr(2))####
chargebar2 = Chargebar(2, chr(3))####
lcd.move_to(14,0)
lcd.putstr(chargebar1.chargebar_chr)
sleep(0.1)
lcd.putstr(chargebar2.chargebar_chr)
sleep(0.1)
#setup happiness & food####################################
lcd.custom_char(4, happiness)
food = Food_Icon()
lcd.move_to(14,1)
lcd.putchar(chr(4))
sleep(0.1)
lcd.putchar(chr(5))
sleep(0.1)
#initialising objects#######################
babymon = Tamagotchi(chr(6), chr(7))
meatmon = Meat(1)

field = 2
while True:
    lcd.move_to(field, move_row)
    lcd.putstr(" ")
    field = randint((field-1),(field+1))
    print(field)
    #field movement##########################  
    if field <=1:
        field = 2
    elif field >= 14:
        field = field-1
    
    if prev_field == field:
        move_row = randint((a), (a+1))
    prev_field = field
    lcd.move_to(field, move_row)
    #baby animation##########################    
    if baby_switch == 0:
        baby_switch = 1
        lcd.putstr(babymon.baby_main)
    else:
        baby_switch = 0
        lcd.putstr(babymon.baby_ani)
    #mental state count######################    
    count = count + 1
    if (count%5) == 0:
        switch = meatmon.change_state(switch)
    if count >= 80:
        count = 0
        if babymon.check_if_dead(switch) == True:    
            break;
    ##########################################     
    sleep(0.8)
