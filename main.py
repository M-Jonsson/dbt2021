####################################
#   Tkinter GUI for the DNA purification protocol using SPRI beads and the qPCR protocol.
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

import os
import sys
import multiprocessing
from multiprocessing.context import ProcessError
import subprocess
import queue
import socket
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import replace_values
import replace_values_qpcr


# Files and logins for SSH and SCP
local_user = os.getlogin() # os.getlogin() gives username on local machine
key_filename = f'c:\\users\\{local_user}\\opentrons\\ot2_ssh_key'
protocol_local_filepath = f'dna_cleaning\\'
protocol_robot_filepath = '/data/user_storage/'
protocol_dna_name = 'dna_cleaning_output.py'
ip1 = '169.254.29.201' #standard ip
ip2 = '169.254.99.249' #secondary ip
username = 'root'
protocol_qpcr_local_filepath = f'qPCR\\'
protocol_qpcr_name = 'qpcr_output.py'

font = (16)


class Selector():
    """
    Creates a frame with widgets used to select which protocol to run. The frame will be added to the root window when 
    initialized and destroyed (closed) when another class containing a new frame is called. 

        Attributes:
            --
        
        Methods:
            select_protocol_beads():
                Creates the frame used for editing the magnetic bead DNA purification protocol.
            select_protocol_qpcr():
                Creates the frame used for the qPCR protocol.
    """

    def __init__(self):
        """
        Constructs Tkinter class variables for the Selector() object.

            Parameters:
                self:           Allows the function to access class attributes and methods
        
            Returns:
                Nothing.
        """
        # Main frame for the protocol selection, to which all associated widgets are added
        self.frame = tk.Frame()
        self.frame.grid()
        self.s = ttk.Style()
        self.s.configure('my.TButton', font=('Helvetica', 12), background = 'grey')
        self.s.configure('small.TButton', font=('Helvetica', 11), background = 'grey')
        self.s.configure('my.TLabel', font =('Helvetica', 15))
        self.s.configure('text.TLabel', font=('Helvetica', 11))

        self.label_selection_info = ttk.Label(self.frame, text='Select a protocol', style ='my.TLabel', anchor="e", justify="right")
        self.label_selection_info.grid(row=0,column=0,columnspan=2, padx=20, pady=20)

        self.button_beads = ttk.Button(self.frame, text='SPRI beads\nDNA purification', command=self.select_protocol_beads,style='my.TButton')
        self.button_beads.grid(row=1, column=0, padx=10, pady=10, ipadx=5, ipady=1)

        self.button_qpcr = ttk.Button(self.frame, text='qPCR protocol', command=self.select_protocol_qpcr,style='my.TButton')
        self.button_qpcr.grid(row=1, column=1, padx=10, pady=10, ipadx=10, ipady=10)

        #self.button_test = ttk.Button(self.frame, text='Test', command=self.test,style='my.TButton')
        #self.button_test.grid(row=1, column=2, padx=10, pady=10,ipadx=10, ipady=10)

    def select_protocol_beads(self):
        """
        Closes the frame created by the Selector() class, but not the root window. Then creates a new frame 
        from the Bead_protocol_config() class for editing a SPRI bead DNA purification protocol.

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing
        """

        self.frame.destroy()
        Bead_protocol_config()

    def select_protocol_qpcr(self):
        """
        Closes the frame created by the Selector() class, but not the root window.
        Then creates a new frame with the qPCR_protocol_config() class.

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing
        """

        self.frame.destroy()
        qPCR_protocol_config()
   

