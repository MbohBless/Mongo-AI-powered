import aiohttp
import chainlit as cl
from typing import Dict
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def fetch_from_backend(message: str, user_id: str = "demo_user") -> Dict:
    async with aiohttp.ClientSession() as session:
        url = "http://localhost:5000/api/devfest/agent/conversation"
        params = {"user_id": user_id}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {"message": message}

        try:
            async with session.post(
                url, 
                params=params, 
                json=payload,
                headers=headers
            ) as response:
                logger.error(f"Response headers: {response.headers}")
                logger.error(f"Response status: {response.status}")
                
                if response.content_type == 'text/html':
                    text_response = await response.text()
                    text_response = text_response.replace("```", "")
                    logger.error(f"Raw response: {text_response}")
                    # parse the response as JSON
                    try:
                        response_data = json.loads(text_response)
                    except json.JSONDecodeError:
                        return {
                            "status": "error",
                            "message": "Invalid response format from server"
                        }
                else:
                    response_data = await response.json()
                    logger.debug(f"Backend response: {response_data}")
                return response_data
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            return {
                "status": "error",
                "message": f"Request failed: {str(e)}"
            }
@cl.on_message
async def main(message: cl.Message):
    try:
        # Log incoming message
        logger.error(f"Received message: {message.content}")
        
        # Get response from backend
        response = await fetch_from_backend(message.content)
        logger.error(f"Processing response: {response}")
        
        # Handle response
        if response.get("status") == "success":
            content = response.get("data", {}).get("response", "No response content")
        else:
            content = f"Error: {response.get('message', 'Unknown error')}"
        
        # Send response back to user
        msg = cl.Message(content=content)
        await msg.send()
        logger.warn(f"Sent message: {content}")
        
    except Exception as e:
        logger.error(f"Error in message handling: {str(e)}")
        error_msg = cl.Message(content=f"An error occurred: {str(e)}")
        await error_msg.send()

# @cl.on_message
# async def on_message(msg: cl.Message):
#     try:
#         # Log incoming message
#         logger.error(f"Received message: {msg.content}")
        
#         # Check client type
#         if cl.context.session.client_type == "copilot":
#             fn = cl.CopilotFunction(name="test", args={"msg": msg.content})
#             res = await fn.acall()
#             await cl.Message(content=res).send()
#         else:
#             # Get response from backend
#             response = await fetch_from_backend(msg.content)
#             logger.error(f"Processing response: {response}")
            
#             # Handle response
#             if response.get("status") == "success":
#                 content = response.get("data", {}).get("response", "No response content")
#             else:
#                 content = f"Error: {response.get('message', 'Unknown error')}"
            
#             # Send response back to user
#             await cl.Message(content=content).send()
#             logger.warn(f"Sent message: {content}")
        
#     except Exception as e:
#         logger.error(f"Error in message handling: {str(e)}")
#         error_msg = cl.Message(content=f"An error occurred: {str(e)}")
#         await error_msg.send()