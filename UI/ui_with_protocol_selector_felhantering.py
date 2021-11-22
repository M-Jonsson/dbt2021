import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.constants import NORMAL
import replace_values
import replace_values_qpcr
import subprocess
from os import getlogin
import os.path
import sys
import time
import multiprocessing
import socket

# Files and logins for SSH and SCP
local_user = getlogin() # os.getlogin() get username on local machine
key_filename = f'c:\\users\\{local_user}\\opentrons\\ot2_ssh_key'
protocol_local_filepath = f'dna_cleaning\\'
protocol_robot_filepath = '/data/user_storage/'
protocol_name = 'dna_cleaning_output.py'
ip = '169.254.29.201'
username = 'root'
protocol_qpcr_local_filepath = f'qPCR\\'
protocol_qpcr_name = 'qpcr_output.py'

font = (16)

# Error check to see that the ssh_key is exists.
if os.path.isfile(key_filename):
    print("ssh-key read successfully.")
# else:
#     messagebox.showerror('File not found error!', f'SSH Key could not be read. Please check the filepath: {key_filename} and confirm it is placed there')
    # sys.exit(0)

class Selector():
    ''' Contains a frame with widgets used to select which protocol to edit.
    The frame will be added to the root window when initialized and destroyed (closed)
    when another class containing a new frame is called. 
    '''

    def __init__(self):
        # Main frame for the protocol selection, to which all associated widgets are added
        self.frame = tk.Frame()
        self.frame.grid()

        self.label_selection_info = ttk.Label(self.frame, text='Select a protocol')
        self.label_selection_info.grid(row=0, column=0, padx=10, pady=10)

        self.button_beads = ttk.Button(self.frame, text='Magnetic beads\nDNA purification', command=self.select_protocol_beads)
        self.button_beads.grid(row=1, column=0, padx=10, pady=10)

        self.button_qpcr = ttk.Button(self.frame, text='qPCR protocol', command=self.select_protocol_qpcr)
        self.button_qpcr.grid(row=1, column=1, padx=10, pady=10)

        self.button_test = ttk.Button(self.frame, text='test', command=self.test)
        self.button_test.grid(row=1, column=2)

    def select_protocol_beads(self):
        '''Closes the frame for protocol selection, but not the root window.
        Then creates a new frame from Bead_protocol_config() for editing a magnetic bead DNA purification protocol.
        '''

        self.frame.destroy()
        Bead_protocol_config()

    def select_protocol_qpcr(self):
        '''Closes the frame for protocol selection, but not the root window.
        Then creates a new frame from qPCR_protocol_config() for editing a qPCR protocol.
        '''

        self.frame.destroy()
        qPCR_protocol_config()

    def test(self):
        # Check_window()
        # subprocess.run(f'scp -i {key_filename} dna_cleaning\\purify_less_than_8_custom.py {username}@{ip}:{protocol_robot_filepath}purify_less_than_8_custom.py')

        # subprocess.run(f'ssh -i {key_filename} {username}@{ip} -t "sh -lic" \'opentrons_execute {protocol_robot_filepath}purify_less_than_8_custom.py\'')

        Check_window()

