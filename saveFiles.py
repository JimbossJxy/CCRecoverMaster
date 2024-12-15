import variables
import json
import logging
import asyncio
import aiofiles


class SaveFiles:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def loadMasterInfo(self):
        try:
            with open(variables.saveDataPath, "r") as file:
                variables.masterInfo = json.load(file)
            self.logger.info("Master info loaded successfully")
            self.logger.info(variables.masterInfo)
        except FileNotFoundError:
            self.logger.info("Master file not found - creating a new one")
            with open(variables.saveDataPath, "w") as file:
                json.dump(variables.masterInfo, file, indent=4)
            self.logger.info("Master file created successfully")
    
        except Exception as e:
            self.logger.error(f"An error occurred while loading the master info: {e}")
           

    def loadWeeklyInfo(self):
        try:
            with open(variables.weeklyPath, "r") as file:
                variables.weeklyInfo = json.load(file)
            self.logger.info("Weekly info loaded successfully")
            self.logger.info(variables.weeklyInfo)

        except FileNotFoundError:
            self.logger.info("Weekly file not found - creating a new one")
            with open(variables.weeklyPath, "w") as file:
                json.dump(variables.weeklyInfo, file, indent=4)
            self.logger.info("Weekly file created successfully")
        except Exception as e:
            self.logger.error(f"An error occurred while loading the weekly info: {e}")
            
    def loadNodeInfo(self):
        try:
            with open(variables.nodePath, "r") as file:
                variables.nodes = json.load(file)
            self.logger.info("Node info loaded successfully")
            self.logger.info(variables.nodes)
        except FileNotFoundError:
            self.logger.info("Node file not found - creating a new one")
            with open(variables.nodePath, "w") as file:
                json.dump(variables.nodes, file, indent=4)
            self.logger.info("Node file created successfully")
        except Exception as e:
            self.logger.error(f"An error occurred while loading the node info: {e}")

    # This function is responsible for saving the master info to a file - this will be done periodically around every 60 seconds
    async def saveMasterInfoPeridically(self):
        while True:
            try:
                variables.masterInfo["onlineNodes"] = len(variables.nodes["online"]) # Update the amount of online nodes
                
                jsonData = json.dumps(variables.masterInfo, indent=4)
                async with aiofiles.open(variables.saveDataPath, "w") as file:
                    await file.write(jsonData)
                self.logger.info("Master info saved successfully")
            except Exception as e:
                self.logger.error(f"An error occurred while saving the master info: {e}")
            
            # Node save info
            try:
                jsonData = json.dumps(variables.nodes, indent=4)
                async with aiofiles.open(variables.nodePath, "w") as file:
                    await file.write(jsonData)
                self.logger.info("Node info saved successfully")
            except Exception as e:
                self.logger.error(f"An error occurred while saving the node info: {e}")
                
            await asyncio.sleep(60)

    async def saveAllInfo(self):
        try:
            jsonData = json.dumps(variables.masterInfo, indent=4)
            async with aiofiles.open(variables.saveDataPath, "w") as file:
                await file.write(jsonData)
            self.logger.info("Master info saved successfully")
        except Exception as e:
            self.logger.error(f"An error occurred while saving the master info: {e}")

        try:
            jsonData = json.dumps(variables.weeklyInfo, indent=4)
            async with aiofiles.open(variables.weeklyPath, "w") as file:
                await file.write(jsonData)
            self.logger.info("Weekly info saved successfully")
        except Exception as e:
            self.logger.error(f"An error occurred while saving the weekly info: {e}")

        try:
            jsonData = json.dumps(variables.nodes, indent=4)
            async with aiofiles.open(variables.nodePath, "w") as file:
                await file.write(jsonData)
            self.logger.info("Node info saved successfully")
        except Exception as e:
            self.logger.error(f"An error occurred while saving the node info: {e}")
        
    async def start(self):
        self.logger.info("Starting the master info saving scheduler")
        self.task = asyncio.create_task(self.saveMasterInfoPeridically())
    
    async def stop(self):
        self.logger.info("Stopping the master info saving scheduler")
        # save the info one last time
        await self.saveAllInfo()

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

class client:
    def __init__(self ):
        self.logger = logging.getLogger(__name__)
    
    async def updateOnlineStatus(self, clientId):
        # Find client id in nodes list

        # check if node is in the offline list
        if clientId in variables.nodes["offline"]:
            variables.nodes["offline"].remove(clientId)
            self.logger.info(f"Node {clientId} is now online")
            self.logger.debug(f"Nodes list: {variables.nodes}")
            variables.nodes["online"].append(clientId)
            #update amount of online nodes
            variables.masterInfo["onlineNodes"] += 1
        
        if clientId in variables.nodes["online"]:
            self.logger.info(f"Node {clientId} is already online")
    
        else:
            # Add node to online list
            variables.nodes["online"].append(clientId)
            self.logger.info(f"Node {clientId} is now online")
            #update amount of online nodes
            variables.masterInfo["onlineNodes"] += 1
    
    async def updateOfflineStatus(self, clientId):
        # Find client id in nodes list

        # check if node is in the online list
        if clientId in variables.nodes["online"]:
            variables.nodes["online"].remove(clientId)
            self.logger.info(f"Node {clientId} is now offline")
            self.logger.debug(f"Nodes list: {variables.nodes}")
            variables.nodes["offline"].append(clientId)
            #update amount of online nodes
            variables.masterInfo["onlineNodes"] -= 1
        
        if clientId in variables.nodes["offline"]:
            self.logger.info(f"Node {clientId} is already offline")

        else:
            # Add node to offline list
            variables.nodes["offline"].append(clientId)
            self.logger.info(f"Node {clientId} is now offline")
            #update amount of online nodes
            variables.masterInfo["onlineNodes"] -= 1