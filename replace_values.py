# -*- coding: utf-8 -*-

####################################
#   Function used to create the protocol for DNA purification using SPRI-beads.
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
#           v1.1 2021-12-XX: --
#
####################################

import os
from shutil import copyfile


def replace_values(sample_no, sample_vol, ratio, clean_amt, eb_vol):
    """
    Takes 5 parameters which are samples, volume, ratio, number of washes and volumeEB. It reads from a file which acts
    as a blueprint to write in another file. Appends the parameters at the bottom of the blueprint and creates the final 
    protocol file.

        Parameters:
            sample_no (int):            Total number of samples
            samepl_vol (int):           Sample volume
            ratio (float):              Samlpe/SPRI-bead ratio
            clean_amt (int):            Number of cleanings with ethanol
            eb_vol (int):               Volume of elution buffer to be used
        
            Returns:
                Nothing.
    """

    local_user = os.getlogin()
    if sample_no <= 8:
        file_in = f'DNA_cleaning\\dna_cleaning_blueprint_few_samples.py'
    else:
        file_in = f'DNA_cleaning\\dna_cleaning_blueprint.py'
    file_out = f'DNA_cleaning\\dna_cleaning_output.py'
    
    copyfile(file_in, file_out)
    
    with open(file_out, 'a') as file:
        file.write(f'\nno_samples = {sample_no}')
        file.write(f'\nvol_samples = {sample_vol}')
        file.write(f'\nratio = {ratio}')
        file.write(f'\ncleanings = {clean_amt}')
        file.write(f'\nvol_EB = {eb_vol}')
        