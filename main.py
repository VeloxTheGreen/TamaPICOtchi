from machine import I2C, Pin
from machine_i2c_lcd import I2cLcd
from time import sleep, sleep_ms
from lcd_multisprites import *
from random import randint

#misc
field = 0
a = 0
move_row = 0
state = 0
switch = 0
prev_field = 0
count = 0

#Pin initialisierung
btn1 = Pin(1, Pin.IN, Pin.PULL_UP)
btn2 = Pin(9, Pin.IN, Pin.PULL_UP)
btn3 = Pin(15, Pin.IN, Pin.PULL_UP)

#LCD initialisierung
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq= 100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.clear()

#misc functions
def dead_print_out():
    if chargebar2.barlvl == 3 or chargebar1.barlvl == 3: # tamagotchi is dead
        lcd.move_to(0, 0)
        lcd.putstr("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        return True

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

def button2_handler(pin):#cleans poop from the screen
    lcd.move_to(0, 1)
    lcd.putstr(" ")
    sleep(0.5)
    lcd.putstr(" ")
    kacke.sadness = 0
    print("poop cleaned")

def button3_handler(pin):#puts or takes meat on the screen
    global switch
    lcd.custom_char(0, meat_bitmap1)
    lcd.move_to(1, 0)
    if meatmon.get_meat_state() == 0:
        lcd.putstr(" ")
        meatmon.set_meat_state(1)
        print("meat gone")
    else:
        lcd.putstr(meatmon.meat_chr)
        meatmon.set_meat_state(0)
        print("meat put")
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
        self.baby_switch = 0
    
    def check_if_dead(self, switch):
        dead_or_alive = False
        if switch == 3:# happens if meat is only bones##!!!!!ändern!!!!!##
            dead_or_alive = dead_print_out()
            chargebar2.change_bar_minus()
        if kacke.sadness >= 1:
            dead_or_alive = dead_print_out()
            chargebar1.change_bar_minus()
        if kacke.sadness == 0:
            chargebar1.change_bar_positive()
        if meatmon.get_meat_state() == 1:
            dead_or_alive = dead_print_out()
            chargebar2.change_bar_minus()
        happiness.change_icon(chargebar1.barlvl)
        food.change_icon(chargebar2.barlvl)
        return dead_or_alive
    
    def animation(self):
        if self.baby_switch == 0:
            self.baby_switch = 1
            lcd.putstr(babymon.baby_main)
        else:
            self.baby_switch = 0
            lcd.putstr(babymon.baby_ani)
#class meat################################################
class Meat:
    def __init__(self, meat_state):
        self.meat_chr = chr(0)
        self.meat_state = meat_state
        
    def get_meat_state(self):
        return self.meat_state
    def set_meat_state(self, new_state):
        self.meat_state = new_state
    
    def change_state(self, switch, chargebar):
        if self.meat_state == 0:
            if switch == 0:
                lcd.custom_char(0, meat_bitmap2)
                chargebar.change_bar_positive()
                switch = 1
            elif switch == 1:
                lcd.custom_char(0, meat_bitmap3)
                chargebar.change_bar_positive()
                switch = 2
            elif switch == 2:
                lcd.custom_char(0, meat_bitmap4)
                chargebar.change_bar_positive()
                count = 0
                sleep(0.3)
                kacke.poop_on_the_floor()
                switch = 3
            food.change_icon(chargebar.barlvl)
        return switch
#class chargebar###########################################
class Chargebar:
    def __init__(self, bar_number, bar_name, char, barlvl):
        self.bar_number = bar_number
        self.bar_name = bar_name
        self.chargebar_chr = char
        self.barlvl = barlvl
        
    def change_bar_minus(self):
        if self.barlvl == 0:
            lcd.custom_char((self.bar_number+1), charge_bitmap3)
            self.barlvl = 1
        elif self.barlvl == 1:
            lcd.custom_char((self.bar_number+1), charge_bitmap2)
            self.barlvl = 2
        elif self.barlvl == 2:
            lcd.custom_char((self.bar_number+1), charge_bitmap1)
            self.barlvl = 3
        print(self.bar_name + " Barlvl: " + str(self.barlvl))
        
    def change_bar_positive(self):
        if self.barlvl == 3:
            lcd.custom_char((self.bar_number+1), charge_bitmap2)
            self.barlvl = 2
        elif self.barlvl == 2:
            lcd.custom_char((self.bar_number+1), charge_bitmap3)
            self.barlvl = 1
        elif self.barlvl == 1:
            lcd.custom_char((self.bar_number+1), charge_bitmap4)
            self.barlvl = 0
        print(self.bar_name + " Barlvl: " + str(self.barlvl))
#class Manure##############################################
class Manure:
    def __init__(self, char):
        self.manure_char = char
        self.sadness = 0
        self.manure_switch = 0
    
    def get_manure_switch(self):
        return self.manure_switch
    def set_manure_switch(self, var):
        self.manure_switch = var
    def get_sadness(self):
        return self.sadness
    def count_sadness(self):
        self.sadness = self.sadness+1
    
    def poop_on_the_floor(self):
        lcd.move_to(self.manure_switch, 1)
        lcd.putstr(self.manure_char)
        self.count_sadness()
        if self.get_manure_switch() == 0:
            self.set_manure_switch(1)
        else:
            self.set_manure_switch(0)
        print("dropped poop on the floor")
#class Happiness Icon######################################
class Happiness_Icon:
    def __init__(self, icon):
        self.icon = icon
        
    def change_icon(self, barlvl):#changes happiness level
        if barlvl == 0:
            lcd.custom_char(4, happy)
        elif barlvl == 2:
            lcd.custom_char(4, neutral)
        elif barlvl == 3:
            lcd.custom_char(4, sad)
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
    
    def change_icon(self, barlvl): #changes food level
        if barlvl == 0:
            if self.food_generator == 1:
                lcd.custom_char(5, pizza1)
            elif self.food_generator == 2:
                lcd.custom_char(5, toast1)
            else:
                lcd.custom_char(5, banana1)
        elif barlvl == 1: # barely gone
            if self.food_generator == 1:
                lcd.custom_char(5, pizza2)
            elif self.food_generator == 2:
                lcd.custom_char(5, toast2)
            else:
                lcd.custom_char(5, banana2)
        elif barlvl == 2: #almost gone
            if self.food_generator == 1:
                lcd.custom_char(5, pizza3)
            elif self.food_generator == 2:
                lcd.custom_char(5, toast3)
            else:
                lcd.custom_char(5, banana3)
        elif barlvl == 3: # no food
            if self.food_generator == 1:
                lcd.custom_char(5, pizza4)
            elif self.food_generator == 2:
                lcd.custom_char(5, toast4)
            else:
                lcd.custom_char(5, banana4)
        print("changed Food Icon")
#manure####################################################
lcd.custom_char(1, manure_bitmap1)
kackchar = chr(1)
#setup charges#############################################        
lcd.custom_char(2, charge_bitmap4)
lcd.custom_char(3, charge_bitmap4)
chargebar1 = Chargebar(1, "HappinessBar", chr(2), 0)#######################
chargebar2 = Chargebar(2, "FoodBar", chr(3), 0)#######################
lcd.move_to(14,0)
lcd.putstr(chargebar1.chargebar_chr)
sleep(0.1)
lcd.putstr(chargebar2.chargebar_chr)
sleep(0.1)
#setup happiness & food####################################
lcd.custom_char(4, happy)
happiness = Happiness_Icon(chr(4))
food = Food_Icon()
lcd.move_to(14,1)
lcd.putchar(chr(4))
sleep(0.1)
lcd.putchar(chr(5))
sleep(0.1)
#initialising objects#######################
babymon = Tamagotchi(chr(6), chr(7))
meatmon = Meat(1)
kacke = Manure(kackchar)

field = 2
while True:
    lcd.move_to(field, move_row)
    lcd.putstr(" ")
    field = randint((field-1),(field+1))
    print("Field: " + str(field))
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
    babymon.animation()
    #mental state count######################    
    count = count + 1
    if (count%40) == 0:
        switch = meatmon.change_state(switch, chargebar2)
    if count >= 80:
        count = 0
        if babymon.check_if_dead(switch) == True:    
            print("dead")
            break;
    ##########################################     
    sleep(0.8)
