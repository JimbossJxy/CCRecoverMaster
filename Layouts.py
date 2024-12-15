"""
    Created at 10/11/2024 13:47:00
    File name: layouts.py
    Description:
        This file is responsible for creating the layouts for the emails.
        This file will be responsible for the following:
            - Creating the layouts for the emails.
"""
# Feel free to change the layout of the emails to your liking by changing the HTML code in the functions below.

import datetime
import pytz

class Layouts:
    def __init__(self):
        pass

    def onlineLayout(self):
        _time = datetime.datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S %Z%z')
        _layout = """
        <!DOCTYPE html>
        <html lang="en">
        <html>
            <body style="margin: 0;padding: 0;background-color: #ffffff;">
                <h1 style="font-family: Arial, Helvetica, sans-serif;color: #ffffff;font-size: 2.28rem;margin-top: 0;padding: 5% 43.3%;background-color: #1098f7;max-width: fit-content;">BIP 38 Cracker</h1>
                <p id="t1" style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 5% auto;">The BIP 38 Password cracker is now online at """+_time+"""</p>
            </body>
        </html>
        """
        return _layout
    
    def offlineLayout(self):
        _time = datetime.datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S %Z%z')
        _layout = """
        <!DOCTYPE html>
        <html lang="en">
        <html>
            <body style="margin: 0;padding: 0;background-color: #ffffff;">
                <h1 style="font-family: Arial, Helvetica, sans-serif;color: #ffffff;font-size: 2.28rem;margin-top: 0;padding: 5% 43.3%;background-color: #1098f7;max-width: fit-content;">BIP 38 Cracker</h1>
                <p id="t1" style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 5% auto;">The BIP 38 Password cracker is now offline at """+_time+"""</p>
            </body>
        </html>
        """
        return _layout
    
    def weeklyLayout(self, week1, week2, onlineAmount,  checkedAmount, firstCheckPass, secondCheckedPass, firstGenPass, secondGenPass):
        _week1 = week1
        _week2 = week2
        _onlineAmount = str(onlineAmount) # Placeholder - This will be the amount of internal nodes that are currently running
    
        _checkedAmount = str(checkedAmount) # Placeholder - This will be the amount of passwords that have been checked
        _firstCheckPass = firstCheckPass
        _secondCheckedPass = secondCheckedPass
        _firstGenPass = firstGenPass
        _secondGenPass = secondGenPass

        _checkedPerSecond = str(round((float(checkedAmount)/(float(604800))), 2)) # Placeholder - This will be the amount of passwords that have been checked per second
        
        _time = datetime.datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S %Z%z')
        _layout = """
            <!DOCTYPE html>
            <html lang="en">
            <html>
                <body style="margin: 0;padding: 0;background-color: #ffffff;">
                    <h1 style="font-family: Arial, Helvetica, sans-serif;color: #ffffff;font-size: 2.28rem;margin-top: 0;padding: 5% 43.3%;background-color: #1098f7;max-width: fit-content;">BIP 38 Cracker</h1>
                    <h2 style="font-size:1.9rem;font-weight: 500;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 2.5% auto;">BIP38 Cracker Weekly update """+_week1+""" to """+_week2+"""</h2>
                    <p style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 2.5% auto;">Number of internal nodes: """+_onlineAmount+"""</p>
                    <p style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 2.5% auto;">Number of passwords checked: """+_checkedAmount+"""</p>
                    <p style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 2.5% auto;">Number of passwords checked per second: """+_checkedPerSecond+"""</p>
                    <p style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 2.5% auto;">Checked from """+_firstCheckPass+""" to """+_secondCheckedPass+"""</p>
                    <p style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 2.5% auto;">Generated from """+_firstGenPass+""" to """+_secondGenPass+"""</p>
                    <p style="font-size: 0.8rem; font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 5% auto;">Sent at """+_time+"""</p>
                </body>
            </html>
        """ 
        return _layout

    def foundLayout(self, password, privatekey):
        _time = datetime.datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S %Z%z')
        _layout = """
        <!DOCTYPE html>
        <html lang="en">
        <html>
            <body style="margin: 0;padding: 0;background-color: #ffffff;">
                <h1 style="font-family: Arial, Helvetica, sans-serif;color: #ffffff;font-size: 2.28rem;margin-top: 0;padding: 5% 43.3%;background-color: #1098f7;max-width: fit-content;">BIP 38 Cracker</h1>
                <p id="t1" style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 5% auto;">The BIP 38 Password cracker has found the password: """+password+"""</p>
                <p id="t1" style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 5% auto;">The BIP 38 Password cracker has found the private key: """+privatekey+"""</p>
                <p id="t1" style="font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 5% auto;">Terminating Program as of now</p>
                <p style="font-size: 0.8rem; font-weight: 400;font-family: Arial, Helvetica, sans-serif;max-width: fit-content;margin: 5% auto;">Sent at """+_time+"""</p>
            </body>
        </html>
        """
        return _layout