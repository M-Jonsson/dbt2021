from opentrons import protocol_api
import time
from opentrons.commands.commands import drop_tip, pick_up_tip
from opentrons.protocol_api import protocol_context

from opentrons.protocol_api.labware import Well

metadata = {'apiLevel': '2.10'}

letters = ['A','B']


def run(protocol: protocol_api.ProtocolContext):

    tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 4)

    well_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 1)

    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_10ul', 2)
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_10ul', 5)
    tiprack_3 = protocol.load_labware('opentrons_96_tiprack_10ul', 3)
    p10 = protocol.load_instrument('p10_single', 'left', tip_racks=[tiprack_1, tiprack_2, tiprack_3])


    for mm in mastermix_destination.keys():
        p10.pick_up_tip()
        for well in mastermix_destination[mm]:
            p10.aspirate(6, tube_rack[mastermix_source[mm][1]])
            p10.dispense(6, well_plate[well])
        p10.drop_tip()


    for sample in sample_destination.keys():
        for well in sample_destination[sample]:
            p10.transfer(4, tube_rack[sample_source[sample][1]], well_plate[well])


    for standard in standard_destination.keys():
        for well in standard_destination[standard]:
            p10.transfer(4, tube_rack[standard_source[standard][1]], well_plate[well])