class Bead_protocol_config():
    '''Contains a frame with widgets used configure a magnetic bead DNA purification protocol.
    The frame will be added to the root window when initialized and destroyed (closed)
    when another class containing a new frame is called.
    Allows for uploading and launching the finished protocol. 
    '''

    def __init__(self):
        # Main frame for the protocol editing, to which all associated widgets are added
        self.frame = tk.Frame()
        self.frame.grid()

        # Labels
        self.label_sample_no = ttk.Label(self.frame, text='How many samples: \n(Valid values between 1-96 samples) ')
        self.label_sample_vol = ttk.Label(self.frame, text='Volume sample: \n(Valid values between 15-40 μl) ')
        self.label_bead_ratio = ttk.Label(self.frame, text='Bead:Sample ratio: \n(Valid ratios between 0.5-1.5 )')
        self.label_ethanol = ttk.Label(self.frame, text='Number of ethanol washes: ')
        self.label_eb = ttk.Label(self.frame, text='Volume EB: \n(Valid values between 15-25 μl)')

        self.label_sample_no.grid(row=0, column=0, padx= 10, pady= 10, sticky=tk.W)
        self.label_sample_vol.grid(row=2, column=0, padx= 10, pady= 10, stick=tk.W)
        self.label_bead_ratio.grid(row=4, column=0, padx= 10, pady= 10, sticky=tk.W)
        self.label_ethanol.grid(row=6, column=0, padx= 10, pady= 10, sticky=tk.W)
        self.label_eb.grid(row=8, column=0, padx= 10, pady= 10, sticky=tk.W)

        # Text entries
        self.entry_sample_no = ttk.Entry(self.frame, width=35)
        self.entry_sample_vol = ttk.Entry(self.frame, width=35)
        self.entry_bead_ratio = ttk.Entry(self.frame, width=35)
        self.entry_eb = ttk.Entry(self.frame, width=35)

        self.entry_sample_no.grid(row= 0, column= 1, padx= 10, pady= 10, columnspan= 2)
        self.entry_sample_vol.grid(row=2, column=1, padx=10, pady=10, columnspan= 2)
        self.entry_bead_ratio.grid(row= 4, column= 1, padx= 10, pady= 10, columnspan= 2)
        self.entry_eb.grid(row= 8, column= 1, padx= 10, pady= 10, columnspan= 2)

        # Radio button for no. of ethanol washes
        self.ethanol_var = tk.IntVar() # Variable associated with the radio buttons, changes depending on button state
        self.radio_ethanol1 = tk.Radiobutton(self.frame, text='1', variable=self.ethanol_var, value=1)
        self.radio_ethanol2 = tk.Radiobutton(self.frame, text='2', variable=self.ethanol_var ,value=2)

        self.radio_ethanol1.grid(row=6, column=1, padx=10, pady=10)
        self.radio_ethanol2.grid(row=6, column=2,  padx=10, pady=10)

        # Buttons
        self.button_ok = ttk.Button(self.frame, text='Ok', command=self.ok_button)
        self.button_ok.grid(row=10, column=0, padx=10, pady=10)

        self.button_back = ttk.Button(self.frame, text='Back', command=self.back_button)
        self.button_back.grid(row=10, column=2, padx=10, pady=10)

        self.button_start = ttk.Button(self.frame, text='Start run', command=self.start_run, state=tk.DISABLED)
        self.button_start.grid(row=15, column=0, padx=10, pady=10)

        self.button_estimate = ttk.Button(self.frame, text='Estimate time', command=self.get_estimate, state=tk.DISABLED)
        self.button_estimate.grid(row=15, column=1, padx=10, pady=10)

        self.prepare_for_run = ttk.Button(self.frame, text='Prepare run', command=self.call_checkbox_beads, state=tk.DISABLED)
        self.prepare_for_run.grid(row=15, column=2, padx=10, pady=10)
    
    def call_checkbox_beads(self):
        '''The purpuse of this function is to call the Checkbox() class, it checks the number of samples and uses
        deck_less_8.gif is the sample number is <8, otherwise it uses dec_96.gif'''

        if int(self.entry_sample_no.get()) < 8:
            Checkbox('dna_cleaning_output.py', 'ui\\deck_less_8.gif')
        else:
            Checkbox('dna_cleaning_output.py', 'ui\\deck_96.gif')
 
    def ok_button(self):
        ''' Checks if all entries are valid.
        If valid, will create a modified protocol with the value given by the user 
        (done by replace_values() to edit an existing protocol blueprint).
        Finally uploads the new protocol to the robot and launches it.
        '''

        try:
        # Gets values from corresponding entry and checks if it is within the allowed range
        # Keeps track of validity with a Bool for each entry. 
            self.sample_no = int(self.entry_sample_no.get())
            if self.sample_no < 1 or self.sample_no > 97:
                messagebox.showerror('Notice', 'Sample amount is too small or too high, choose 1-96 samples')
                self.correct_sample_no = False
            else:
                self.correct_sample_no = True
            
            self.sample_vol = float(self.entry_sample_vol.get())
            if self.sample_vol <= 14.5 or self.sample_vol > 40:
                messagebox.showerror('Notice', 'Volume amount is too low or too high, choose a volume between 15-40µl')
                self.correct_sample_vol = False
            else:
                self.correct_sample_vol = True

            self.ratio = float(self.entry_bead_ratio.get())
            if self.ratio < 0.5 or self.ratio > 1.5:
                messagebox.showerror('Notice', 'Ratio is too low or too high, choose a ratio between 0.5 and 1.5')
                self.correct_ratio = False
            else:
                self.correct_ratio = True

            self.ethanol = self.ethanol_var.get()
            if self.ethanol == 1 or self.ethanol == 2:
                self.correct_wash = True
            else:
                messagebox.showerror('Notice', 'Choose amount of washes')
                self.correct_wash = False 

            self.eb = float(self.entry_eb.get())
            if self.eb < 15 or self.eb > 25:
                messagebox.showerror('Notice', 'EB volume is too low or too high, choose an EB volume between 15-25µl')
                self.correct_eb = False
            else:
                self.correct_eb = True
            
            if self.correct_sample_no and self.correct_sample_vol and self.correct_ratio and self.correct_wash and self.correct_eb:
                # replace_values() edits an existing blueprint with the user inputs
                try:
                    replace_values.replace_values(self.sample_no, self.sample_vol, self.ratio, self.ethanol, self.eb) 
                except IOError:
                    tk.messagebox.showerror('Protocol write error!', 'Could not write protocol file. Please check that the template file exists and is accessible.'\
                                            ' Contact your administrator if you are uncertain.')
                else:
                    # Calculate total amount of magnetic beads required. 
                    self.total_beads = (self.sample_no * self.sample_vol * self.ratio) / 8
                    print(self.total_beads)
                    messagebox.showinfo('Success!', 'Successfully entered parameters into the protocol')

                    # Allow starting or simulating the now created protocol
                    self.button_estimate.config(state=tk.NORMAL)
                    self.button_start.config(state=tk.NORMAL)
                    self.prepare_for_run.config(state=tk.NORMAL)

                    # Disable editing values since a protocol has been created
                    self.entry_bead_ratio.config(state=tk.DISABLED)
                    self.entry_eb.config(state=tk.DISABLED)
                    self.entry_sample_no.config(state=tk.DISABLED)
                    self.entry_sample_vol.config(state=tk.DISABLED)
                    self.radio_ethanol1.config(state=tk.DISABLED)
                    self.radio_ethanol2.config(state=tk.DISABLED)
                    self.button_ok.config(state=tk.DISABLED)

        except ValueError:
            messagebox.showerror('Notice', 'You did not enter valid numbers')
    
    def start_run(self):
        '''Uploads the new protocol using 
        scp -i <key> <file_to_upload> <where_to_place_it>

        Then launches the new protocol using
        ssh -i <key> <login> -t "sh -lic" <command>
        -t creates a pseudo terminal on the remote machine (?)
        sh -lic makes the following command (c) run in an interactive (i) and login (l) shell,
        which is required to initialize everything correctly.
        Else the robot cannot use any labware or find calibration data. 
        '''
        # Upload the new protocol using 
        # scp -i <key> <file_to_upload> <where_to_place_it>
        # Defines the multiprocess to be able to handle errors when transferring the protocol to the robot via SCP.
        time_process = multiprocessing.Process(target=scp_transfer, name="SCP transfer")
        time_process.start()
        time_process.join(5)
        # If the upload takes longer than 5 seconds the program throws an error as it should not take that long. 
        if time_process.is_alive():
            time_process.terminate()
            messagebox.showerror('Transfer Error!','An error occured during the transfer of the protocol file to the robot.')
            try:
                time_process.close()
            except ValueError:
                print("Time process still running")
        else:
            # If the upload of the protocol file is successful, powershell tries to run to connect to the robot.
            try:
                # Launch the new protocol using
                # ssh -i <key> <login> <command>
                # -t creates a pseudo terminal on the remote machine (?)
                # sh -lic makes the following command (c) (opentrons_execute <file>) run in an interactive (i) and login (l) shell.
                # This is required to initialize everything correctly, else cannot use magnetic module or find calibration data. 
                subprocess.run(f'ssh -i {key_filename} {username}@{ip} -t "sh -lic" \'opentrons_execute {protocol_robot_filepath}{protocol_name}\'')
            except:
                messagebox.showerror('Error', 'There was an error running the powershell SSH connect command.')     

    def get_estimate(self):
        '''Simulates the protocol using opentrons_simulate.exe
        with the experimental time estimate feature enabled (-e flag).
        Shows the result in an message box. 
        '''
        run = subprocess.run(f"opentrons_simulate.exe -e {protocol_local_filepath}{protocol_name}", capture_output=True, text=True)
        self.beads_estimate = run.stdout.split('\n')[-4]
        messagebox.showinfo('Protocol estimate', f'{self.beads_estimate}')
    
    def back_button(self):
        '''Closes the frame for protocol editing and replaces it with a frame for protocol selection.'''
        self.frame.destroy()
        Selector()

