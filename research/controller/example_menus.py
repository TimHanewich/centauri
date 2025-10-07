import rich.live
import rich.table
import rich.text
import rich.align
import keyboard
import time
import platform
import sys
import os

def flush_input() -> None:
    if platform.system() == "Windows":
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

def cls() -> None:
    if os.name == "nt": # windows NT, like windows 10 or windows 11, the modern windows
        os.system("cls")
    else: # if on linux, just run clear
        os.system("clear")


with rich.live.Live(refresh_per_second=60, screen=True) as l:
    while True:

        if keyboard.is_pressed("m"):
            tbl = rich.table.Table()
            tbl.add_column("Sample Info")
            tbl.add_column("Sample Data")
            tbl.add_row("Battery", "16.8")
            l.update(tbl)
        elif keyboard.is_pressed("s"):

            
            
            l.stop() # stop live view

            

            # wait until s is depressed
            cls()
            print("Stop pressing S to enter settings.")
            while keyboard.is_pressed("s"):
                time.sleep(0.1)
            cls()

            flush_input()

            print("----- SETTINGS -----")
            print("What do you want to do?")
            print("1 - Update PID settings.")
            print("2 - Do something else")
            WTD = input("What do you want to do? ")
            if WTD == "1":
                kp = input("P gain: ")
                ki = input("I gain: ")
                kd = input("D gain: ")
                print("Got it! " + str(kp) + ", " + str(ki) + ", " + str(kd))
                input("Enter to continue.")
            elif WTD == "2":
                print("Ok doing something else.")
                input("Enter to return")
            else:
                print("Huh?")
                input("Enter to continue.")
            
            # restart
            l.start()

        else:
            txt = rich.text.Text("Press 'm' for main, 's' for settings.")
            centered = rich.align.Align.center(txt)
            l.update(centered)