class Bead_protocol_config():
    """
    Creates a frame containing widgets used to configure a magnetic bead DNA purification protocol.
    The frame will be added to the root window when initialized and destroyed (closed) when another 
    class containing a new frame is called.

        Attributes:
            --
        
        Methods:
            call_checkbox_beads():
                Calls the Checkbox() class.
            ok_button():
                Checks if entered values are valid and creates the new protocol.
            get_estimate():
                Simulates the protocol using opentrons_simulate.exe to get an estimate of how long it will take to run the protocol.
            back_button():
                Closes the current frame and opens the a new frame from the Selector() class
    """

    def __init__(self):
        """
        Constructs Tkinter class variables for the Bead_protocol_config() object.

            Parameters:
                self:           Allows the function to access class attributes and methods
        
            Returns:
                Nothing.
        """
        # Main frame for the protocol editing, to which all associated widgets are added
        self.frame = tk.Frame()
        self.frame.grid()

        # Labels
        self.label_sample_no = ttk.Label(self.frame, text='Number of samples: \n(Valid values between 1-96 samples)', style='text.TLabel')
        self.label_sample_vol = ttk.Label(self.frame, text='Sample volume: \n(Valid values between 15-40 μl)', style='text.TLabel')
        self.label_bead_ratio = ttk.Label(self.frame, text='Bead:Sample ratio: \n(Valid ratios between 0.5-1.5)', style='text.TLabel')
        self.label_ethanol = ttk.Label(self.frame, text='Number of ethanol washes: ', style='text.TLabel')
        self.label_eb = ttk.Label(self.frame, text='Elution buffer volume: \n(Valid values between 15-25 μl)', style='text.TLabel')

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
        self.button_ok = ttk.Button(self.frame, text='Create robot protocol', command=self.ok_button, style='small.TButton')
        self.button_ok.grid(row=10, column=0, padx=10, pady=10)

        self.button_back = ttk.Button(self.frame, text='Back', command=self.back_button, style='small.TButton')
        self.button_back.grid(row=15, column=1, padx=10, pady=10)

        self.button_estimate = ttk.Button(self.frame, text='Estimate time', command=self.get_estimate, style='small.TButton', state=tk.DISABLED)
        self.button_estimate.grid(row=10, column=1, padx=10, pady=10)

        self.prepare_for_run = ttk.Button(self.frame, text='Next', command=self.call_checkbox_beads, style='small.TButton', state=tk.DISABLED)
        self.prepare_for_run.grid(row=15, column=0, padx=10, pady=10)
    
    def call_checkbox_beads(self):
        """
        Creates a new window with a Checkbox() object that is given
        information about the entered protocol values as arguments.

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing
        """

        sample_no = int(self.entry_sample_no.get())
        sample_vol = float(self.entry_sample_vol.get())
        ratio = float(self.entry_bead_ratio.get())
        EB=float(self.entry_eb.get()) 
        etoh=self.ethanol_var.get()

        if sample_no < 8:
            self.image_path = 'Deck Images\\deck_less_8.gif'
        else:
            self.image_path = 'Deck Images\\deck_96.gif'

        self.window = tk.Toplevel()
        self.list_frame = ttk.Frame(self.window)
        self.list_frame.grid(row=0, column=0)
        self.image_frame = ttk.Frame(self.window)
        self.image_frame.grid(row=0, column=1)

        checkbox = Checkbox(parent=self.list_frame, protocol_type=protocol_dna_name, num_samples=sample_no, sample_vol=sample_vol, ratio=ratio, EB=EB, etoh=etoh)
        checkbox.add_image(self.image_frame, self.image_path)
        self.window.grab_set()

    def ok_button(self):
        """ 
        Checks if all entries are valid. If valid, will create a
        modified protocol with the value given by the user by calling
        replace_values() to edit an existing protocol blueprint.

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing
        """

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
                messagebox.showerror('Notice', 'Volume amount is too low or too high, choose a volume between 15-40 µl')
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
                messagebox.showerror('Notice', 'EB volume is too low or too high, choose an EB volume between 15-25 µl')
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
                    messagebox.showinfo('Success!', 'Successfully entered parameters into the protocol')

                    # Allow starting or simulating the now created protocol
                    self.button_estimate.config(state=tk.NORMAL)
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


    def get_estimate(self):
        """
        Simulates the protocol using the opentrons_simulate.exe command with the experimental 
        time estimate feature enabled (-e flag). Shows the result in a message box.

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing 
        """
        run = subprocess.run(f"opentrons_simulate.exe -e {protocol_local_filepath}{protocol_dna_name}", capture_output=True, text=True)
        self.beads_estimate = run.stdout.split('\n')[-4]
        messagebox.showinfo('Protocol estimate', f'{self.beads_estimate}')
    
    def back_button(self):
        """
        Closes the current frame for protocol editing and replaces it with a frame for protocol selection
        by calling the Selector() class.

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing 
        """
        self.frame.destroy()
        Selector()

