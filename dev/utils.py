import json 
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi
from langchain_openai import ChatOpenAI
from openai import OpenAI
import logging

client = None
llm_client = None
langchain_llm_client = None


def validate_data(data, required_fields):
    """
    Validate incoming data to ensure all required fields are present
    """
    errors = []
    for field in required_fields:
        if field not in data:
            errors.append(f"Field '{field}' is required")
    return errors

def jsonify_success_response(data, message="Success", status_code=200, **kwargs):
    """
    Return a JSON response for a successful request
    """ 
    response = {
        "status": "success",
        "message": message,
        "data": data
    }
    response.update(kwargs)
    return json.dumps(response), status_code

def jsonify_error_response(errors, message="An error occurred", status_code=400, **kwargs):
    """
    Return a JSON response for an unsuccessful request
    """
    response = {
        "status": "error",
        "message": message,
        "errors": errors
    }
    response.update(kwargs)
    return json.dumps(response), status_code

def init_database(connection_string, db_name):
    """
    Initialize the database connection
    """
    try:
        global client
        client = MongoClient(connection_string)
        logging.warning(client.name)
        return client
    except ConnectionFailure:
        raise ConnectionFailure("Could not connect to the database")
    
def get_database_client():
    """
    Get the database client
    """
    if not client:
        raise ConnectionFailure("Database client not initialized")
    return client["amazon_product_data"]


def init_llm_client(api_key, base_url=None):
    """
    Initialize the OpenAI client
    """
    try:
        global llm_client
        global langchain_llm_client
        if llm_client is None:
            if base_url:
                llm_client = OpenAI(api_key=api_key, base_url=base_url)
            llm_client = OpenAI(api_key=api_key)
        if langchain_llm_client is None:
            if base_url:
                langchain_llm_client = ChatOpenAI(api_key=api_key, base_url=base_url,
                                                  model="gpt-4o"
                                                )
            langchain_llm_client = ChatOpenAI(api_key=api_key,
                                                model="gpt-4o",
                                                )
        
        return llm_client, langchain_llm_client
    except ConnectionFailure:
        raise ConnectionFailure("Could not connect to the OpenAI API")
    except Exception as e:
        raise ValueError(f"An error occurred: {str(e)}")

def get_llm_client():
    """
    Get the OpenAI client
    """
    if not llm_client:
        raise ValueError("OpenAI client not initialized")
    return llm_client

def init_langchain_client(api_key, base_url=None):
    """
    Initialize the Langchain client
    """
    # try:
    global langchain_llm_client
    if langchain_llm_client is None:
        if base_url:
            langchain_llm_client = ChatOpenAI(api_key=api_key, base_url=base_url)
        langchain_llm_client = ChatOpenAI(api_key=api_key,
                                            model="gpt-4o",
                                            )
    
    return langchain_llm_client
    # except ValueError as e:
    #     raise ValueError(f"An error occurred: {str(e)}")
    
def get_langchain_client():
    """
    Get the Langchain client
    """
    # logging.warning(f"Langchain client: {langchain_llm_client}")
    if langchain_llm_client  is None:
        raise ValueError("Langchain client not initialized")
    return langchain_llm_client

