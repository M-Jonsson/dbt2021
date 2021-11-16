#Code written by DBT-group 5 
#2021-10-12

from opentrons import protocol_api
import math

metadata = {'apiLevel': '2.10'}

def get_values(*names):
    import json
    _all_values = json.loads("""{"mag_mod":"magnetic module"}""")
    return [_all_values[n] for n in names]

#Mixes the sample with given volume, repetitions, aspirate height, and dispense height
def customMix(well, volym= float, repetitions= int, pipette= None, bottom_aspirate= float, bottom_dispense= float):
    pipette.well_bottom_clearance.aspirate = bottom_aspirate
    pipette.well_bottom_clearance.dispense = bottom_dispense
    for i in range(repetitions):
        pipette.aspirate(volym, well, 0.15)
        pipette.dispense(volym, well, 0.15)
    pipette.well_bottom_clearance.aspirate = 1
    pipette.well_bottom_clearance.dispense = 1 
 
#Dispenses the liquid with increasing distance from the bottom     
def stepwise_dispense(pipette, volume, location_dispense, steps):
    step_volume = volume/steps
    for i in range(steps):
        volume_added = (i+1)*step_volume #total volume added efter the step is done
        #polyn. describing relationship between height and volume
        #applies only to 200ul 96-well PCR plate from bio rad
        dispense_height = (-2.5+((2.5**2)+4.9+1.42*volume_added)**(1/2)) + 1 #additional 1 mm above est. level
        pipette.dispense(step_volume, location_dispense.bottom(z=dispense_height))

def run(protocol: protocol_api.ProtocolContext):
    
    #Define and load all labware
    
    # [mag_mod] = get_values("mag_mod")
    mag_deck = protocol.load_module('magnetic module', '1')
    mag_plate = mag_deck.load_labware('biorad_96_wellplate_200ul_pcr')
    mag_deck.disengage()
    
    resevoirEtOH = protocol.load_labware('usascientific_96_wellplate_2.4ml_deep', 5) #kolla vilken som faktiskt anvands
    resevoir = protocol.load_labware('usascientific_96_wellplate_2.4ml_deep',2) #magnetic beeds + eb, kolla vilken som anvands
    clean_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',3) #ren 96well plate for renat DNA
    
    #tip racks and pipettes
    tiprack_7 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    tiprack_8 = protocol.load_labware('opentrons_96_tiprack_300ul', 8) 
    tiprack_9 = protocol.load_labware('opentrons_96_tiprack_300ul', 9)
    tiprack_10 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)
    p300 = protocol.load_instrument('p300_multi', 'right', tip_racks=[tiprack_8, tiprack_9, tiprack_10, tiprack_7])

    tiprack_11 = protocol.load_labware('opentrons_96_tiprack_10ul', 11)
    p10 = protocol.load_instrument('p10_multi', 'left', tip_racks=[tiprack_10, tiprack_11])
  
   
    #Add magnetic beads
    columns = math.ceil(no_samples/8) #calculates how many columnes are filled
    amount_beads = vol_samples * ratio #calculates the amount of magnetic beads
    
    for i in range(1,columns+1):
        p300.pick_up_tip()
        p300.transfer(amount_beads, resevoir['A1'], mag_plate['A'+str(i)], blow_out=(True), blowout_location='destination well', new_tip='never') 
        customMix(mag_plate['A'+str(i)], vol_samples+amount_beads-5, 5, p300, 0.6, 3.5)
        p300.drop_tip()
    
    #Delay 5 min, Engage magnet, Delay 5 min
    protocol.delay(minutes=15)
    mag_deck.engage() 
    protocol.delay(minutes=15)

    #Remove liquid
    for i in range(1,columns+1):
        p300.pick_up_tip()
        p300.flow_rate.aspirate=30
        p300.aspirate(vol_samples+amount_beads, mag_plate['A'+str(i)])
        p300.drop_tip()
    
    
    #Clean with EtOH
    for j in range(1,cleanings+1):
        for i in range(1,columns+1):
            p300.pick_up_tip(tiprack_7.wells('A'+str(i))[0]) 
            p300.aspirate(200, resevoirEtOH['A'+str(i)],3)
            p300.flow_rate.dispense=30
            stepwise_dispense(p300, 200, mag_plate['A'+str(i)], 10) 
            p300.return_tip() #returns tip to the box
        
        if columns < 4:
            protocol.delay(seconds=30) 
       
        for k in range(1,columns+1):
            p300.pick_up_tip(tiprack_7.wells('A'+str(k))[0])
            p300.transfer(200,mag_plate['A'+str(k)],resevoir['A12'],blow_out=(True), blowout_location='destination well', new_tip='never') #vad ska den gora med etanolen? just nu, i en well
            if j < cleanings:
                p300.return_tip()
            elif j == cleanings:
                p300.drop_tip()
                   
    
    #Delay 5 min, Disengage magnet
    protocol.delay(minutes=5) 
    mag_deck.disengage()


    #Add EB and mix
    for i in range(1,columns+1):      
        p300.pick_up_tip()
        p300.transfer(vol_EB, resevoir['A3'], mag_plate['A'+str(i)], new_tip ='never')
        customMix(mag_plate['A'+str(i)], vol_EB-3, 5, p300, 0.6, 1.5)
        p300.drop_tip()
      
    
    #Set DNA free
    mag_deck.engage()
    protocol.delay(minutes=1)
 

    #Transfer the purified sample to a clean plate
    p10.flow_rate.aspirate = 3
    for i in range(1,columns+1):
        p10.pick_up_tip()
        p10.transfer(vol_EB-3, mag_plate['A'+str(i)], clean_plate['A'+str(i)], new_tip ='never')
        p10.blow_out()
        p10.drop_tip()
    
    mag_deck.disengage()

#User input
# Default values
no_samples = 20
vol_samples = 20
ratio = 0.8
cleanings = 1
vol_EB = 15