class qPCR_protocol_config():
    """
    Creates a frame with widgets used for the creating and running a qPCR protocol.
    The frame will be added to the root window when initialized 
    and destroyed (closed) when another class containing a new frame is called. 

        Attributes:
            --
        
        Methods:
            call_checkbox_qpcr():
                Calls the Checkbox() class.
            open_file_dialog():
                Opens a file dialog for csv-files
            get_estimate():
                Simulates the protocol to get an estimate of how long it will take to run the protocol.
            back_button():
                Closes the current frame and opens the a new frame from the Selector() class
    """
    def __init__(self):
        """
        Constructs Tkinter class variables for the qPCR_protocol_config() object.

            Parameters:
                self:           Allows the function to access class attributes and methods
        
            Returns:
                Nothing.
        """
        self.frame = tk.Frame()
        self.frame.grid()

        self.file_label = ttk.Label(self.frame, text='File:', style='my.TLabel')
        self.file_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W)

        self.file_name_label = ttk.Label(self.frame, text='No file chosen', foreground='red', style='my.TLabel')
        self.file_name_label.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W)

        self.open_file_dialog_button = ttk.Button(self.frame, text='Choose a file', command=self.open_file_dialog, style='my.TButton')
        self.open_file_dialog_button.grid(row=5, column=0, padx=10, pady=5, ipadx=10, ipady=5)    
        
        self.estimate_button = ttk.Button(self.frame, text='Estimate time', command=self.get_estimate, state=tk.DISABLED, style='my.TButton')
        self.estimate_button.grid(row=5, column=2, padx=10, pady=10, ipadx=10, ipady=5)
        
        self.button_back = ttk.Button(self.frame, text='Back', command=self.back, style='my.TButton')
        self.button_back.grid(row=10, column=2, padx=10, pady=10, ipadx=10, ipady=5)  

        self.prepare_for_run = ttk.Button(self.frame, text='Next', command=self.call_checkbox_qpcr, state=tk.DISABLED, style='my.TButton')
        self.prepare_for_run.grid(row=10, column=0, padx=10, pady=10, ipadx=10, ipady=5)

        self._sources = None # klassvariabel som sparar dictionary med sources
    
    def call_checkbox_qpcr(self):
        """
        Creates a new window and adds a Checkbox() object that is given
        information about the protocol values as arguments.

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing
        """

        self.window = tk.Toplevel()
        self.frame_list = tk.Frame(self.window)
        self.frame_list.grid(row=0, column=0)

        checkbox = Checkbox(parent=self.frame_list, protocol_type='qpcr', qpcr_sources=self.sources, qpcr_destinations=self.destinations, qpcr_filepath=self.filepath)

        checkbox.add_tube_racks(self.window, self.sources, self.destinations)
        self.window.grab_set()


    def open_file_dialog(self):
        """
        Opens a file dialog window that allows you to select a csv-file to be read
        for the qPCR protcol. Creates a protocol by calling csv_till_lista() and 
        replace_values_qpcr().

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing
        """
        self.filepath = filedialog.askopenfilename(filetypes=(('CSV files','*.csv'),))
        if self.filepath:
            [self.destinations, self.sources] = replace_values_qpcr.csv_till_lista(self.filepath)

            self._sources = self.sources
            replace_values_qpcr.replace_values_qpcr(self.destinations, self.sources)

            # Enable locked buttons
            self.estimate_button.config(state=tk.NORMAL)
            self.prepare_for_run.config(state=tk.NORMAL)
            # Show name of chosen file
            self.file_name_label.config(text=self.filepath.split('/')[-1], foreground='green', style='text.TLabel')
            self.file_name_label.grid(row=1, column=0, columnspan=3, padx=10, pady=8, sticky=tk.W)

    def get_estimate(self):
        """
        Simulates the protocol using the opentrons_simulate.exe command with the experimental 
        time estimate feature enabled (-e flag). Shows the result in a message box.

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing 
        """
        run = subprocess.run(f"opentrons_simulate.exe -e {protocol_qpcr_local_filepath}{protocol_qpcr_name}", capture_output=True, text=True)
        self.qPCR_estimate = run.stdout.split('\n')[-4]
        messagebox.showinfo('Protocol estimate', f'{self.qPCR_estimate}')

    def back(self):
        """
        Closes the current frame for protocol editing and replaces it with a frame for protocol selection
        by calling the Selector() class.

            Parameters:
                self:           Allows the function to access class attributes and methods

            Returns:
                Nothing 
        """
        self.frame.destroy()
        Selector()

