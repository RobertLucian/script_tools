from __future__ import print_function
from __future__ import division

'''
THIS IS NOT A COPY OF ANOTHER FILE.
--John (June 2017)
'''

import sys
import time     # import the time library for the sleep function
from smbus import SMBus
import os
import serial
from shutil import copyfile

bus = SMBus(1)
detected_robot = "None"
detectable_robots = ["GoPiGo3","GoPiGo","BrickPi3","BrickPi+","GrovePi","PivotPi"]

def debug_print(in_str):
    if False:  # change to False to get all prints to shut up
        print(in_str)


def find_pivotpi():
    '''
    Boolean function that returns the presence of at least one PivotPi
    Checks all four possible addresses
    Returns True or False
    '''
    debug_print("Detecting PivotPi")
    pivotpi_found = False
    try:
        import pivotpi
        possible_addresses = [0x40,
                              0x41,
                              0x42,
                              0x43]
        for add in possible_addresses:
            try:
                p = pivotpi.PivotPi(add)
                pivotpi_found = True
            except:
                pass
    except:
        pass
    return pivotpi_found


def find_gopigo():
    '''
    boolean function that detects the presence of a GoPiGo
    returns True or False
    '''
    debug_print("Detecting GoPiGo")
    gopigo_address = 0x08
    try:
        import gopigo
        # print("DETECTED GOPIGO");
        test_gopigo = bus.read_byte(gopigo_address)
        return True
    except:
        # print("Unexpected error:", sys.exc_info()[0])
        # print("NOT DETECTED GOPIGO")
        return False


def find_gopigo3():
    '''
    boolean function that detects the presence of a GoPiGo3
    returns True or False
    '''
    debug_print("Detecting GoPiGo3")
    try:
        import gopigo3
        try:
            GPG3 = gopigo3.GoPiGo3()
            return True
        except gopigo3.FirmwareVersionError:
            return True
        except:
            return False
    except:
        return False


def find_grovepi():
    '''
    boolean function that detects the presence of a GrovePi
    ONLY HANDLES DEFAULT GrovePi ADDRESS
    returns True or False
    '''
    debug_print("Detecting GrovePi")
    grovepi_address = [0x04,
                       0x03,
                       0x05,
                       0x06,
                       0x07]
    grovepi_found = False
    for add in grovepi_address:
        try:
            test_grovepi = bus.read_byte(add)


            # if we have found a GoPiGo so far, and we're finding something at address 0x06
            # then assume it's a line follower and not a GrovePi

            if detected_robot.find("GoPiGo") != -1 and add == 0x06:
                grovepi_found = False
            else:
                grovepi_found = True
        except:
            pass
    return grovepi_found


def find_brickpi():
    '''
    boolean function that detects the presence of a BrickPi+
    returns True or False
    using try/except in case the BrickPi library is not found. Return False
    '''
    debug_print("Detecting BrickPi+")
    try:
        import ir_receiver_check
        if ir_receiver_check.check_ir():
            return False
        else:
            import BrickPi
            BrickPi.BrickPiSetup()
            #if BrickPiSetupSensors() == 0: # really slow
            if BrickPi.BrickPiUpdateValues() == 0:
                return True
            else:
                return False
    except:
        return False


def find_brickpi3():
    '''
    boolean function that detects the presence of a BrickPi3
    returns True or False
    '''
    debug_print("Detecting BrickPi3")
    try:
        import brickpi3
        try:
            BP3 = brickpi3.BrickPi3()
            return True
        except brickpi3.FirmwareVersionError:
            return True
        except:
            return False
    except:
        return False


def add_robot(in_robot):
    '''
    Add detected robot into a concatenated string,
    all robots are separated by a _
    Do not change the _ to another character as many places 
    in the robot code depend on it
    '''
    global detected_robot

    debug_print("Found {}".format(in_robot))
    if detected_robot != "None":
        detected_robot += "-"
    else:
        # get rid of the None as we do have something to add
        detected_robot = ""

    detected_robot += in_robot


