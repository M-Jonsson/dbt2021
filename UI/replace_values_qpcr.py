import csv
from shutil import copyfile
from os import getlogin


def csv_till_lista(filepath):
    '''Takes a .csv file as input and finds which wells to distribute each
    mastermix, standard and sample. Also determines how to place each source on a tube rack. 

    The information is stored in a separate dictionary for mastermixes, standards and samples,
    as well as separate dictionaries for destination wells and source wells. Everything is then
    stored again as a dictionary of dictionaries to save which dictionary corresponds to what. 
    
    Returns a list with all dictionaries at position 0 and only the source dictionaries at position 1. 
    '''

    with open(filepath, 'r') as csv_file:
        '''Ev. lägg till errorhantering
        för att se om .csv ser rätt ut genom att 
        kolla på header-raden.
        '''
        csv_reader = csv.reader(csv_file, delimiter = ',')
        first_line = next(csv_reader) # Skip header in file.

        # Check if the .csv file starts at column 0 or 1.
        # The example file started at 1 but changed to 0 when modified and re-saved.  
        if first_line[0]:
            csv_list = [line for line in csv_reader]
        elif not first_line[0]:
            csv_list = [line[1:] for line in csv_reader]
            first_line = first_line[1:]

    # Finds all unique mastermixes, stadards and samples.
    # Each standard concentration is considered unique and NTC is considered a standard.
    # Each combination of antibody, biological set name and dilution factor is considered as a unique sample.
    unique_mastermixes = []
    unique_standards = []
    unique_samples = []
    for line in csv_list:
        # Unique mastermixes
        if line[4] not in unique_mastermixes:
            unique_mastermixes.append(line[4])
        # Line corresponds to a standard or NTC
        if 'Std' in line[2] or 'NTC' in line[2]:
            standard = '|'.join([line[2], line[8]])
            if standard not in unique_standards:
                unique_standards.append(standard)
        # or line corresponds to a sample
        elif 'Unkn' in line[2]:
            sample = '|'.join([line[2],line[5],line[6],line[7]])
            if sample not in unique_samples:
                unique_samples.append(sample)


    # Find well coordinates (line[0:2]) for each mastermix 
    # and saves it as a list to a dictionary with the corresponding mastermix as the key.
    mastermix_destination = {}
    for mm in unique_mastermixes:
        wells = [''.join(line[0:2]) for line in csv_list if line[4] == mm]
        mastermix_destination[f'{mm}'] = wells
    # Even more compact alternative but not as clear
    # mastermix_dest_test = {f'{mm}':[''.join(line[0:2]) for line in csv_list if line[4] == mm] for mm in unique_mastermixes}

    # Find well coordinates for each standard (including NTC) .
    standard_destination = {}
    for standard in unique_standards:    
        wells = [''.join(line[0:2]) for line in csv_list if '|'.join([line[2], line[8]]) == standard]
        standard_destination[f'{standard}'] = wells

    # Find well coordinates for each sample.
    sample_destination = {}
    for sample in unique_samples:
        wells = [''.join(line[0:2]) for line in csv_list if '|'.join([line[2],line[5],line[6],line[7]]) == sample]
        sample_destination[f'{sample}'] = wells


    # Distribute source wells for each mastermix, standard and sample
    # from list of wells on tube rack.
    wells_list_tr = ['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2', 'A3', 'B3', 'C3', 'D3', 
                       'A4', 'B4', 'C4', 'D4', 'A5', 'B5', 'C5', 'D5', 'A6', 'B6', 'C6', 'D6']
    tube_racks = ['tr1', 'tr2', 'tr3', 'tr4', 'tr5', 'tr6', 'tr7', 'tr8']
    tube_rack_wells = [[tube_rack, well] for tube_rack in tube_racks for well in wells_list_tr]

    mastermix_source = {}
    i = 0 # Kept outside of loops to keep track which wells have been assigned. 
    for mm in mastermix_destination.keys():
        mastermix_source[mm] = tube_rack_wells[i]
        i = i + 1

    sample_source = {}
    for sample in sample_destination.keys():
        sample_source[sample] = tube_rack_wells[i]
        i = i + 1

    standard_source = {}
    for standard in standard_destination.keys():
        standard_source[standard] = tube_rack_wells[i]
        i = i + 1


    return [
        {
            'mastermix_destination': mastermix_destination,
            'sample_destination': sample_destination,
            'standard_destination': standard_destination,
            # 'mastermix_source': mastermix_source,
            # 'sample_source': sample_source,
            # 'standard_source': standard_source
        },
        {
            'mastermix_source': mastermix_source,
            'sample_source': sample_source,
            'standard_source': standard_source
        }]


def replace_values_qpcr(destinations, sources):
    '''Creates a copy of the qPCR protocol blueprint and adds
    source and destination wells for each
    mastermix, standard and sample to the new copy.
    '''
    local_user = getlogin() # Used when specifiying filepaths
    all_wells = {**destinations, **sources} # Merge into 1 dicitonary for easy looping
    # Create a copy
    file_in = f'..\\qPCR\\qpcr_blueprint.py'
    file_out = f'..\\qPCR\\qpcr_output.py'
    copyfile(file_in, file_out)

    # Appends well information in the format of 
    # <Group> = <Dictionary of wells for all group members>
    # to the end of the file.
    # A group is e.g. mastermix destination wells or 
    # mastermix source wells and a group memeber a specific mastermix.
    with open(file_out, 'a') as file:
        for well_group in all_wells:
            wells_str = str(all_wells[well_group])
            file.write(f'\n{well_group} = {wells_str}')


# csv_till_lista(r"C:\Users\Mathias\OneDrive\Dokument\Python\DBT2021\qPCR\ChIP_max.csv")