class qPCR_protocol_config():
    def __init__(self):
        self.frame = tk.Frame()
        self.frame.grid()

        self.file_label = ttk.Label(self.frame, text='File:')
        self.file_label.grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=tk.W)

        self.file_name_label = ttk.Label(self.frame, text='No file chosen', foreground='red')
        self.file_name_label.grid(row=1, column=0, columnspan=3, padx=10, pady=0, sticky=tk.W)

        self.open_file_dialog_button = ttk.Button(self.frame, text='Choose a file', command=self.open_file_dialog)
        self.open_file_dialog_button.grid(row=5, column=0, padx=10, pady=10)

        self.button_back = ttk.Button(self.frame, text='Back', command=self.back)
        self.button_back.grid(row=5, column=2, padx=10, pady=10)

        self.start_button = ttk.Button(self.frame, text='Start protocol', command=self.start_protocol, state=tk.DISABLED)
        self.start_button.grid(row=5, column=1, padx=10, pady=10)
        
        self.grid_button = ttk.Button(self.frame, text='Tube Rack Layout', command=self.layout_grid, state=tk.DISABLED)
        self.grid_button.grid(row=10, column=0, padx=10, pady=10)        
        
        self.estimate_button = ttk.Button(self.frame, text='Estimate time', command=self.get_estimate, state=tk.DISABLED)
        self.estimate_button.grid(row=10, column=1, padx=10, pady=10)

        self.prepare_for_run = ttk.Button(self.frame, text='Prepare run', command=self.call_checkbox_qpcr)
        self.prepare_for_run.grid(row=10, column=2, padx=10, pady=10)

        self._sources = None # klassvariabel som sparar dictionary med sources
    
    def call_checkbox_qpcr(self):
        '''The purpuse of this function is to call the Checkbox() class, currently we do
        not have a picture for the qpcr deck layout, the picture is a placeholder.'''

        Checkbox('qpcr_output.py','ui\\deck_96.gif')

    def open_file_dialog(self):
        filepath = filedialog.askopenfilename(filetypes=(('CSV files','*.csv'),))
        if filepath:
            [self.destinations, self.sources] = replace_values_qpcr.csv_till_lista(filepath)
            self._sources = self.sources
            replace_values_qpcr.replace_values_qpcr(self.destinations, self.sources)

            # Enable locked buttons
            self.start_button.config(state=tk.NORMAL)
            self.grid_button.config(state=tk.NORMAL)
            self.estimate_button.config(state=tk.NORMAL)
            # Show name of chosen file
            self.file_name_label.config(text=filepath.split('/')[-1], foreground='green')
    
    def layout_grid(self):
        # Creates a new window with a notebook widget
        tube_rack_window = Tube_rack_window()

        # Variable to keep track of the loops
        tube_racks = []

        # Loop through each type of group (mastermix, sample, standard)
            # and each mixture in a group (each mastermix etc.)
        t1 = time.time_ns()
        for group_name, group_content in self._sources.items():
            for mixture, [tube_rack, well] in group_content.items():
                # Checks if a new tab=new tube rack is needed.
                if tube_rack not in tube_racks:
                    # Create a new tab in the notebook and add a grid to it.
                    trw_tab = tube_rack_window.new_tab(tube_rack)
                    trg = Tube_rack_grid(trw_tab)
                    tube_racks.append(tube_rack)

                # Find corresponding destination wells to calculate volume needed.
                for dest_key in self.destinations.keys():
                    # Remove _source part of name
                    dest_start = group_name.split('_')[0]
                    if dest_key.startswith(dest_start):
                        # Number of destination well for a specific mixture.
                        dest_amount = len(self.destinations[dest_key][mixture])
                        # Mastermix requires 6ul, samples/standards require 4ul.
                        # Calculates total volume required using n+3 wells.
                        if dest_start == 'mastermix':
                            dest_vol = 6 * (dest_amount + 3)
                        else:
                            dest_vol = 4 * (dest_amount + 3)

                # Capitalizes first letter of name (e.g. Mastermix)
                # Also adds the specific mixture name, which well to put it in and total volum required. 
                text = f"{dest_start.title()}:\n{mixture}\n{well}\n{dest_vol} ul"
                trg.edit(well, text)
        t2 = time.time_ns()
        print((t2-t1)//1000000)

    def start_protocol(self):
                # Upload the new protocol using 
        # scp -i <key> <file_to_upload> <where_to_place_it>
        subprocess.run(f'scp -i {key_filename} {protocol_qpcr_local_filepath}{protocol_qpcr_name} {username}@{ip}:{protocol_robot_filepath}{protocol_qpcr_name}')
        print(f'would have run:\nubprocess.run(scp -i {key_filename} {protocol_qpcr_local_filepath}{protocol_qpcr_name} {username}@{ip}:{protocol_robot_filepath}{protocol_qpcr_name}')

        # Launch the new protocol using
        # ssh -i <key> <login> <command>
        # -t creates a pseudo terminal on the remote machine (?)
        # sh -lic makes the following command (c) (opentrons_execute <file>) run in an interactive (i) and login (l) shell.
        # This is required to initialize everything correctly, else cannot use magnetic module or find calibration data. 
        subprocess.run(f'ssh -i {key_filename} {username}@{ip} -t "sh -lic" \'opentrons_execute {protocol_robot_filepath}{protocol_qpcr_name}\'')
        print(f'would have run:\nsubprocess.run(ssh -i {key_filename} {username}@{ip} -t "sh -lic" \'opentrons_execute {protocol_robot_filepath}{protocol_qpcr_name}\')')

    def get_estimate(self):
        run = subprocess.run(f"opentrons_simulate.exe -e {protocol_qpcr_local_filepath}{protocol_qpcr_name}", capture_output=True, text=True)
        self.qPCR_estimate = run.stdout.split('\n')[-4]
        messagebox.showinfo('Protocol estimate', f'{self.qPCR_estimate}')

    def back(self):
        self.frame.destroy()
        Selector()

class Tube_rack_window():
    def __init__(self):
        # Create a new window
        self.window = tk.Toplevel()
        self.window.title('Tube rack layout')
        # Create notebook (tabs) associated with the window
        self.nb = ttk.Notebook(self.window)
        # Place the notebook to show it
        self.nb.pack()

        

    def new_tab(self, title):
        self.frame = tk.Frame(self.nb)
        self.nb.add(self.frame, text=title)
        return self.frame

class Tube_rack_grid():
    def __init__(self, parent):
        # Creates a frame assigned to the specified parent widget
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.frame.grid()

        # Headers
        self.header_letters = ['A', 'B', 'C', 'D']
        self.header_numbers = [str(i) for i in range(1, 7)]

        # Place headers on grid, letters on left-most column and numbers on upper-most row
        for i, row_letter in enumerate(self.header_letters):
            ttk.Label(self.frame, text=row_letter, foreground='grey').grid(row=i+1, column=0, padx=20, pady=20)
        for i, col_num in enumerate(self.header_numbers):
            ttk.Label(self.frame, text=col_num, foreground='grey').grid(row=0, column=i+1, padx=20, pady=20)
        
        # Fill rest of grid with 'Empty'
        for i in range(len(self.header_letters)):
            for j in range(len(self.header_numbers)):
                ttk.Label(self.frame, text='Empty', foreground='black', justify='center').grid(row=i+1, column=j+1, padx=20, pady=20)

    def edit(self, xy, new_text):
        row_index_to_letter = {0:None, 1:'A', 2:'B', 3:'C', 4:'D'}
        # Loop through each label on the grid
        for child in self.frame.children.values():
            # Find row and column index for each label and convert to well name
            child_x = row_index_to_letter[child.grid_info()['row']]
            child_y = str(child.grid_info()['column'])
            # Edit label text when the correct well is found
            if child_x == xy[0] and child_y == xy[1]:
                child.configure(text=str(new_text))
                break

class Checkbox:
    '''Checkbox class containing checkboxes and other stuff. very bare bones at the moment'''
    def __init__(self, protocol_type, image):
        self.window = tk.Toplevel()
        self.window.title('checkboxes')
        self.frame = ttk.Frame(self.window)
        self.frame.pack()
        self.protocol_type = protocol_type
        
        self.ssh_conection = False

        if self.protocol_type == 'qpcr_output.py':
            pass
        else:
            self.pipette_text = '\n     Left: P10 8-channel\n     Right: P300 8-channel'

        
        # self.var1 = tk.IntVar()
        
        #self.start_button = tk.Button(self.frame, text='Start protocol', command=self.start_protocol, state=tk.DISABLED)
        self.connection_button = ttk.Button(self.frame, text='Check Connection', command= self.check_ssh)
        self.connection_button.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
        
        self.run_protocol_button = ttk.Button(self.frame, text='Run Protocol', command= self.run_protocol, state='disabled')
        self.run_protocol_button.grid(row=20, column= 1, padx=20, pady=20, sticky=tk.W)
        
        self.label1 = ttk.Label(self.frame, text='1. Check the ssh-connection', font=font).grid(row=0, column=1, sticky=tk.W, padx=20, pady=20, columnspan=2)
        self.label2 = ttk.Label(self.frame, text='2. Check the pipettes:' + self.pipette_text, font=font).grid(row=5, column=1, sticky=tk.W, padx=20, pady=20, columnspan=2)
        self.label3 = ttk.Label(self.frame, text='3. Load the robot deck according to the picture', font=font).grid(row=10, column=1, sticky=tk.W, padx=20, pady=20, columnspan=2)

        self.volumes = ttk.Label(self.frame, text='\n     Ethanol: ___ ul per well\n     EB: ___ ul per well', font=font).grid(row=11, column=1, sticky=tk.W, padx=20, pady=20, columnspan=2)

        self.connection_status = ttk.Label(self.frame, text=' ', font=font)
        self.connection_status.grid(row=3, column=2, sticky=tk.W, padx=20, pady=20)


        # self.checkbox1 = ttk.Checkbutton(self.frame,variable=self.var1, onvalue=1, offvalue=0, command=None)
        # self.checkbox1.grid(column=0, row=0, pady=20)
        
        self.image = tk.PhotoImage(file=image)
        self.img_label = ttk.Label(self.frame, image=self.image)
        self.img_label.grid(row=0, column=5, rowspan=30) # Show imgage on frame
        
    def check_ssh(self):
        '''This function should check if you have a ssh-connection, the host variable should be changed to the robot ip (i think)'''

        self.connection_status.config(text='Checking connection...', foreground='green')
        host = 'localhost'
        port = 22
        self.ssh_conection = False
        print(1)
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.connect((host, port))
            print(2)
        except Exception:
        # not up, log reason from ex if wanted
            print(3)
    
        else:
            test_socket.close()
            self.ssh_conection = True
            print(4)
            
        if self.ssh_conection:
            self.run_protocol_button.config(state='normal')
            self.connection_status.config(text='Connection OK', foreground='green')
            print(5)
        else:
            # tk.messagebox.showerror('Notice', 'Could not establish a ssh-connection')
            self.connection_status.config(text='Connection failed', foreground='red')
            print(6)
            
    def run_protocol(self):
        '''This function runs the protocols, which one it runs is determined by the variable protocol_type when the an object is created.'''

        print(f'this should run the protocol {self.protocol_type}')

        if self.protocol_type == 'dna_cleaning_output.py':
            print('Running magentic beads protocol')
            '''Uploads the new protocol using 
            scp -i <key> <file_to_upload> <where_to_place_it>
            Then launches the new protocol using
            ssh -i <key> <login> -t "sh -lic" <command> -t creates a pseudo terminal on the remote machine (?)
            sh -lic makes the following command (c) run in an interactive (i) and login (l) shell,
            which is required to initialize everything correctly.
            Else the robot cannot use any labware or find calibration data. 
            '''
            '''
            # Upload the new protocol using 
            # scp -i <key> <file_to_upload> <where_to_place_it>
            # Defines the multiprocess to be able to handle errors when transferring the protocol to the robot via SCP.
            time_process = multiprocessing.Process(target=scp_transfer, name="SCP transfer")
            time_process.start()
            time_process.join(5)
            # If the upload takes longer than 5 seconds the program throws an error as it should not take that long. 
            if time_process.is_alive():
                time_process.terminate()
                messagebox.showerror('Transfer Error!','An error occured during the transfer of the protocol file to the robot.')
                try:
                    time_process.close()
                except ValueError:
                    print("Time process still running")
            else:
                # If the upload of the protocol file is successful, powershell tries to run to connect to the robot.
                try:
                    # Launch the new protocol using
                    # ssh -i <key> <login> <command>
                    # -t creates a pseudo terminal on the remote machine (?)
                    # sh -lic makes the following command (c) (opentrons_execute <file>) run in an interactive (i) and login (l) shell.
                    # This is required to initialize everything correctly, else cannot use magnetic module or find calibration data. 
                    subprocess.run(f'ssh -i {key_filename} {username}@{ip} -t "sh -lic" \'opentrons_execute {protocol_robot_filepath}{protocol_name}\'')
                except:
                    messagebox.showerror('Error', 'There was an error running the powershell SSH connect command.')
                '''

        if self.protocol_type == 'qpcr_output.py':
            # Upload the new protol using 
            # # scp -i <key> <file_to_upload> <where_to_place_it>
            #subprocess.run(f'scp -i {key_filename} {protocol_qpcr_local_filepath}{protocol_qpcr_name} {username}@{ip}:{protocol_robot_filepath}{protocol_qpcr_name}')
            print(f'would have run:\nsubprocess.run(scp -i {key_filename} {protocol_qpcr_local_filepath}{protocol_qpcr_name} {username}@{ip}:{protocol_robot_filepath}{protocol_qpcr_name}')
            
            # Launch the new protocol using
            # ssh -i <key> <login> <command>
            # -t creates a pseudo terminal on the remote machine (?)
            # sh -lic makes the following command (c) (opentrons_execute <file>) run in an interactive (i) and login (l) shell.
            # This is required to initialize everything correctly, else cannot use magnetic module or find calibration data. 
            #subprocess.run(f'ssh -i {key_filename} {username}@{ip} -t "sh -lic" \'opentrons_execute {protocol_robot_filepath}{protocol_qpcr_name}\'')
            print(f'would have run:\nsubprocess.run(ssh -i {key_filename} {username}@{ip} -t "sh -lic" \'opentrons_execute {protocol_robot_filepath}{protocol_qpcr_name}\')')


class Check_window():
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title('test title')
        self.frame = tk.Frame(self.window)
        self.frame.pack() # Show frame on window

        self.test_label = ttk.Label(self.frame, text='test')
        self.test_label.grid(row=0, column=0, padx=10, pady=10)

        self.image = tk.PhotoImage(file='qpcr\\test.gif')
        self.img_label = ttk.Label(self.frame, image=self.image)
        self.img_label.grid(row=0, column=1) # Show imgage on frame
        

        # "You need to keep an additional reference to [image] so it 
        # doesn't get prematurely garbage collected at the end of the
        # function.
        # ...'Note: When a PhotoImage object is garbage-collected by 
        # Python (e.g. when you return from a function which stored 
        # an image in a local variable), the image is cleared even if
        # it’s being displayed by a Tkinter widget. 
        # To avoid this, the program must keep an extra reference to 
        # the image object.'
        # ...You could attach the image to you self variable"
        # "[image] is referenced in the line that creates the photo object,
        # but the reference count for photo still drops to zero at the end 
        # of the expression, and photo ceases to exist. This behavior can be
        # surprising because most custom classes will retain at least one 
        # reference to any arguments that it needs to make use of later. 
        # But Label and other Tkinter widgets are essentially thin wrappers 
        # over Tcl classes implemented in C, which don't go out of their way 
        # to handle the reference counts of its arguments.""
        # https://stackoverflow.com/questions/27430648/tkinter-vanishing-photoimage-issue

        # Behöver alltså ej längre global på objektet som skapas från klassen
        # utan endast följande, vilket knyter image till själva img_label-objectet. 
        self.img_label.image = self.image 

def run_gui():
    # Creates a root window
    root = tk.Tk()
    root.title('Protocol selector test')

    # Creates a frame for the root window with widgets for protocol selection. 
    Selector()
    #Checkbox('qpcr_output.py')
    #Checkbox('dna_cleaning_output.py')

    root.mainloop()

# Small function to enable multiprocessing later - used only for error-checking.
def scp_transfer():
    subprocess.run(f'scp -i {key_filename} {protocol_local_filepath}{protocol_name} {username}@{ip}:{protocol_robot_filepath}{protocol_name}')
    return  

# Main if-statement that runs the program.
if __name__ == '__main__':
    # Runs the main program.
    run_gui()