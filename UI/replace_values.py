# -*- coding: utf-8 -*-
import os
from shutil import copyfile


def replace_values(sample_no, sample_vol, ratio, clean_amt, eb_vol):
    """
    Takes 5 parameters which are samples, volume, ratio, washes and volumeEB. It reads from a file which acts
    as a blueprint to write in an other file. Uses the input parameters and replaces the blueprint lines with
    those instead, and creates the final protocol file.
    """

    local_user = os.getlogin()
    if sample_no < 8:
        file_in = f'..\\DNA_cleaning\\purify_less_than_8_modified.py'
    else:
        file_in = f'..\\DNA_cleaning\\dna_cleaning_blueprint.py'
    file_out = f'..\\DNA_cleaning\\dna_cleaning_output.py'
    
    copyfile(file_in, file_out)
    
    with open(file_out, 'a') as file:
        file.write(f'\nno_samples = {sample_no}')
        file.write(f'\nvol_samples = {sample_vol}')
        file.write(f'\nratio = {ratio}')
        file.write(f'\ncleanings = {clean_amt}')
        file.write(f'\nvol_EB = {eb_vol}')
        