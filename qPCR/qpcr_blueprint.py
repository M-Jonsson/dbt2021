from opentrons import protocol_api
import time
from opentrons.commands.commands import drop_tip, pick_up_tip
from opentrons.protocol_api import protocol_context
import json
from opentrons.protocol_api.labware import Well

metadata = {'apiLevel': '2.10'}

letters = ['A','B']


def run(protocol: protocol_api.ProtocolContext):

    with open('/data/user_storage/own_24_tuberack_1500ul.json') as labware_file:
        labware_def = json.load(labware_file)

    tube_rack1 = protocol.load_labware_from_definition(labware_def, 8)
    tube_rack2 = protocol.load_labware_from_definition(labware_def, 9)
    tube_rack3 = protocol.load_labware_from_definition(labware_def, 4)
    tube_rack4 = protocol.load_labware_from_definition(labware_def, 5)
    tube_rack5 = protocol.load_labware_from_definition(labware_def, 6)
    tube_rack6 = protocol.load_labware_from_definition(labware_def, 1)
    tube_rack7 = protocol.load_labware_from_definition(labware_def, 2)
    tube_rack8 = protocol.load_labware_from_definition(labware_def, 3)

    tube_racks = {
        'tr1': tube_rack1, 
        'tr2': tube_rack2, 
        'tr3': tube_rack3, 
        'tr4': tube_rack4, 
        'tr5': tube_rack5, 
        'tr6': tube_rack6,
        'tr7': tube_rack7,
        'tr8': tube_rack8}

    well_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 11)

    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_10ul', 10)
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_10ul', 7)
    p10 = protocol.load_instrument('p10_single', 'left', tip_racks=[tiprack_1, tiprack_2])

    for mm in mastermix_destination.keys():
        p10.pick_up_tip()
        for well in mastermix_destination[mm]:
            tube_rack = tube_racks[mastermix_source[mm][0]]
            p10.aspirate(6, tube_rack[mastermix_source[mm][1]])
            p10.dispense(6, well_plate[well])
        p10.drop_tip()


    for sample in sample_destination.keys():
        for well in sample_destination[sample]:
            tube_rack = tube_racks[sample_source[sample][0]]
            p10.transfer(4, tube_rack[sample_source[sample][1]], well_plate[well])


    for standard in standard_destination.keys():
        for well in standard_destination[standard]:
            tube_rack = tube_racks[standard_source[standard][0]]
            p10.transfer(4, tube_rack[standard_source[standard][1]], well_plate[well])

    print('Protocol Complete')
    