class Tube_rack_base():
    """
    Base frame with notebook tabs. Function to add new tabs.
    Parent is which window to add it to.

        Attributes:
            parent:         Which frame/window to add the notebook to
        
        Methods:
            new_tab():
                Creates a new tab on the notebook with the given title.
            fill_notebook():
                Populates the notebook with tables for each needed tube rack in separate tabs.
    """
    def __init__(self, parent):
        """
        Constructs Tkinter class variables for the Tube_rakc_base() object.

            Parameters:
                parent:         Which frame/window to add the notebook to

            Returns:
                Nothing.
        """
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        # Create notebook (tabs) associated with the window
        self.notebook = ttk.Notebook(self.frame)

        self.frame.pack()
        self.notebook.grid(row=0, column=1)

    def new_tab(self, title):
        """
        Adds another tab to the tube rack notebook.

            Parameters:
                self:                 Allows the function to access class attributes and methods
                title (str):          The name of the new tab in the notebook

            Returns:
                self.tab_frame 
        """
        self.tab_frame = tk.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text=title)
        return self.tab_frame

    def fill_notebook(self, sources, destinations):
        """
        Loops through mastermix, samples and standard dictionaries and checks how many
        tube racks, and by extension how many tabs in the notebook, are needed.

            Parameters:
                self:                  Allows the function to access class attributes and methods
                sources (dict):        Dictionary containing sources for msatermixes, samples and standards
                destinations (dict):   Dictionary containing destinations for mastermixes, samples and standards

            Returns:
                Nothing.
        """
        # Variable to keep track of the loops
        tube_racks = []

        self.sources = sources
        self.destinations = destinations

        # Loop through each type of group (mastermix, sample, standard)
            # and each mixture in a group (each mastermix etc.)
        for group_name, group_content in self.sources.items():
            for mixture, [tube_rack, well] in group_content.items():
                # Checks if a new tab=new tube rack is needed.
                if tube_rack not in tube_racks:
                    # Create a new tab in the notebook and add a grid to it.
                    trw_tab = self.new_tab(tube_rack)
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
    
class Tube_rack_grid():
    """
    Creates a tube rack layout grid used in the base notebook and its tabs.

        Attributes:
            parent:         Which frame/window to add the tube rack grid to
        
        Methods:
            edit():
                Edits the grid at a specific position.
    """
    def __init__(self, parent):
        """
        Constructs Tkinter class variables for the Tube_rack_grid() object.

            Parameters:
                parent:         Which window/frame to add the grid to
        
            Returns:
                Nothing.
        """
        # Creates a frame assigned to the specified parent widget.
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.frame.grid()

        # Headers on the grid.
        self.header_letters = ['A', 'B', 'C', 'D']
        self.header_numbers = [str(i) for i in range(1, 7)]

        # Place headers on grid, letters on left-most column and numbers on upper-most row.
        for i, row_letter in enumerate(self.header_letters):
            ttk.Label(self.frame, text=row_letter, foreground='grey').grid(row=i+1, column=0, padx=20, pady=20)
        for i, col_num in enumerate(self.header_numbers):
            ttk.Label(self.frame, text=col_num, foreground='grey').grid(row=0, column=i+1, padx=20, pady=20)
        
        # Fill rest of grid with 'Empty'
        for i in range(len(self.header_letters)):
            for j in range(len(self.header_numbers)):
                ttk.Label(self.frame, text='Empty', foreground='black', justify='center').grid(row=i+1, column=j+1, padx=20, pady=20)

    def edit(self, xy, new_text):
        """
        Edits the tube rack grid on a specific position.

            Parameters:
                self:               Which window/frame to add the grid to
                xy (str):           Which position on the grid to edit, given in the form of e.g. 'A1'.
                new_text (str):     New text for the given position. 
        
            Returns:
                Nothing.
        """
        row_index_to_letter = {0:None, 1:'A', 2:'B', 3:'C', 4:'D'}
        # Loop through each label on the grid
        for child_values in self.frame.children.values():
            # Find row and column index for each label and convert to well name
            child_x = row_index_to_letter[child_values.grid_info()['row']]
            child_y = str(child_values.grid_info()['column'])
            # Edit label text when the correct well is found
            if child_x == xy[0] and child_y == xy[1]:
                child_values.configure(text=str(new_text))
                break

