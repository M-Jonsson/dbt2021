# -*- coding: utf-8 -*-
import os
from shutil import copyfile


def replace_values(sample_no, sample_vol, ratio, clean_amt, eb_vol):
    """
    Takes 5 parameters which are samples, volume, ratio, washes and volumeEB. It reads from a file which acts
    as a blueprint to write in an other file. Uses the input parameters and replaces the blueprint lines with
    those instead, and creates the final protocol file.
    """
    # local_user = os.getlogin()
    # file_read = open(f'c:\\users\\{local_user}\\Onedrive\\Dokument\\python\\dbt2021\\DNA_cleaning\\Final\\dna_cleaning_blueprint.py', 'r')
    # file_write = open(f'c:\\users\\{local_user}\\Onedrive\\Dokument\\python\\dbt2021\\DNA_cleaning\\Final\\dna_cleaning_output.py', 'w')
    # for line in file_read.readlines():
    #     try:
    #         rad = line.split()
    #         if rad[0] == 'Sample':
    #             file_write.write('Sample = {}\n'.format(sample_no))
                
    #         elif rad[0] == 'volSample':
    #             file_write.write('volSample = {}\n'.format(sample_vol))
                
    #         elif rad[0] == 'ratio':
    #             file_write.write('ratio = {}\n'.format(ratio))  
                
    #         elif rad[0] == 'cleanings':
    #             file_write.write('cleanings = {}\n'.format(clean_amt))
                
    #         elif rad[0] == 'volEB':
    #             file_write.write('volEB = {}\n'.format(eb_vol))
                
    #         else:
    #             file_write.write(line)
    #     except:
    #         pass

    local_user = os.getlogin()
    if sample_no < 8:
        file_in = f'c:\\users\\{local_user}\\Onedrive\\Dokument\\python\\dbt2021\\DNA_cleaning\\Final\\purify_less_than_8_modified.py'
    else:
        file_in = f'c:\\users\\{local_user}\\Onedrive\\Dokument\\python\\dbt2021\\DNA_cleaning\\Final\\dna_cleaning_blueprint.py'
    file_out = f'c:\\users\\{local_user}\\Onedrive\\Dokument\\python\\dbt2021\\DNA_cleaning\\Final\\dna_cleaning_output.py'
    
    copyfile(file_in, file_out)
    
    with open(file_out, 'a') as file:
        file.write(f'\nno_samples = {sample_no}')
        file.write(f'\nvol_samples = {sample_vol}')
        file.write(f'\nratio = {ratio}')
        file.write(f'\ncleanings = {clean_amt}')
        file.write(f'\nvol_EB = {eb_vol}')
        