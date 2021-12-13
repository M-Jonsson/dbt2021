####################################
#   Protocol for DNA purification of 1-8 samples with magnetic beads, using Opentons OT-2 pipetting robot.
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
#           v1.1 2021-12-10: Refined after quality controls.
#
####################################

from opentrons import protocol_api
from opentrons.types import Point
import time
import threading
metadata = {'apiLevel': '2.10'}


####################################
#========INTERNAL FUNCTIONS=========
####################################

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
    
def stepwise_dispense(pipette, volume, well, steps):
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
    for i in range(steps):
        volume_added = (i+1)*step_volume #total volume added efter the step is done
        #polyn. describing relationship between height and volume
        #applies only to 200ul 96-well PCR plate from bio rad
        dispense_height = (-2.5+((2.5**2)+4.9+1.42*volume_added)**(1/2)) + 1 #additional 1 mm above est. level
        pipette.dispense(step_volume, well.bottom(z=dispense_height))

class Pipette:
    """
    A customized pipette class for picking up less than 8 tips on the multichannel pipette.
    Contains all the required information, orders the tips it will use, and picks them
    up in that order.

        Attributes:
            pipette (pipette):          The pipette to use.
            tip_rack (list[Labwear]):   List of tipracks to use.
            tip_count (int):            Counter how many times tips have been picked up.
            tips_ordered (list):        List of where to pick up tips.
        
        Methods:
            pick_up():
                Picks up correct number of tips from the correct place on the tiprack.
    """
    def __init__(Pipette, protocol, pipette, tip_rack):
        """
        Constructs all the necessary attributes for the Pipette object and orders the tips
        it will use.

        Parameters:
            protocol:                   --
            pipette (pipette):          The pipette to use.
            tip_rack (list[Labwear]):   List of tipracks to use.
        
        Returns:
            Nothing.
        """
        #Set attributes.
        Pipette.pipette = pipette
        Pipette.tip_rack = tip_rack
        Pipette.tip_count = 0
        Pipette.tips_ordered = []

        #Less than 8-settings.
        per_tip_pickup_current = .125   # (current required for picking up one tip, do not modify)
        pick_up_current = no_samples*per_tip_pickup_current
        
        protocol._implementation._hw_manager.hardware._attached_instruments[
        pipette._implementation.get_mount()
        ].update_config_item('pick_up_current', pick_up_current)
        Pipette.tips_ordered = [
        tip for rack in tip_rack
            for row in rack.rows()[    
            len(rack.rows())
            -no_samples::-1*no_samples]
            for tip in row]
    
    def pick_up(Pipette):
        """
        A customized pick up tip function that makes the robot pick up
        the correct number of tips (1-8) with the multichannel pipette, 
        from a premade order.

        Parameters:
            None.
        
        Returns:
            Nothing.
        """
        Pipette.pipette.pick_up_tip(Pipette.tips_ordered[Pipette.tip_count])
        Pipette.tip_count += 1

        


