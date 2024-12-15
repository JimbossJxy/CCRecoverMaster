

import emails
import logging
import variables
import json
import asyncio
import time
import aiofiles
import sys





class characterGen:
    def __init__(self, emailInstance):
        
        self.logger = logging.getLogger(__name__)
        self.lock = asyncio.Lock()
        self.queuePath = variables.queuePath
        self.maxQueueSize = variables.settings["settings"]["queueSize"]
        self.emailInstance = emailInstance
    
    def next(self, previous= "a", incrementCounter=1):
        _charset = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-_=+[]{}|;:'\",./<>?\\"""
        _charsetLength = len(_charset)
        _incrementCounter = incrementCounter +1

        indices = [_charset.index(char) for char in previous]

        i = len(indices) - 1
        while i >= 0:
            if indices[i] < _charsetLength - 1:
                indices[i] += 1
                break
            else:
                # reset this character over pass most significant character and adds a new character
                indices[i] = 0
                i -= 1

        # If we carried over the most significant character, add a new character
        if i < 0:
            indices = [0] + indices
        
        next_string = "".join([_charset[i] for i in indices])
        #next_string = next_string.replace("\\\\", "\\") - might be causing issues where it wont go past 2 char long
        return next_string, _incrementCounter

    def genPassList(self, amount, lastChar='a', incrementCounter=1):
        _passList = []
        for _ in range(amount):
            lastChar, incrementCounter =  self.next(lastChar, incrementCounter)
            _passList.append(lastChar)
        return _passList, lastChar, incrementCounter
        
    async def refillQueue(self):
        while True:
            async with self.lock:
                # Check if the queue is full
                currentFiles = sorted(self.queuePath.glob("*.json"), key=lambda f: int(f.stem))
                if len(currentFiles) < self.maxQueueSize: # If the queue is not full
                    

                    data, variables.masterInfo["lastGeneratedPassword"], variables.masterInfo["amountOfPasswordsGenerated"] = self.genPassList(amount=variables.settings["settings"]["amountOfPasswordsPerJsonFile"], lastChar=variables.masterInfo["lastGeneratedPassword"], incrementCounter=variables.masterInfo["amountOfPasswordsGenerated"])
                    fileName = str(int(time.time()*100)) + ".json"
                    filePath = self.queuePath / fileName
                    variables.sendDataPacket["passwords"] = data
                    variables.sendDataPacket["packetInfo"]["lastGeneratedPassword"] = variables.masterInfo["lastGeneratedPassword"]
                    data = variables.sendDataPacket
                    async with aiofiles.open(filePath, "w") as f:
                        await f.write(json.dumps(data, indent=4))
                       

                    

                    self.logger.info(f"Created password list with name of: {fileName} - path: {filePath}")

            await asyncio.sleep(0.1) # Sleep for 0.1 seconds to prevent the loop from running too fast
    
    async def start(self):
        self.logger.info("Starting the character generator")
        self.task = asyncio.create_task(self.refillQueue())

    async def stop(self):
        self.logger.info("Stopping the character generator")
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass


class intake:
    def __init__(self, emailInstance):
        self.logger = logging.getLogger(__name__)
        self.queue = asyncio.Queue()
        self.emailInstance = emailInstance
    
    async def addToQueue(self, data):
        
        nodeId = data["packetInfo"]["node_id"]
        timestamp = time.time()
        uniqueId = f"{nodeId}-{timestamp}"

        await self.queue.put({"name": uniqueId, "data": data})
        self.logger.info(f"Data added to queue: {uniqueId}")
    
    async def processQueue(self):
        while True:
            data = await self.queue.get()
            try:
                await self.processTask(data)

            finally:
                self.queue.task_done()
    
    def compare_strings(self, string1, string2):
        """
        Compares two strings by assigning numerical values to characters based on a custom order.
        Returns the string with the higher total value.
        If both strings have the same value, returns "Equal".
        """
        # Define the character set with assigned values
        char_values = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-_=+[]{}|;:'\",./<>?\\"
        
        # Create a dictionary mapping each character to its value (1-based index)
        char_map = {char: i + 1 for i, char in enumerate(char_values)}
        
        # Function to calculate the total value of a string
        def calculate_value(string):
            return sum(char_map.get(char, 0) for char in string)  # Default to 0 if char is not in the map

        # Calculate values for both strings
        value1 = calculate_value(string1)
        value2 = calculate_value(string2)

        # Compare values and return the string with the higher value
        if value1 > value2:
            return string1
        elif value2 >= value1:
            return string2
        

    # Example usage
    string1 = "Hello!"
    string2 = "World123"
    result = compare_strings(string1, string2)
    print(f"The string with the higher value is: {result}")

    async def processTask(self, task):
        self.logger.info(f"Processing task: {task['name']}")

        packetData = task["data"]
        print(packetData)

        try:
            packetInfo = packetData["packetInfo"]
            packetContent = packetData["packetData"]

            if packetInfo["successful"] == "True":
                self.logger.info(f"Data from {packetInfo['node_id']} was sucessful")

                privatekey = packetContent["data"]["password"]
                
                password = packetContent["info"]["lastCheckedPassword"]
                print(password)
                self.logger.info(f"Found Password key: {password}")
                await self.emailInstance.foundEmail(password, privatekey)
                variables.found = True
                variables.serverShutdown = True
                return True
            
            else:
                checkAmount = packetContent["info"]["checkAmount"]
                lastCheckedPassword = packetContent["info"]["lastCheckedPassword"]

                variables.masterInfo["amountOfPasswordsChecked"] += checkAmount
                # check if the password is higher than the last checked password
                variables.masterInfo["lastCheckedPassword"] = self.compare_strings(variables.masterInfo["lastCheckedPassword"], lastCheckedPassword)
                self.logger.info(f"Checked {checkAmount} passwords")

        
        except KeyError as e:
            self.logger.error(f"A key error occurred while processing the task: {e} line {sys.exc_info()[-1].tb_lineno}")
            
            
        except Exception as e:
            self.logger.error(f"An error occurred while processing the task: {e}, line {sys.exc_info()[-1].tb_lineno}")
            

    async def drainQueue(self):
        self.logger.info("Draining the queue...")
        while not self.queue.empty():
            data = await self.queue.get()
            try:
                await self.processTask(data)
            finally:
                self.queue.task_done()
        self.logger.info("Queue drained successfully.")

    
    async def start(self):
        self.logger.info("Starting the intake")
        self.task = asyncio.create_task(self.processQueue())
    
    async def stop(self):
        self.logger.info("Stopping the intake")
        self.logger.info("Draining the queue...")
        await self.drainQueue()
        self.logger.info("Queue drained successfully.")
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    
    async def main():
        emailInstance = emails.Email(variables.settings["settings"]["masterEmail"], variables.settings["settings"]["credentialsLocation"])
        charGenInstance = characterGen(emailInstance)
        await charGenInstance.start()

        try:
            # Keep the script running
            while True:
                
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await charGenInstance.stop()

    asyncio.run(main())
