#!/usr/bin/env python3
# https://www.youtube.com/watch?v=iWS9ogMPOI0&ab_channel=pixegami

"""
    TODO:
    -  Make a dashboard when accessing /dashboard/ that will show the following: ( not a priority, may be done later)
        - Master node information
        - Weekly information
        - Node information
        - Passwords checked
        - Passwords generated
        - Passwords sent
        - Passwords checked per week
        - Passwords generated per week
        - Passwords sent per week
        - Passwords checked per month
        - Passwords generated per month
        - Passwords sent per month
        - It checks to see if it has standard browser headers and if it does it will return the dashboard if not it wont return the dashboard it will just 404
    
    - node counts
    
   


    FINISHED:
    - Save data works
    - Add queue management for the password lists - very quick and efficient :)
    - Add Online/Offline node recording functionality - p1
    - the restart functionality for the master will be once a month on the first of the month
    - the restart functionality for the node will be once a week on no set day, just a week after start up
    - Add server restarting functionality to make sure the node runs as best as possible
    - Add return json checking functionality - may involve adding a password checking queue to prevent overloading the system
"""


from fastapi import FastAPI, HTTPException, Request, responses
from uvicorn import Server, Config
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import aiofiles
import sys


import json

from pathlib import Path
import logging

import uvicorn.server

# Other imports
import variables
import emails
import masterLogger
import saveFiles
import charGen
import serverRestart





# Setting up the SSL context
#sslContext = ssl.create_default_context(ssl.PROTOCOL_TLS_SERVER)
#sslContext.load_cert_chain(certfile=variables.settings["settings"]["sslcrt"], keyfile=variables.settings["settings"]["sslkey"])

# initializing the logger
masterLogger.masterLogging()
logger = logging.getLogger(__name__)

# Initializing instances
emailScheduler = None
save = None
passwordCheckQueue = None
isProcessing = False
restartManager = None


# Initializing Queues
# Initializing the password check queue

queueLock = asyncio.Lock()

# Initializing email 
email = emails.Email(variables.settings["settings"]["masterEmail"], variables.settings["settings"]["credentialsLocation"])
save = saveFiles.SaveFiles()
passwordCheckQueue= charGen.intake(emailInstance=email)
passwordGen = charGen.characterGen(emailInstance=email)
clientStatus = saveFiles.client()



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Annoucing global variables
    global emailScheduler
    global save
    global passwordCheckQueue
    global isProcessing



    isProcessing = False


    # This is the startup
 
    logger.info("Starting up")
    logger.info("Loading master info")

    # Loading master info
    save.loadMasterInfo()
    logger.info(f"Master info loaded successfully- {variables.masterInfo} ")

    # Loading weekly info
    save.loadWeeklyInfo()
    logger.info(f"Weekly info loaded successfully- {variables.weeklyInfo} ")

    # Loading node info
    save.loadNodeInfo()
    logger.info(f"Node info loaded successfully- {variables.nodes} ")

    # Send Online Email
    await email.onlineEmail()
    # Starting periodic saving of master info
    await save.start()

    # Start the queue processing
    await passwordGen.start()
    
    # Sleep for 5 seconds to make sure all save data is loaded
    await asyncio.sleep(5)
    # Start the email scheduler
    emailScheduler = emails.EmailScheduler(emailInstance=email)
    await emailScheduler.start()

    # starting checking queue
    await passwordCheckQueue.start()

    # Start the server restart manager
    
    
    # Make sure all the required paths are created
    
    try:
        yield
    finally:
        # This is the shutdown
        logger.info("Shutting down")

        # Stop the password check queue

        if passwordCheckQueue:
            await passwordCheckQueue.stop()
        
        if passwordGen:
            await passwordGen.stop()

        # send offline email
        

        # Stop the email scheduler
        if emailScheduler:
            await emailScheduler.stop()
        
        # Stop the master info saver
        if save:
            await save.stop()

        
        await email.offlineEmail()

        # Stop the server restart manager
        

        


        
        

# Initializing the FastAPI app
app = FastAPI(lifespan=lifespan)

# Checks if the server is shutting down if it is all passwords get processed and then the server shuts down
@app.middleware("http")
async def checkServerAvailability(request: Request, call_next):
    if isProcessing:
        return responses.JSONResponse(status_code=503, detail="Server is currently processing and unavailable for requests.")

    return await call_next(request)