####################################
#============RUN FUNCTION===========
####################################

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

        print(str(protocol.door_closed))
        time.sleep(1)
        if not done:
            try:
                check_pause()
            except KeyboardInterrupt:
                pass

    thread = threading.Thread(target=check_pause)
    thread.start()

    #Define and load all labware.
    [mag_mod] = get_values("mag_mod")
    mag_deck = protocol.load_module(mag_mod, '1')
    sample_plate = mag_deck.load_labware('biorad_96_wellplate_200ul_pcr') #Contains the samples and are mounted on megnetic module.
    mag_deck.disengage()
    
    resevoir = protocol.load_labware('biorad_96_wellplate_200ul_pcr',2) #Contains Magnetic Beads on A1, EB on A3 and EtOH on A5, A6.
    resevoir_trash = protocol.load_labware('usascientific_96_wellplate_2.4ml_deep', 6) #Empty plate for disgarding used EtOH.
    clean_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',3) #Clean plate for the purified samples.

    #Set tip racks and order for pipettes.
    tiprack_7 = [protocol.load_labware('opentrons_96_tiprack_300ul', 7)]
    p300 = protocol.load_instrument('p300_multi', 'right')
    P300 = Pipette(protocol, p300, tiprack_7)

    tiprack_11 = [protocol.load_labware('opentrons_96_tiprack_10ul', 11)]
    p10 = protocol.load_instrument('p10_multi', 'left')
    P10 = Pipette(protocol, p10, tiprack_11)

    
    
    #########################
    ###START PROTOCOL########
    #########################

    #Add magnetic beads to samples, and mix.
    vol_beads = vol_samples * ratio
    P300.pick_up()
    p300.flow_rate.aspirate = 9
    p300.flow_rate.dispense = 9        
    custom_mix(p300, 30, 15, resevoir['A1'], 3, 6)
    p300.flow_rate.aspirate = 120
    p300.flow_rate.dispense = 30
    #p300.transfer(vol_beads, resevoir['A1'], sample_plate['A1'], blow_out=(True), blowout_location='destination well', new_tip='never')
    p300.aspirate(vol_beads+10, resevoir['A1'].bottom(z=3))
    p300.dispense(vol_beads, sample_plate['A1'].bottom(z=5))
    p300.dispense(10, resevoir['A1'].bottom(z=20))
    p300.blow_out(resevoir['A1'].bottom(z=20))
    p300.flow_rate.aspirate=60
    p300.flow_rate.dispense=60
    custom_mix(p300, 15, vol_samples+vol_beads-10, sample_plate['A1'], 0.6, 3)
    p300.drop_tip()
    
    #Wait 5 min. Engage magnet. Wait 5 min.
    protocol.delay(minutes=5) #minutes=5
    mag_deck.engage() 
    protocol.delay(minutes=5) #minutes=5

    #Remove liquid from sample.
    v_tot = vol_beads + vol_samples
    P300.pick_up()
    p300.flow_rate.aspirate = 90
    p300.aspirate(v_tot/2 - 5, sample_plate['A1'].bottom(z=5))
    p300.aspirate(v_tot/2 - 5, sample_plate['A1'].bottom(z=2))
    
    p300.aspirate(5, sample_plate['A1'].bottom(z=0.5))
    p300.aspirate(5, sample_plate['A1'].bottom(z=0.2))
    p300.aspirate(5, sample_plate['A1'].bottom(z=0.1))
    p300.aspirate(5, sample_plate['A1'].bottom(z=0))
    #p300.aspirate(vol_samples+vol_beads, sample_plate['A1'])
    p300.drop_tip()
    
    
    #Cleans the samples with EtOH.
    P300.pick_up()
    for i in range(1, cleanings + 1):
        p300.flow_rate.aspirate = 60
        p300.flow_rate.dispense = 30
        p300.aspirate(190, resevoir['A' + str(4 + i)].bottom(z=3), 3) 
        stepwise_dispense(p300, 190, sample_plate['A1'], 10)
        protocol.delay(seconds=30) #seconds=30
        
        #p300.transfer(200, sample_plate['A1'], resevoir_trash['A1'], blow_out=(True), blowout_location='destination well', new_tip='never')
        
        #remove EtOH
        p300.flow_rate.aspirate=90
        p300.flow_rate.dispense=100
        #p300.pick_up_tip(tiprack_7.wells('A' + str(i))[0])
        center_location = sample_plate['A1'].bottom(z=0.3)
        center_location_higher = center_location.move(Point(0, 0, 1.2))
        adjusted_location1 = center_location.move(Point(0.3, 0.3, 0.1))
        adjusted_location2 = center_location.move(Point(-0.3, -0.3, 0.1))

        p300.aspirate(150, center_location_higher)
        p300.aspirate(30, center_location)
        p300.aspirate(20, adjusted_location1)
        p300.aspirate(20, adjusted_location2)

        p300.dispense(220, resevoir_trash['A1'].bottom(z=3)) 
        p300.blow_out(resevoir_trash['A1'].bottom(z=10)) 
         
    p300.drop_tip()
    
    
    #Wait 5 min. Disengage magnet.
    protocol.delay(minutes=5) #minutes=5
    mag_deck.disengage()


    #Add EB and mix.
    P300.pick_up()
    p300.flow_rate.aspirate = 120
    p300.flow_rate.dispense = 120    
    #p300.transfer(vol_EB, resevoir['A3'], sample_plate['A1'], new_tip ='never')
    p300.transfer(
        vol_EB,
        resevoir['A3'].bottom(z=3), 
        sample_plate['A1'], 
        new_tip ='never',
        blow_out=(True),
        blowout_location='destination well')
    custom_mix(p300, 30, vol_EB-3, sample_plate['A1'], 0.4, 1.5)
    p300.drop_tip()
      
    
    #Disengage magnet to release DNA. Wait 1 min.
    mag_deck.engage()
    protocol.delay(minutes=1) #minutes=1
 

    #Transfer the purified sample to a clean plate.
    p10.flow_rate.aspirate = 3
    p10.flow_rate.dispense = 10
    P10.pick_up()
    p10.transfer(vol_EB-3, sample_plate['A1'].bottom(z=1), clean_plate['A1'].bottom(z=1), new_tip ='never')
    p10.blow_out()
    p10.drop_tip()
    
    p10.home()
    mag_deck.disengage()

    done = True
    thread.join()

    print('Protocol Complete')

    ###########
    ### END ###
    ###########

#User input variables.
# Default values:
no_samples=4
vol_samples=20
ratio=1
cleanings=1
vol_EB=20
# New values from user:
