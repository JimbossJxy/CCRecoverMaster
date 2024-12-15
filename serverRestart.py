# to restart the master node once a month on the first of the month
import asyncio
import datetime
import os
import logging
import variables

class monthlyRestartManager:
    def __init__(self, server):
        self.logger = logging.getLogger(__name__)
        self.server = server
        self.task = None

    async def start(self):
        self.logger.info("Starting the monthly restart manager")
        self.task = asyncio.create_task(self.restartMasterMonthly())
    
    async def stop(self):
        self.logger.info("Stopping the monthly restart manager")
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
    
    async def restartMasterMonthly(self):
        while True:
            # Get the current date
            currentDate = datetime.datetime.now()
            self.logger.info(f"Checking if it is time to restart the master node - currentDate: {currentDate}")
            # Check if it is the second of the month
            if currentDate.day == 2:
                # checks if the time is 00:00
                if currentDate.hour == 0 and currentDate.minute == 0:
                    self.logger.info("It is the second of the month, restarting the master node")
                    await self.server.shutdown()
                    self.logger.info("Master node restarted successfully")
            
            # stop server after 30 seconds if password has been found
            if variables.found:
                self.logger.info("Password has been found, stopping the master node")
                await asyncio.sleep(20) # this allows the node to send the email as well as shut the other nodes down
                await self.server.shutdown()
                self.logger.info("Master node stopped successfully")

                    

            # Sleep for 30 seconds to prevent the loop from running too fast and to prevent a missed restart
            await asyncio.sleep(30)
    
    def computerRestart(self, isShutdown):
        # Uses linux - the server will allow for non sudo users to restart the server
        debug = False # Change to False when in production
        if not debug:
            if isShutdown:
                os.system("shutdown /s /t 1")
            else:
                os.system("shutdown /r /t 1")
        