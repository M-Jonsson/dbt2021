####################################
#   qPCR preparation protocl using the Opentons OT-2 pipetting robot.
#
#   Authors: Group 5 Design-Build-Test 2021:
#           Elsa Renström    
#           Agata Jasna
#           Tiam Fitoon
#           Mathias Jonsson
#           Johan Lehto
#           Johan Lundberg 
#      
#   Version information:
#           v1.0 2021-11-XX: First protocol version.
#           v1.1 2021-12-16: Added documentation.
#           v1.2 2021-12-21: Ready for external use.
#
####################################

import json
from opentrons import protocol_api
import time
import threading

metadata = {'apiLevel': '2.10'}

####################################
#============RUN FUNCTION===========
####################################

def run(protocol: protocol_api.ProtocolContext):

    # Load custom labware from file
    path_to_custom = '/data/user_storage/own_24_tuberack_1500ul.json'
    if protocol.is_simulating():
        path_to_custom = 'custom labware\\own_24_tuberack_1500ul.json'
    with open(path_to_custom) as labware_file:
        labware_def = json.load(labware_file)

    # Add custom labware to deck
    tube_rack1 = protocol.load_labware_from_definition(labware_def, 8)
    tube_rack2 = protocol.load_labware_from_definition(labware_def, 9)
    tube_rack3 = protocol.load_labware_from_definition(labware_def, 4)
    tube_rack4 = protocol.load_labware_from_definition(labware_def, 5)
    tube_rack5 = protocol.load_labware_from_definition(labware_def, 6)
    tube_rack6 = protocol.load_labware_from_definition(labware_def, 1)
    tube_rack7 = protocol.load_labware_from_definition(labware_def, 2)
    tube_rack8 = protocol.load_labware_from_definition(labware_def, 3)

    tube_racks = {
        'Tube rack 1': tube_rack1, 
        'Tube rack 2': tube_rack2, 
        'Tube rack 3': tube_rack3, 
        'Tube rack 4': tube_rack4, 
        'Tube rack 5': tube_rack5, 
        'Tube rack 6': tube_rack6,
        'Tube rack 7': tube_rack7,
        'Tube rack 8': tube_rack8}

    # Add standard labware
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_10ul', 10)
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_10ul', 7)
    p10 = protocol.load_instrument('p10_single', 'left', tip_racks=[tiprack_1, tiprack_2])

    # Note: There seems to be an error in the opentrons labware library
    # where the combined aluminium block + 200ul pcr plate has the wrong height.
    # Instead, the combined aluminium block + 100ul pcr plate has a height 
    # in the library within 0.1mm of a real block with a 200ul PCR plate
    # (tested on 200ul BioRad and 200ul Armadillo plates).
    # In other words, the protocol uses a 200ul plate despite telling the robot otherwise. 
    well_plate = protocol.load_labware('opentrons_96_aluminumblock_nest_wellplate_100ul', 11)

    protocol.set_rail_lights(True)
    
    #Multithreded method to pause the protocol if the door of the OT-2 is opened. 
    global paused
    paused = False
    global done
    done = False

    def check_pause():
        """
        Pause function that checks if the robot door is closed or not, if it is open the protocol is paused
        and you have to close the door again to resume.

        Parameters:
            None.
        
        Returns:
            Nothing.
        """
        global paused
        global done
        if not paused and not protocol.door_closed:
            protocol.pause()
            paused = True
        if paused and protocol.door_closed:
            protocol.resume()
            paused = False
        if paused and not protocol.door_closed:
            print('Protocol paused. Close the door to the robot to resume.')

        time.sleep(1)
        # Check if the main thread is still alive or if the run has been stopped by ctrl+C
        run_canceled = not threading.main_thread().is_alive()
        if not done and not run_canceled:
            check_pause()

    thread = threading.Thread(target=check_pause)
    thread.start()

    #########################
    ###START PROTOCOL########
    #########################

    for mm in mastermix_destination.keys():
        p10.pick_up_tip()
        for well in mastermix_destination[mm]:
            tube_rack = tube_racks[mastermix_source[mm][0]]
            p10.aspirate(6, tube_rack[mastermix_source[mm][1]])
            p10.dispense(7, well_plate[well]) #Dispense more than aspirated to minimize liquid left in the pipette. 
        p10.drop_tip()

    for sample in sample_destination.keys():
        for well in sample_destination[sample]:
            tube_rack = tube_racks[sample_source[sample][0]]
            p10.transfer(4, tube_rack[sample_source[sample][1]], well_plate[well])

    for standard in standard_destination.keys():
        for well in standard_destination[standard]:
            tube_rack = tube_racks[standard_source[standard][0]]
            p10.transfer(4, tube_rack[standard_source[standard][1]], well_plate[well])

    #Some finnishing stuff.
    done = True
    thread.join()

    print('Protocol Complete')
    