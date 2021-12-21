# DBT2021 - Pipette robot automation
The OT-2 Protocol Selector program allows for creating and running protocol on the Opentrons OT-2 robot. The program supports SPRI beads DNA cleaning protocols and qPCR preparation protocols, which are constructed based on parameters input by the user or by a .csv file provided by the user, respectively. 
## General instructions
The general workflow when using the program is as follows:
1.	Turn on the robot using the power switch.
2.	Wait for the light on the front of the robot to shine with a steady blue light before plugging in the USB cable to a computer. 
3.	Start the OT-2 Protocol Selector program.
4.	Select the type of protocol that you want to work with.
  a.	For SPRI bead DNA cleaning: Enter the desired protocol parameters and press “Create robot protocol”.
  b.	For qPCR preparation: Press “Choose a file” and select the .csv file to base the protocol on.
5.	(Optional: Press “Estimate time” to simulate the protocol using an experimental function from the robot manufacturer to get a rough estimation on how long the robot will run for.)
6.	Press “Next”. A new window will open showing instructions on the necessary steps needed to prepare the robot for running the protocol.
7.	Check the connection to the robot by pressing the “Check connection” button. If the connection fails, try pressing the button a few more times, otherwise see the troubleshooting section for more information. 
8.	Following the instructions and load the robot deck according to the picture. When running a qPCR protocol, also load each tube rack according to its own tab.
9.	(Optional, for qPCR protocol only: Press “Print layout to file” to get a printable version of the tube rack layouts and the volumes needed. This will create a .txt file in the same folder as the provided .csv file, which then can be printed by the user if needed.)
10.	Once ready, press “Run protocol” to start the robot. The robot will output information about each step it is doing in the terminal window that also opens when starting the program. The robot can be paused by opening the front door.
11.	When the protocol is finished, closed the program by pressing the “Exit” button. Once the program has closed, the robot can be shut off using the power switch and the USB cable can be unplugged.
## Detailed instructions
For more details, see [the accompanying manual](ot2_protocol_selector_manual.pdf). The manual additionally contains instructions on how to use the official Opentrons app for procedures where that is necessary, such as changing pipettes and calibrating the robot. It also contains troubleshooting instructions and a description of the general structure of the code meant for advanced users that want to make modifications to the program. 