# Get Endpoints
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/password-check-list/")
async def get_password_check_list():
    if variables.found:
        return {"found": True}
    async with queueLock:
        files = sorted(variables.queuePath.glob("*.json"), key=lambda f: int(f.stem))
        if not files:
            raise HTTPException(status_code=404, detail="No password lists available")
        
        filePath = files[0]
        try:
            logger.info(f"Reading file {filePath}")
            async with aiofiles.open(filePath, "r") as f:
                fileConent = await f.read()
                data = json.loads(fileConent)
            await asyncio.to_thread(filePath.unlink)
            logger.info(f"File {filePath} deleted")
            return data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while reading the file: {e} - line: {sys.exc_info()[-1].tb_lineno}")
        
@app.get("/alldata/")
async def get_all_data():
    return {"masterInfo": variables.masterInfo, "weeklyInfo": variables.weeklyInfo, "nodes": variables.nodes, "queueSize": passwordCheckQueue.queue.qsize()}
    

# Post Endpoints
@app.post("/online/")
async def online(request: Request):
    # This will add the node to the online list
    try:
        data = await request.json()
        #data= json.loads(data)
        logger.info(f"Data received: {data}")
        # get the node id

        nodeId = data["packet"]["node_id"]
        await clientStatus.updateOnlineStatus(clientId=nodeId)
        print (f"Node ID: {nodeId}")
        print (variables.nodes)
        

    
    except Exception as e:
        logger.error(f"An error occurred while parsing the request: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while parsing the request: {str(e)}")

    

@app.post("/offline/")
async def offline(request: Request):
    try:
        data = await request.json()
        logger.info(f"Data received: {data}")

        # get the node id
        nodeId = data["packet"]["node_id"]
        await clientStatus.updateOfflineStatus(clientId=nodeId)


    
    except Exception as e:
        logger.error(f"An error occurred while parsing the request: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while parsing the request: {str(e)}")


@app.post("/password-return/")
async def password_return(request: Request):
    # This will return the password to the master node
    data = await request.json()
    QUEUE_MAX_SIZE = 1000  # Example limit
    if passwordCheckQueue.queue.qsize() >= QUEUE_MAX_SIZE:
        raise HTTPException(
            status_code=503, 
            detail="Queue is full. Try again later."
    )

    try:
        await passwordCheckQueue.addToQueue(data)
        logger.info(f"Current queue size: {passwordCheckQueue.queue.qsize()}")
        return {"message": "Password added to queue"}, 200
    except Exception as e:
        logger.error(f"An error occurred while processing the request: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the request: {e}")
    
    

@app.post("/found-password/")
async def found_password(request: Request):
    data = await request.json()
    try:
        if "password" not in data:
            raise HTTPException(status_code=400, detail="No password found in the request")
        
        password = data["password"]
        await email.foundEmail(password=password)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the request: {e}") 

@app.post("/shutdown/") # This will shut down the server but it wont work as i have not implemented the server restart manager
async def shutdown():
    try:
        variables.stop = True
        return {"message": "Server shutting down"}, 200
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while shutting down the server: {e}")
    

# dashboard
@app.get("/dashboard/")
async def dashboard():
    # This will return the dashboard
    return {"message": "Dashboard"}

@app.post("/dashboard/sendlogInfo/")
async def sendInfo(request: Request):
    data = await request.json()
    print(data)
    return {"message": "Data received"}




# Get requests are to get data from the server
# Post requests are to send data to the server
if __name__ == "__main__":
    config = Config(
        "main:app",
        host="0.0.0.0",
        port=variables.settings["settings"]["port"],
        #ssl_ca_certs=variables.settings["settings"]['keys']["ca"], # This is the CA certificate - if you're only using a self-signed certificate, you can remove this
        ssl_keyfile=variables.settings["settings"]['keys']["sslkey"],
        ssl_certfile=variables.settings["settings"]['keys']["sslcrt"],
    )
    server = Server(config)

    restartManager = serverRestart.monthlyRestartManager(server)
    loop = asyncio.get_event_loop()
    async def run():
        # Start the restart manager
        await restartManager.start()

        # Run the Uvicorn server
        await server.serve()

        # Stop the restart manager after the server stops
        await restartManager.stop()
        restartManager.computerRestart(isShutdown=variables.serverShutdown)

    try:
        loop.run_until_complete(run())
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(server.shutdown())