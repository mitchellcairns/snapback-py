import hid
import matplotlib.pyplot as plt
import numpy as np

procon_device = int(0x2009)
procon_vendor = int(0x057E)

print("Looking for Pro Controller:")

dev = hid.enumerate()
conch = ""

connected_device = ""
output_buffer_size = 20
output_buffer = [0] * output_buffer_size

output_buffer_index = 0

for x in dev:
    pid = x['product_id']
    vid = x['vendor_id']
    if (vid==procon_vendor and pid==procon_device):
        print("Pro Controller connected. Please flick your stick :)")
        connected_device = "Pro Controller"

def parseprocondata(byte):
    data_out = []
    try: 
        data_out.insert(0, byte[6] | ((byte[7] & 0xF) << 8))
        data_out.insert(1, (byte[7] >> 4) | (byte[8] << 4))
    except:
        data_out.insert(0, 0)
        data_out.insert(0, 0)

    return data_out

if connected_device == "Pro Controller":
    dev = hid.device()
    dev.open(procon_vendor, procon_device)

    high_threshold = 3450
    low_threshold = 550
    direction_tracker = 0

    change_mode_msg = [0x01, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3, 0x30]

    dev.write(change_mode_msg)

    while True:
        dat = dev.read(60)
        out = parseprocondata(dat)

        output_buffer[output_buffer_index] = out[0]
        
        if (out[0] > high_threshold and direction_tracker == 0):
            direction_tracker = 1
        elif (out[0] < 1900 and direction_tracker == 1):
            direction_tracker = 2
        elif(out[0] >= 2000 and direction_tracker == 2):
            print("Snapback detected POSITIVE")
            direction_tracker = 100
        elif(out[0] < low_threshold and direction_tracker == 0):
            direction_tracker = -1
        elif(out[0] > 2100 and direction_tracker == -1):
            direction_tracker = -2
        elif(out[0] <= 2000 and direction_tracker == -2):
            print("Snapback Detected NEGATIVE")
            direction_tracker = 100

        if direction_tracker == 100:
            plt.xlabel('Ticks')
            plt.ylabel('Stick Value')
            plt.xlim(0, output_buffer_size)
            plt.ylim(0,4000)
            plt.plot(list(range(0, output_buffer_size)), output_buffer)
            plt.show()
            direction_tracker = 0

        output_buffer_index += 1
        if (output_buffer_index > output_buffer_size-1):
            output_buffer_index = 0

        
        
    