class Checkbox:
    """
    Creates the Checkbox window and checks from which protocol it was launched from, in order to load the correct
    information.

        Attributes:
            parent:                 Which frame/window to add the notebook to
            ip (str):               The ip to the OT-2 robot
            protocol_type (str):    Either the qPCR or the DNA purification protocol
        
        Methods:
            add_image():
                Adds an image of the robot deck to the checkbox window.
            add_tube_racks():
                Adds the notebook for tube racks as well as the image of the robot deck, if the protocol is qPCR.
            check_ssh():
                Creates a Queue object used to determine if a ssh connection can be established.
            try_connection():
                Checks if an item is returned from the Queue object, i.e a connection was established.
            run_protocol():
                Uploads the protocol using the scp_transfer() function and then executes the run. Times out if it takes longer than 5 seconds.
                Also checks if the protocol was completed successfully or not.
            scp_transfer():
                Function used for multiprocessing, uploads the protocol to the robot, used in the run_protocol() function.
            execute_run():
                Runs the protocol on the robot, used in the run_protocol() function.
            quit():
                Asks the user if they want to exit the program, if yes, quits in a safe manner.
            change_ip():
                A function that changes between the two most common ip-addresses to the robot.
            create_printable_file()
                Creates a summary of all tube racks in a .txt file in the same directory as the .csv used as template.  
    """
    def __init__(self, parent, protocol_type: str, num_samples=None, sample_vol=None, ratio=None, EB=None, etoh=None, qpcr_sources=None, qpcr_destinations=None, qpcr_filepath=None):
        """
        Constructs Tkinter class variables, methods and parameters needed for the Checkbox() object.

            Parameters:
                parent:                     Which window/frame to add the checkbox to
                protocol_type (str):        The protocol
                num_samples (int):          The number of samples
                sample_vol (int):           Volume of one sample
                ratio (float):              The sample/SPRI-bead ratio
                EB (int):                   Amount of EB used for elution
                etoh (int):                 Number of ethanol washes
                qpcr_sources (dict):        Which well has which mixture on which tube rack in qPCR protocols.
                qpcr_destinations(dict):    Which well on the PCR plate will get which mixture in qPCR protocols. 
                qpcr_filepath(dict):        Filepath to the .csv file that a qPCR protocol gets made from. 

            Returns:
                Nothing.
        """
        
        self.ip = ip1
        self.parent = parent
        self.frame = ttk.Frame(self.parent)
        self.frame.pack()
        self.protocol_type = protocol_type

        # Layout differences between the protocols.
        if self.protocol_type.startswith('qpcr'): # qPCR protocol'
            self.protocol = [protocol_qpcr_local_filepath, protocol_qpcr_name]
            self.image_name = 'Deck Images\\deck_qpcr.gif'
            self.pipette_text = '\n     Left: P10 single-channel\
                \n     Right: Any'
            self.volumes_label = '4. Fill each tube rack according to its tab\
                \n    The tabs can be selected on the row above the image\
                \n\n5. Do not forget the aluminum block under the PCR plate'
            self.pause_info_text = '\n Pause the protocol by opening the robot door\
                \n Resume the protocol by closing the robot door'

            # Button calls lambda function which in turn calls the real function.
            # Used to be able to pass arguments to the real function.
            self.print_file_button = ttk.Button(self.frame, text='Print layout\n  to file', command=lambda: self.create_printable_file(qpcr_sources, qpcr_destinations, qpcr_filepath), style='my.small.TButton')

            self.print_file_button.grid(row=22, column=1, padx=20, pady=10, ipadx=10, ipady=3)

        elif self.protocol_type.startswith('dna') and num_samples >= 8: # 8-96 DNA cleaning
            columns=math.ceil(num_samples/8)
            beads=sample_vol*ratio*columns+60
            vol_eb=EB*columns+60
            vol_etoh=etoh*200+100

            self.protocol = [protocol_local_filepath, protocol_dna_name]
            # self.image_name = 'Deck Images\\deck_96.gif'
            self.pipette_text = '\n     Left: P10 8-channel\
                \n     Right: P300 8-channel'
            self.volumes_label = '     SPRI beads: '+str(beads)+' µl per well\
                \n     Elution buffer: '+ str(vol_eb)+ ' μl per well\
                \n     EtOH: Fill the wells on the EtOH plate\n               corresponding to the wells with samples;\
                \n               '+ str(vol_etoh)+ ' μl per well'
            self.pause_info_text = '\n Pause the protocol by opening the robot door\
                \n Resume the protocol by closing the robot door'
            
            self.image_frame = ttk.Frame(self.frame)
            self.image_frame.grid(row=0, column=1)
            # self.add_image(self.image_frame, self.image_name)

        elif self.protocol_type.startswith('dna') and num_samples < 8: # 1-7 DNA cleaning
            columns=math.ceil(num_samples/8)
            beads=sample_vol*ratio*columns+60
            vol_eb=EB*columns+60
            vol_etoh=etoh*200+100
            
            self.protocol = [protocol_local_filepath, protocol_dna_name]
            # self.image_name = 'Deck Images\\deck_less_8.gif'
            self.pipette_text = '\n     Left: P10 8-channel\
                \n     Right: P300 8-channel'
            self.volumes_label = '     SPRI beads: '+str(beads)+' µl per well\
                \n     Elution buffer: '+ str(vol_eb)+ ' μl per well\
                \n     One Cleaning: Fill column 5 with 200µl EtOH on the liquids plate\
                \n     Two Cleaning: Fill column 5 & 6 with 200µl EtOH on the liquids plate'
            self.pause_info_text = '\n Pause the protocol by opening the robot door\
                \n Resume the protocol by closing the robot door'
            # self.add_image(self.frame, self.image_name)

        else:
            messagebox.showerror('Error', f"Invalid protocol type '{self.protocol_type}' entered.")
    
        # Buttons
        self.connection_button = ttk.Button(self.frame, text='Check Connection', command= self.check_ssh, style='my.small.TButton')
        self.connection_button.grid(row=3, column=1, rowspan=2, padx=20, pady=10, ipadx=5, ipady=5, sticky=tk.W)
        
        self.run_protocol_button = ttk.Button(self.frame, text='Run Protocol', command= self.run_protocol, state='disabled', style='my.small.TButton')
        self.run_protocol_button.grid(row=22, column=2, padx=20, pady=10, ipadx=5, ipady=5, sticky=tk.W)

        self.quit_protocol_button = ttk.Button(self.frame, text='Exit', command= self.quit, style='my.small.TButton')
        self.quit_protocol_button.grid(row=22, column= 3, padx=20, pady=10, ipadx=10, ipady=5)

        # Labels
        self.label1 = ttk.Label(self.frame, text='1. Check the ssh-connection', font=font)
        self.label1.grid(row=0, column=1, sticky=tk.W, padx=20, pady=10, columnspan=3)

        self.label2 = ttk.Label(self.frame, text='2. Check the pipettes:' + self.pipette_text, font=font)
        self.label2.grid(row=5, column=1, sticky=tk.W, padx=20, pady=10, columnspan=3)

        self.label3 = ttk.Label(self.frame, text='3. Load the robot deck according to the picture', font=font)
        self.label3.grid(row=10, column=1, sticky=tk.W, padx=20, pady=10, columnspan=3)
    
        self.volumes = ttk.Label(self.frame, text=self.volumes_label, font=font)
        self.volumes.grid(row=11, column=1, sticky=tk.W, padx=20, pady=10, columnspan=3)

        self.pause_info = ttk.Label(self.frame, text=self.pause_info_text, font=font,foreground='red')
        self.pause_info.grid(row=20, column=1, sticky=tk.W, padx=20, pady=10, columnspan=3)

        self.connection_status = ttk.Label(self.frame, text='   Check connection\n     to continue', font=font, foreground= 'red')
        self.connection_status.grid(row=3, column=2, columnspan =2, sticky=tk.NW, padx=20, pady=0)

    def add_image(self, parent, image_path):
        """
        Adds an image to the checkbox window.

            Parameters:
                self:                   Allows the function to access class attributes and methods
                parent:                 Which window/frame to add the checkbox to
                image_path (str):       The filepath to the image
        
            Returns:
                Nothing.
        """
        self.image = tk.PhotoImage(file=image_path)
        self.img_label = ttk.Label(parent, image=self.image)
        self.img_label.grid(row=0, column=5, rowspan=30) # Show imgage on frame
    
    def add_tube_racks(self, parent, sources, destinations):
        """
        Adds the image and the notebook for tube racks to the checkbox object, used for qPCR.

            Parameters:
                self:                   Allows the function to access class attributes and methods
                parent:                 Which window/frame to add the checkbox to
                sources (dict):         Dictionary of which well on which tube rack each mixture is taken from.
                destinations (dict):    Dictionary of which well on the PCR each mixture is to be added to.
        
            Returns:
                Nothing.
        """
        self.parent = parent
        self.frame_tube_racks = tk.Frame(self.parent)
        self.frame_tube_racks.grid(row=0, column=1)

        base = Tube_rack_base(self.frame_tube_racks)

        self.deck_tab = base.new_tab('Deck')
        self.add_image(self.deck_tab, 'Deck Images\\deck_qpcr.gif')

        base.fill_notebook(sources, destinations)

    def check_ssh(self):
        """
        Checks if it is possible to connect by SSH. Creates a Queue object and passes it to a Process subclass, Threaded_ssh_check().
        The queue creates a connection between the main process (the UI) and this new process. When the process is started, 
        its run() method is executed, which tries to create a socket connection to the robot ip.
        After 1 second, calls try_connection() to check if the queue is empty, i.e. if the attempts at creating a socket conneciton is 
        finished. If not, checks again in 3 seconds.
            
            Parameters:
                self:                   Allows the function to access class attributes and methods
        
            Returns:
                Nothing. 
        """

        self.connection_status.config(text='    Checking connection...', foreground='black')
        self.connection_status.update()
        
        self.valid_connection = False

        self.connection_progress = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, length=200, mode='indeterminate', )
        self.connection_progress.grid(row=4, column=2, padx=10, columnspan=2, sticky=tk.W)
        self.connection_progress.start(10)
        self.connection_progress.update()

        self.connection_button.config(state=tk.DISABLED)


        self.queue = multiprocessing.Queue()
        self.process = Threaded_ssh_check(self.queue, self.ip)
        self.process.start()

        self.connection_progress.after(1000, self.try_connection)
 
    def try_connection(self):
        """
        Checks if a connection can be established and prepares the robot for running a protocol. If an item was returned by the get_nowait()
        function then a connection was established. If no item was returned and the Empty exception wasn't raised, then a connection couldn't
        be established. If the Empty exception is raised it tries to establish a connection again after 3 seconds.
            
            Parameters:
                self:                   Allows the function to access class attributes and methods
        
            Returns:
                Nothing. 
        """
        try:
            # valid_connection = True
            valid_connection = self.queue.get_nowait()
        except queue.Empty:
            print(f'Attempting to connect to {self.ip}')
            self.connection_progress.after(3000, self.try_connection)
        else:
            if not valid_connection:
                self.connection_button.config(state=tk.NORMAL)
                self.connection_status.config(text='   Connection failed', foreground='red')
                self.connection_progress.destroy()
                self.change_ip()
                
            elif valid_connection:
                self.connection_button.config(state=tk.NORMAL)
                self.run_protocol_button.config(state=tk.NORMAL)
                self.connection_status.config(text='   Connection OK', foreground='green')
                self.connection_progress.destroy()

                print('Preparing robot to run by stopping opentrons-robot-server')
                subprocess.run(f'ssh -i {key_filename} {username}@{self.ip} -t "sh -lic" \'systemctl stop opentrons-robot-server\'')
   
    def run_protocol(self):
        """
        Uploads the new protocol using: scp -i <key> <file_to_upload> <where_to_place_it>
        Then launches the new protocol using: ssh -i <key> <login> -t "sh -lic" <command> -t
        The sh -lic makes the following command (c) run in an interactive (i) and login (l) shell,
        which is required to initialize everything correctly. Else the robot cannot use 
        any labware or find calibration data. 

            Parameters:
                self:                   Allows the function to access class attributes and methods
        
            Returns:
                Nothing. 
        """
        
        # Upload the new protocol using 
        # scp -i <key> <file_to_upload> <where_to_place_it>
        # Defines the multiprocess to be able to handle errors when transferring the protocol to the robot via SCP.
        time_process = multiprocessing.Process(target=self.scp_transfer(self.protocol), name="SCP transfer")
        time_process.start()
        time_process.join(5)
        # Throws an error if the upload takes more than 5 seconds as it should happen almost instantly. 
        if time_process.is_alive():
            time_process.terminate()
            messagebox.showerror('Transfer Error!','An error occured during the transfer of the protocol file to the robot.')
            try:
                time_process.close()
            except ValueError:
                print('Time process still running')
        else:
            # Successful upload with scp so continue to execution. 
            try:
                log = self.execute_run()
            except ProcessError:
                print('There was an error starting the run.')

            # The protocol has "print('Protocol Complete')" as a final step.
            if 'Protocol Complete' in log:
                # self.run_complete(True)
                messagebox.showinfo('Run Completed', 'Protocol was completed successfully!', parent=self.parent)
            else:
                # self.run_complete(False)
                messagebox.showwarning('Run Failed!', 'Protocol was canceled before completing,\neither due to an error or it was canceled by the user.', parent=self.parent)
    
    def scp_transfer(self, protocol):
        """
        Uploads a protocol using scp.
        Done as a separate function to enable checking for errors.

            Parameters:
                self:                   Allows the function to access class attributes and methods
                protocol (str):         The protocol that is uploaded to the robot.
        
            Returns:
                Literally nothing. 
        """
        subprocess.run(f'scp -i {key_filename} {protocol[0]}{protocol[1]} {username}@{self.ip}:{protocol_robot_filepath}{protocol[1]}')
        return  

    def execute_run(self):
        """
        Starts the robot by calling for 'opentrons_execute' over SSH using a subprocess.
        Saves the output in a log, which is also continuously printed so that it is also visible
        to the user. 

            Parameters:
                self:               Allows the function to access class attributes and methods
            
            Returns:
                log (list):         Output from the subprocess as a list. 
        """
        # Start subprocess to run command over SSH.
        command = f'ssh -i {key_filename} {username}@{self.ip} -t "sh -lic" \'opentrons_execute {protocol_robot_filepath}{self.protocol[1]}\''
        process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
        log = []
        for line in process.stdout:
            print(line.strip())
            log.append(line.strip())
        return log

    def quit(self):
        """
        Restarts the opentrons-robot-server before closing the program
        if the user chooses "yes" when asked.

            Parameters:
                self:               Allows the function to access class attributes and methods
            
            Returns:
                Nothing.
        """
        exit_choice = messagebox.askyesno('Quitting', 'This will close the program and prepare the robot to shut down.\nDo you want to continue?', parent=self.parent)
        if exit_choice:
            print('Shutting down...')
            subprocess.run(f'ssh -i {key_filename} {username}@{self.ip} -t "sh -lic" \'systemctl start opentrons-robot-server\'')
            sys.exit(0)
    
    def change_ip(self):
        """
        Alternates between the two most common ip addresses.
        Made for if the ssh_check fails in order to try another next attempt.

            Parameters:
                self:               Allows the function to access class attributes and methods
            
            Returns:
                Nothing.
        """
        if self.ip == ip1:
            self.ip = ip2
        elif self.ip == ip2:
            self.ip = ip1
  
    def create_printable_file(self, sources: dict, destinations: dict, filepath_csv: str):
        """Creates a .txt file showing the volume needed for each
        mastermix, sample and stadard, as well as how to place it
        on the tube racks/cooling blocks.
        Saves the file in the same directory as the .csv it is based on.

            Parameters:
                sources (dictionary):       Dictionary of source wells (tube racks).
                destinations (dicitonary):  Dicitonary of destination wells (PCR plate).
                filepath_csv (str):         Filepath of .csv that the protocol is based on.

            Returns:
                Nothing.
        """
        filepath_base = filepath_csv.split('/')[:-1]
        original_file = filepath_csv.split('/')[-1].split('.')[0]
        new_file = f'qpcr_robot_layout_{original_file}.txt'
        filepath_output = '/'.join(filepath_base) + '/' + new_file
        print(filepath_output)

        with open(filepath_output, 'w') as file:
            file.write(f'Robot preparation based on {original_file}.csv.\n')
            file.write('    Note: The volumes shown are for N+3 reactions.\n\n')
            for type in destinations.keys():
                if type.startswith('mastermix'):
                    file.write('Mastermixes:\n')
                    vol = 6
                    source_key = 'mastermix_source'
                if type.startswith('sample'):
                    file.write('Samples:\n')
                    vol = 4
                    source_key = 'sample_source'
                if type.startswith('standard'):
                    file.write('Standards:\n')
                    vol = 4
                    source_key = 'standard_source'

                for mixture in destinations[type]:
                    [source_tuberack, source_well] = sources[source_key][mixture]
                    wells_num = len(destinations[type][mixture])
                    file.write(f'    {mixture}\
                        \n        Total volume: {vol*(wells_num+3)} ul        Place on {source_tuberack}, column {source_well[1]}, row {source_well[0]}.\n')

        messagebox.showinfo('Created printable file', f'A .txt file with a summary of the needed volumes has been placed in the same folder as the earlier provided .csv file.\n\nFile location:\n{filepath_output}', parent=self.parent)
     
