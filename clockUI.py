import machine, rp2, network, ntptime, time, ssd1306, math

# ---------- CONFIG ----------
SSID = "Batman"
PASSWORD = "iambatman"
TZ_OFFSET = 6 * 3600  

# ---------- OLED SETUP ----------
i2c = machine.I2C(1, scl=machine.Pin(15), sda=machine.Pin(14))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# ---------- BOOTSEL BUTTON LOGIC ----------
def bootsel_button():
    return (rp2.bootsel_button() == 1)

# ---------- WIFI & TIME SYNC ----------
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

for _ in range(20):
    if wlan.isconnected(): break
    time.sleep(0.5)

try:
    ntptime.settime()
except:
    pass

# ---------- MODERN FONT ----------
FONT = {
    "0":[0x3E,0x51,0x49,0x45,0x3E], "1":[0x00,0x42,0x7F,0x40,0x00],
    "2":[0x62,0x51,0x49,0x49,0x46], "3":[0x22,0x49,0x49,0x49,0x36],
    "4":[0x18,0x14,0x12,0x7F,0x10], "5":[0x27,0x45,0x45,0x45,0x39],
    "6":[0x3C,0x4A,0x49,0x49,0x30], "7":[0x01,0x71,0x09,0x05,0x03],
    "8":[0x36,0x49,0x49,0x49,0x36], "9":[0x06,0x49,0x49,0x29,0x1E],
    ":":[0x00,0X36,0x36,0X00],
    "A":[0x7E,0x11,0x11,0x11,0x7E], "P":[0x7F,0x09,0x09,0x09,0x06],
    "M":[0x7F,0x02,0x0C,0x02,0x7F]
}

def draw_big_colored(text, x, y, scale, color):
    # Ensure pixels are at least 1x1 even if scale is 1
    pixel_size = max(1, scale - 1) if scale > 1 else 1
    
    for ch in text:
        if ch == " ":
            x += (2 * scale)
            continue
            
        if ch not in FONT: continue
        data = FONT[ch]
        char_width = len(data)
        
        for col in range(char_width):
            for row in range(7):
                if data[col] & (1 << row):
                    # Use pixel_size here
                    oled.fill_rect(x + col*scale, y + row*scale, pixel_size, pixel_size, color)
        
        if ch == ":":
            x += (char_width * scale) + 2
        else:
            x += (char_width * scale) + 2 # Tightened gap for Scale 1
        
# ---------- UI 1: REFINED SIDE ELEMENTS (Dark Mode) ----------
def draw_ui_classic(tm, h, m, s, suffix):
    oled.fill(0) # Black Background
    
   # 1. Top Bar Full Capsule (White)
    oled.fill_rect(0, 0, 128, 12, 1)   
    
    # 2. Greeting (Black Text on White)
    oled.text("HI RATUL", 3, 2, 0)   
    
    # 3. WiFi Signal Bars (Now Black on White)
    if wlan.isconnected():
        # Using color '0' so it's visible inside the white capsule
        for i in range(4): 
            oled.fill_rect(112 + (i*4), 8-(i*2), 2, 2+(i*2), 0)
    else: 
        oled.text("OFF", 102, 2, 0) # Black text for "OFF"
    
    # Line separating the bar from the clock
   
    
    # 2. Big Time (Scale 4) - Forced 04 : 34 format
    # Using {:02d} for leading zero on hour
    time_str = "{:02d}:{:02d}".format(h, m)
    
    # Starting at x=1 to prevent overflow with the new wider string
    draw_big_colored(time_str, 1, 17, 4, 1)
    
  # 3. Sidebar (Now visible at Scale 1)
    # Moved to x=104 so they don't fall off the edge
    draw_big_colored(suffix, 111, 19 , 1, 1) 
    draw_big_colored("{:02d}".format(s), 107, 31, 2, 1)
    
   # 4. Date Pill (Format: SAT 02/03/25)
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    day_name = days[tm[6]]
    # tm[0] is year (e.g., 2025). % 100 gets the last two digits (25)
    short_year = tm[0] % 100
    date_str = "{} {:02d}/{:02d}/{:02d}".format(day_name, tm[2], tm[1], short_year)
    
    oled.fill_rect(0, 52, 128, 12, 1) 
    oled.text(date_str, 16, 54, 0) # Centered better for shorter date
    
    # 5. Progress Bar (Seconds)
    oled.hline(0, 48, int((s / 60) * 128), 1)
    
    

    # UI2

frame = 0

def draw_ui_stack(tm, h, m, s, suffix):
    global frame
    frame += 1
    
    # 1. Background (White)
    oled.fill(1)
    
    # 2. Top Bar (Static for better readability)
    oled.text("FLY HIGH ", 5, 2, 0)
    oled.hline(0, 12, 128, 0)

    # 3. Time Stack (Scaled down to 3)
    # Centered slightly better for the new size
    draw_big_colored("{:02d}".format(h), 12, 16, 3, 0)
    draw_big_colored("{:02d}".format(m), 12, 40, 3, 0)
    
    # 4. Sidebar Divider
    oled.vline(62, 12, 52, 0)
    
    # 5. Right Side Info (Adjusted to fit inside 128px)
    # AM/PM Badge
    oled.fill_rect(70, 16, 22, 10, 0)
    oled.text(suffix, 72, 17, 1)
    
    # Large Seconds
    draw_big_colored("{:02d}".format(s), 70, 28, 2, 0)
    
    # 6. Static Date (No more bouncing)
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    oled.text(days[tm[6]], 70, 46, 0)
    oled.text("{:02d}/{:02d}".format(tm[2], tm[1]), 70, 55, 0)

# ---------- MAIN LOOP ----------
ui_mode = 0
last_btn_state = False

while True:
    current_btn_state = bootsel_button()
    if current_btn_state and not last_btn_state:
        ui_mode = (ui_mode + 1) % 2
    last_btn_state = current_btn_state

    t = time.time() + TZ_OFFSET
    tm = time.localtime(t)
    h_12 = tm[3] % 12 or 12
    suffix = "PM" if tm[3] >= 12 else "AM"

    if ui_mode == 0:
        draw_ui_classic(tm, h_12, tm[4], tm[5], suffix)
    else:
        draw_ui_stack(tm, h_12, tm[4], tm[5], suffix)
        
    oled.show()
    time.sleep(0.05) # Smooth animation speed
