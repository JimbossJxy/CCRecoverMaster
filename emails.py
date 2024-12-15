"""
    Created on Nov 9 19:22:00 2024
    File name: email.py
    Description:
        This file is responsible for sending emails to the user.
        This file will be responsible for the following:
            - Sending emails to the user
"""

# Importing the necessary libraries
import logging
import time
import Layouts
import variables
import yagmail
import asyncio
import json
import sys
from datetime import datetime

class Email:
    def __init__(self, email, credentials):
        self.email = email
        self.credentials = credentials
        self.yag = yagmail.SMTP(self.email, oauth2_file=self.credentials)
        self.logger = logging.getLogger(__name__)

    async def sendEmail(self, subject, contents, isPassword=False):
        try:
            if isPassword:
                await asyncio.to_thread(self.yag.send,
                    to="email@address",# update to your own email - this can be a list of emails, I have it set to a single email if you might only want one person to receive the email if there is a password found
                    subject=subject,
                    contents=contents
                )
                print(f"{subject} Email sent successfully")
                self.logger.info(f"{subject} Email sent successfully")
            else:
                await asyncio.to_thread(self.yag.send,
                    to=variables.settings["settings"]["reciepientEmails"],
                    subject=subject,
                    contents=contents
                )
                print(f"{subject} Email sent successfully")
                self.logger.info(f"{subject} Email sent successfully")
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            

    async def onlineEmail(self):
        _layout = Layouts.Layouts().onlineLayout()
        self.logger.info("Sending online email")
        await self.sendEmail( subject="BIP 38 Cracker - Online", contents=_layout, isPassword=False)
    
    async def offlineEmail(self):
        _layout = Layouts.Layouts().offlineLayout()
        self.logger.info("Sending offline email")
        await self.sendEmail( "BIP 38 Cracker - Offline", _layout)
    
    async def weeklyEmail(self):
        try:
            self.logger.info("Creating weekly email")
            self.logger.info(f"weeklyLastTimeChecked: {variables.weeklyInfo['weeklyLastTimeChecked']}")
            week1 = datetime.fromtimestamp(variables.weeklyInfo["weeklyLastTimeChecked"]).strftime('%Y-%m-%d %H:%M:%S ')
            _layout = Layouts.Layouts().weeklyLayout(
                        week1=week1,
                        week2=time.strftime('%Y-%m-%d %H:%M:%S'),
                        internalAmount=variables.masterInfo["onlineNodes"], 
                        checkedAmount=(int(variables.masterInfo["amountOfPasswordsChecked"]) -int(variables.weeklyInfo["weeklyAmountOfPasswordsChecked"])), 
                        firstCheckPass=variables.weeklyInfo["weeklyLastCheckedPassword"], 
                        secondCheckedPass=variables.masterInfo["lastCheckedPassword"],
                        firstGenPass=variables.weeklyInfo["weeklyLastGeneratedPassword"],
                        secondGenPass=variables.masterInfo["lastGeneratedPassword"]
                        )
            self.logger.info("Sending weekly email")
            
            await self.sendEmail("BIP 38 Cracker - Weekly Update", _layout)
            self.logger.info("Weekly email sent successfully")
        except Exception as e:
            self.logger.error(f"An error occurred while sending the weekly email: {e}, line: {sys.exc_info()[-1].tb_lineno}")
    
    async def foundEmail(self, password="password" ,privatekey = "private"):
        _layout = Layouts.Layouts().foundLayout(password=password, privatekey=privatekey)
        self.logger.info(f"Sending password found email - password: {password}")
        await self.sendEmail( "BIP 38 Cracker - Password Found", _layout)

        
        
class EmailScheduler:
    def __init__(self, emailInstance):
        self.emailInstance = emailInstance
        self.logger = logging.getLogger(__name__)
        self.task = None

    
    async def checkAndSendWeeklyEmail(self):
        while True:
            try:
                currentTime = time.time()
                self.logger.info(f"Checking if it is time to send the weekly email - currentTime: {currentTime} - weeklyLastTimeChecked: {variables.weeklyInfo['weeklyLastTimeChecked']}")
                timeDifference = int(currentTime) - int(variables.weeklyInfo["weeklyLastTimeChecked"])
                if timeDifference >= 604800:
                    await self.emailInstance.weeklyEmail()
                    variables.weeklyInfo["weeklyLastTimeChecked"] = currentTime
                    variables.weeklyInfo["weeklyLastCheckedPasswordTime"] = variables.masterInfo["lastCheckedPasswordTime"]
                    variables.weeklyInfo["weeklyLastCheckedPassword"] = variables.masterInfo["lastCheckedPassword"]
                    variables.weeklyInfo["weeklyLastSentPassword"] = variables.masterInfo["lastSentPassword"]
                    variables.weeklyInfo["weeklyLastGeneratedPassword"] = variables.masterInfo["lastGeneratedPassword"]
                    
                    variables.weeklyInfo["weeklyAmountOfPasswordsChecked"] = variables.masterInfo["amountOfPasswordsChecked"]

                    # Save the weekly info to json file
                    self.logger.debug(f"Saving weekly info to file - weeklyInfo: {variables.weeklyInfo}")
                    with open(variables.weeklyPath, "w") as file:
                        json.dump(variables.weeklyInfo, file, indent=4)

                    self.logger.info("Weekly email sent successfully")
            
            except Exception as e:
                self.logger.error(f"An error occurred while sending the weekly email: {e}, line: {sys.exc_info()[-1].tb_lineno}")
            await asyncio.sleep(60)

    async def start(self):
        self.logger.info("Starting the weekly email scheduler")
        self.task = asyncio.create_task(self.checkAndSendWeeklyEmail())

    async def stop(self):
        self.logger.info("Stopping the weekly email scheduler")
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass


def main():
    # testing weekly email shuduler
    email = Email(variables.settings["settings"]["masterEmail"], variables.settings["settings"]["credentialsLocation"])
    scheduler = EmailScheduler(email)
    asyncio.run(scheduler.start())
    time.sleep(10)
    asyncio.run(scheduler.stop())

if __name__ == "__main__":
    main()