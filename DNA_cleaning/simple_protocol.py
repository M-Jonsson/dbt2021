####################################
#   Protocol for DNA purification of 8-96 samples with magnetic beads, using Opentons OT-2 pipetting robot.
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
#           v1.0 2021-11-XX: First public version.
#
####################################

from opentrons import protocol_api
import math
import time
import multiprocessing
import queue
metadata = {'apiLevel': '2.10'}

def get_values(*names):
    """
    Function to help load magnetic module.
    """
    import json
    _all_values = json.loads("""{"mag_mod":"magnetic module"}""")
    return [_all_values[n] for n in names]

def custom_mix(pipette, repetitions, volume, well, bottom_aspirate, bottom_dispense):
    """
    A customized mix function that makes the robot aspirate 
    the liquid at one hight i the well, and then dispense it 
    at another hight in the same well, with a given numer of repititions.

        Parameters:
            pipette (pipette):          The pipette to use.
            repetitions (int):          Number of repetitions.
            volume (float):             Volume to aspirate/dispense.
            well (well):                The well where the mixing shall take place.
            bottom_aspirate (float):    Distance in mm above the bottom of the well
                                        to aspirate from.
            bottom_dispense (float):    Distance in mm above the bottom of the well
                                        to dispense at.
        
        Returns:
            Nothing.
    """
    pipette.well_bottom_clearance.aspirate = bottom_aspirate
    pipette.well_bottom_clearance.dispense = bottom_dispense
    for i in range(repetitions):
        pipette.aspirate(volume, well, 1)
        pipette.dispense(volume, well, 1)
    pipette.well_bottom_clearance.aspirate = 1
    pipette.well_bottom_clearance.dispense = 1 
  
def stepwise_dispense(pipette, volume, location_dispense, steps):
    """
    A customized dispense function that makes the robot dispense 
    the liquid stepwise, by dispensing small amounts of liquid at the time
    and inbetween dispenses move upwards such that the pipette 
    is always close to the surface of the liquid.

        Parameters:
            pipette (pipette):          The pipette to use.
            volume (float):             Total volume to dispense.
            well (well):                The well where to dispense.
            steps (int):                Number of steps to divide dispense into.
        
        Returns:
            Nothing.
    """
    step_volume = volume/steps
    #pipette.flow_rate.dispense=30
    for i in range(steps):
        volume_added = (i+1)*step_volume #total volume added efter the step is done
        #polyn. describing relationship between height and volume
        #applies only to 200ul 96-well PCR plate from bio rad
        dispense_height = (-2.5+((2.5**2)+4.9+1.42*volume_added)**(1/2)) + 1 #additional 1 mm above est. level
        pipette.dispense(step_volume, location_dispense.bottom(z=dispense_height))
    #pipette.flow_rate.dispense = 300


####################################
#============RUN FUNCTION===========
####################################

def run(protocol: protocol_api.ProtocolContext):

    #Define and load all labware.

    is_paused = False
    queue = multiprocessing.Queue()
    process = PauseListener(queue)
    process.start()


    [mag_mod] = get_values("mag_mod")
    mag_deck = protocol.load_module(mag_mod, '1')
    sample_plate = mag_deck.load_labware('biorad_96_wellplate_200ul_pcr') #Contains the samples and are mounted on megnetic module.
    mag_deck.disengage()
    
    resevoir = protocol.load_labware('usascientific_96_wellplate_2.4ml_deep',2) #Contains Magnetic Beads on A1 and EB on A3.
    
    #Set tip racks and pipettes.
    tiprack_7 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    tiprack_8 = protocol.load_labware('opentrons_96_tiprack_300ul', 8) 
    tiprack_9 = protocol.load_labware('opentrons_96_tiprack_300ul', 9)
    tiprack_10 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)
    p300 = protocol.load_instrument('p300_multi', 'right', tip_racks=[tiprack_8, tiprack_9, tiprack_10, tiprack_7])
    

    #########################
    ###START PROTOCOL########
    #########################

    #Add magnetic beads to samples, and mix.
    # columns = math.ceil(no_samples / 8) #calculates how many columnes are filled
    columns = 2
    volBeads = vol_samples * ratio 

    print('* * * * BEFORE PAUSE * * * *')
    
    is_paused = True


    is_paused = False
    for i in range(1,columns+1):
        p300.pick_up_tip()
        if (columns == 1 or columns == 6):
            p300.flow_rate.aspirate=9
            p300.flow_rate.dispense=9            
            # custom_mix(resevoir['A1'], 30, 15, p300, 3, 6)         
        p300.flow_rate.aspirate=60
        p300.flow_rate.dispense=60
        p300.transfer(volBeads, resevoir['A1'].bottom(z=3), sample_plate['A' + str(i)], blow_out=(True), blowout_location='destination well', new_tip='never') 
        custom_mix(p300, 15, vol_samples+volBeads-5, sample_plate['A' + str(i)], 0.6, 3.5)
        p300.drop_tip()
    
    

    ###########
    ### END ###
    ###########


class PauseListener(multiprocessing.Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
    
    def run(self):
        while True:
            print('* * * Pause state = ' + str(is_paused))
            time.sleep(1)

is_paused = False
#User input variables.
# Default values
no_samples = 20
vol_samples = 20
ratio = 0.8
cleanings = 1
vol_EB= 15
# New values from user:
no_samples = 20
vol_samples = 20.0
ratio = 1.0
cleanings = 1
vol_EB = 20.0