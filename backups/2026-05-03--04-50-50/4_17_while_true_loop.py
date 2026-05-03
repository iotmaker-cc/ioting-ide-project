import time

start_ms = time.ticks_ms()
current_ms = 0
interval_ms = 5000

while True:
    current_ms = time.ticks_ms()
    if (current_ms - start_ms) > 5000:
        start_ms = current_ms 
        print(int(current_ms / 1000))
    