class Threaded_ssh_check(multiprocessing.Process):
    """
    Subclass of multiprocessing.Process. When the process is started,
    a socket connection is attempted to the provided IP.
    The result of the connection attempt is communicated back by
    putting it into the provided queue. 

        Attributes:
            queue:                  The queue used to communicate between this process and the main UI.
            ip (str):               The ip address to attempt to connect to.         
        
        Methods:
            run:                    Creates a socket connection to the provided ip.        
    """
    def __init__(self, queue, ip):
        """
        Inherits the __init__() from multiprocessing.Process.

            Parameters:
                self:               Allows the function to access class attributes and methods
                queue (Queue):      The multiprocessing.Queue used to communicate between the process and main UI.
                ip (str):           THe ip address to attempt to connect to. 
            
            Returns:
                Nothing.
        """
        super().__init__()
        self.queue = queue
        self.ip = ip
    
    def run(self):
        """
        Creates a socket connection to the provided ip and returns
        the result by putting it back inte the provided queue.
        Automatically called by using the start() function on the object.

            Parameters:
                self:               Allows the function to access class attributes and methods
            
            Returns:
                Nothing.
        """
        host = self.ip
        port = 22
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(6)
            test_socket.connect((host, port))
        except (socket.error, socket.timeout) as error_msg:
            print(error_msg)
            self.queue.put(False)
        else:
            test_socket.close()
            self.queue.put(True)


def run_gui():
    """
    The main function that creates the Tkinter main window. Also calls the Selector() class. Raises an error if the ssh-key
    can't be found

        Parameters:
            Nothing.
            
        Returns:
            Nothing.
    """
    # Creates a root window
    root = tk.Tk()
    root.title('Protocol selector')

    # Creates a frame for the root window with widgets for protocol selection. 
    Selector()

    # Error check to see that the ssh_key exists.
    if os.path.isfile(key_filename):
        print(f'ssh-key found in {key_filename}.')
    else:
        messagebox.showerror('File not found error!', f'SSH Key could not be found.\n\nA new key can be created following the instructions on the Opentrons website.\nIf a new key has been created,\nplease make sure that the key is placed in: {key_filename}')
        
    root.mainloop()

if __name__ == '__main__':
    # Runs the main program.
    run_gui()