def autodetect():
    '''
    Returns a string
    Possible strings are:
    GoPiGo
    GoPiGo_PivotPi
    GrovePi
    GrovePi_PivotPi
    GrovePi_GoPiGo
    GrovePi_GoPiGo_PivotPi
    PivotPi
    BrickPi
    BrickPi3
    BrickPi3_PivotPi
    '''
    debug_print ("autodetect ")
    global detected_robot
    detected_robot = "None"

# the order in which these are tested is important
# as it will determine the priority in Scratch    
    if find_gopigo3():
        add_robot("GoPiGo3")
    elif find_gopigo():      # if GPG3 wasn't detected, check for GPG.
        add_robot("GoPiGo")
    
    if find_brickpi3():
        add_robot("BrickPi3")

    if find_brickpi():
        add_robot("BrickPi+")
    
    if find_grovepi():
        add_robot("GrovePi")

    if find_pivotpi():
        add_robot("PivotPi")

    return detected_robot


def add_symlink(src):
    if src in detectable_robots: # sanity check
        try:
            if not os.path.islink("/home/pi/Desktop/"+src):
                os.symlink("/home/pi/Dexter/"+src, "/home/pi/Desktop/"+src)
        except:
            pass


def remove_symlink(src):
    try:
        if os.path.islink('/home/pi/Desktop/'+src):
            os.unlink('/home/pi/Desktop/'+src)
    except:
        pass

        
def remove_control_panel(src):
    GoPiGo_3_Src_File = '''/home/pi/Dexter/GoPiGo3/Software/Python/Examples/Control_Panel/gopigo3_control_panel.desktop'''
    GoPiGo_2_Src_File = '''/home/pi/Dexter/GoPiGo/Software/Python/control_panel/gopigo_control_panel.desktop'''
    GoPiGo_3_Dsk_File = '''/home/pi/Desktop/gopigo3_control_panel.desktop'''
    GoPiGo_2_Dsk_File = '''/home/pi/Desktop/gopigo_control_panel.desktop'''

    try:
        os.remove(GoPiGo_3_Dsk_File) # Delete the GoPiGo3 file.
    except OSError as e:
        print("GoPiGo3 File Not Found.")
        print(e)

    try:
        os.remove(GoPiGo_2_Dsk_File)
    except OSError as e:
        print("GoPiGo2 File Not Found.")
        print(e)

    # For the GoPiGo, add the Control Panel Links
    if src == "GoPiGo":
        try:
            copyfile(GoPiGo_2_Src_File, GoPiGo_2_Dsk_File)
        except OSError as e:
            print("No GoPiGo control panel found.")
            print(e)
    if src == "GoPiGo3":
        try:
            copyfile(GoPiGo_3_Src_File, GoPiGo_3_Dsk_File)
        except OSError as e:
            print("Error Adding GoPiGo3 Control Panel Links")
            print(e)
    
##########################################################################
##########################################################################

if __name__ == '__main__':
    detected_robot = autodetect()
    print("Detected robot: %s" % detected_robot)

    try:
        with open("/home/pi/Dexter/detected_robot.txt", 'w+') as outfile:
            outfile.write(detected_robot)
            outfile.write('\n')
    except:
        print("Couldn't write to ~/Dexter/detected_robot.txt")
     
    try:
        remove_control_panel(detected_robot)
    except OSError as e:
        print("Control Panel setup failed. ", e)
        
    # adjust softlinks on desktop
    for detection in detectable_robots:
        if detected_robot.find(detection)==0 or detected_robot.find("None")==0:

            add_symlink(detection)

            # In the case of a GoPiGo3, a false positive can be generated when there's GoPiGo3.
            # The GoPiGo3 can generate symlinks for both the GoPiGo and the GoPiGo3.  So remove 
            # the "GoPiGo" link if the "GoPiGo3" is found.  

            if detection == "GoPiGo":
                if detection.find("3")!=0:
                    remove_symlink(detection)

        else:
            remove_symlink(detection)
