# Shut off robot server to enable GPIO
# Required to monitor door state and control lights.

import os

os.system("systemctl stop opentrons-robot-server")

from opentrons import protocol_api
import math
import time
import threading

metadata = {'apiLevel': '2.10'}

# global protocol
# protocol = protocol_api.ProtocolContext

# global paused
# paused = False

# paused = multiprocessing.Value('i', 0)
# print(paused)
# print(paused.value)





def run(protocol: protocol_api.ProtocolContext):
    protocol.set_rail_lights(True)
    print('DOOR STATE = ' + str(protocol.door_closed))

    global paused
    paused = False

    global done
    done = False

    def check_pause():
        global paused
        global done
        if not paused and not protocol.door_closed:
            protocol.pause()
            paused = True
        
        if paused and protocol.door_closed:
            protocol.resume()
            paused = False

        print('Door closed = ', str(protocol.door_closed))
        time.sleep(1)
        if not done:
            check_pause()

    # queue = multiprocessing.Queue()
    thread = threading.Thread(target=check_pause)
    thread.start()
    # process = threading.start_new_thread(target=check_pause)
    # process.start()
    # process.join()

    resevoir = protocol.load_labware('usascientific_96_wellplate_2.4ml_deep',8) #Contains Magnetic Beads on A1 and EB on A3.
    tiprack_7 = protocol.load_labware('opentrons_96_tiprack_300ul', 9)
    p300 = protocol.load_instrument('p300_multi', 'right', tip_racks=[tiprack_7])


    for i in range(1,2):
        p300.pick_up_tip()
        p300.aspirate(200, resevoir['A1'], rate=1)
        # p300.transfer(50, resevoir['A'+str(i)], resevoir['A'+str(i+6)], new_tip='never')
        p300.drop_tip()


    done = True
    thread.join()

    print('Protocol Complete')