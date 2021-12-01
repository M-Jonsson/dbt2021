from opentrons import protocol_api
import math
import time
import multiprocessing
from multiprocessing.pool import ThreadPool
import queue

metadata = {'apiLevel': '2.10'}

protocol = protocol_api.ProtocolContext


def run(protocol):
    global paused
    paused = False
    pool = ThreadPool()
    pool.apply_async(check_pause)
    

    resevoir = protocol.load_labware('usascientific_96_wellplate_2.4ml_deep',2) #Contains Magnetic Beads on A1 and EB on A3.
    tiprack_7 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    p300 = protocol.load_instrument('p300_multi', 'right', tip_racks=[tiprack_7])


    # for i in range(1,7):
    #     p300.pick_up_tip()
    #     p300.transfer(50, resevoir['A'+str(i)], resevoir['A'+str(i+6)], new_tip='never')
    #     p300.drop_tip()
    #     paused = True
    #     time.sleep(1)
    #     protocol.delay(seconds=30)
    #     paused = False
    #     time.sleep(0.5)

    protocol.pause()
    for i in range(1,4):
        print(i)

        p300.pick_up_tip()
        time.sleep(0.5)
        p300.transfer(50, resevoir['A'+str(i)], resevoir['A'+str(i+6)], new_tip='never')
        time.sleep(1)
        p300.drop_tip()
        time.sleep(0.5)

        

        if i == 2:
            paused = True
            protocol.pause()

def check_pause():
    while True:
        print('* * * * * * * *' + str(paused))
        
        if paused:
            print('*** PROTOCOL IS PAUSED ***')
            protocol.resume()
        else:
            print('*** PROTOCOL IS RUNNING ***')

        time.sleep(0.1)
        
