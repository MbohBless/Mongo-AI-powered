from .utils import get_database_client, get_llm_client
import logging
from bson import ObjectId
from datetime import datetime
from config.settings import get_config
from langchain_openai import OpenAIEmbeddings
def convert_objectid_to_str(data):
    if isinstance(data, list):
        for item in data:
            if '_id' in item and isinstance(item['_id'], ObjectId):
                item['_id'] = str(item['_id'])
    elif isinstance(data, dict):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
    return data



def get_ecommerce_data(page, limit):
    """
    This function fetches data from the source
    """
    db = get_database_client()
    data = db["product_data"].find(
        {},
        {
            "_id": 1,
            "product_name": 1,
            "price": 1,
            "category": 1,
            "labels": 1,
            "tech_data": 1,
            "tech_process": 1,
            "image_url": 1
        }
    ).skip(page * limit).limit(limit)
    data = list(data)
    data = convert_objectid_to_str(data)
    return data

def get_ecommerce_data_by_id(product_id):
    """
    This function fetches data from the source
    """
    db = get_database_client()
    data = db["product_data"].find_one({"_id": ObjectId(product_id)},
                                       {
        "_id": 1,
        "product_name": 1,
        "price": 1,
        "category": 1,
        "labels": 1,
        "tech_data": 1,
        "tech_process": 1,
        "feature_string": 1,
        "image_url": 1
    })
    if not data:
        raise ValueError("Product not found")
    data = convert_objectid_to_str(data)
    return data


def get_ecommerce_data_by_category(category, page, limit):
    """
    This function fetches data from the source
    """
    db = get_database_client()
    data = db["product_data"].find(
        {"category": category},
        {
            "_id": 1,
            "product_name": 1,
            "price": 1,
            "category": 1,
            "labels": 1,
            "tech_data": 1,
            "tech_process": 1,
            "image_url": 1
        }
    ).skip(page * limit).limit(limit)
    data = list(data)
    data = convert_objectid_to_str(data)
    return data


def get_ecommerce_data_by_label(label, page, limit):
    """
    This function fetches data from the source
    where label is in the labels array
    """
    db = get_database_client()
    data = db["product_data"].find(
        {"labels": {
            "$in": [label]
        }},
        {
            "_id": 1,
            "product_name": 1,
            "price": 1,
            "category": 1,
            "labels": 1,
            "tech_data": 1,
            "tech_process": 1,
            "image_url": 1
        }
    ).skip(page * limit).limit(limit)
    data = list(data)
    data = convert_objectid_to_str(data)
    return data


def get_ecommerce_data_by_tech_data(tech_data, page, limit):
    """
    This function fetches data from the source
    where label is in the labels array
    """
    db = get_database_client()
    data = db["product_data"].find(
        {"tech_data": {
            "$in": [tech_data]
        }},
        {
            "_id": 1,
            "product_name": 1,
            "price": 1,
            "category": 1,
            "labels": 1,
            "tech_data": 1,
            "tech_process": 1,
            "image_url": 1
        }
    ).skip(page * limit).limit(limit)
    data = list(data)
    data = convert_objectid_to_str(data)
    return data


def embed_query(query: str):
    try:
        # llm_client = =
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            base_url=get_config().OPENAI_API_URL,
        )
        query_embedding = embeddings.embed_query(query)
        return query_embedding
    except Exception as e:
        logging.error(f"An error occurred during query: {str(e)}")
        raise ValueError("An error occurred during query embedding")

def vector_search_data(query: str):
    try:
        query_vector = embed_query(query)
        db = get_database_client()
        collection = db["product_data"]
        aggragation = [
            {
                "$vectorSearch": {
                    "index": "multi_vector_index",
                    "queryVector": query_vector,
                    "path": "labels_embeddings",
                    "exact": True,
                    "limit": 5
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "asin": 1,
                    "category": 1,
                    "labels": 1,
                    "product_name": 1,
                    "tech_process": 1,
                    "tech_data": 1,
                    "feature_string": 1,
                    "image_url": 1,
                    "score": {
                        "$meta": "vectorSearchScore"
                    }
                }
            }
        ]
        data = collection.aggregate(aggragation)
        data = list(data)
        data = convert_objectid_to_str(data)
        return data
    except Exception as e:
        logging.error(f"An error occurred during vector search: {str(e)}")
        raise ValueError("An error occurred during vector search")
def get_categories():
    """
    This function fetches all the data from the source
    """
    db = get_database_client()
    data = db["product_data"].distinct("category")
    return data

def seatch_by_name_regex(name):
    db = get_database_client()
    data = db["product_data"].find(
        {"product_name": {
            "$regex": name,
            "$options": "i"
        }},
        {
            "_id": 1,
            "product_name": 1,
            "price": 1,
            "category": 1,
            "labels": 1,
            "tech_data": 1,
            "tech_process": 1,
            "image_url": 1
        }
    )
    data = list(data)
    data = convert_objectid_to_str(data)
    return data


def add_to_cart(product_id, quantity, user_id):
    logging.warning(f"Adding product {product_id} to cart for user {user_id}")
    db = get_database_client()
    product = db["product_data"].find_one({"_id": ObjectId(product_id)})
    if not product:
        raise ValueError("Product not found")
    
    cart = db["cart"].find_one({"user_id": user_id})
    if not cart:
        logging.warning("Cart not found")
        cart = {
            "user_id": user_id,
            "products": []
        }
    else:
        cart = convert_objectid_to_str(cart)
        logging.warning(cart)
    
    # Check if the product is already in the cart
    product_found = False
    for cart_product in cart["products"]:
        if cart_product["product_id"] == product_id:
            cart_product["quantity"] += quantity
            product_found = True
            break
    logging.warning(f"Product found: {product_found}")
    
    if not product_found:
        cart["products"].append({
            "product_id": product_id,
            "quantity": quantity
        })
    logging.warning("Testing")
    # Remove the _id field before updating the cart
    if "_id" in cart:
        del cart["_id"]
    logging.warning("HEre")
    db["cart"].update_one({"user_id": user_id}, {"$set": cart}, upsert=True)
    logging.warning("Here")
    return cart

def get_cart(user_id):
    db = get_database_client()
    cart = db["cart"].find_one({"user_id": user_id})
    if not cart:
        return []
    for product in cart["products"]:
        product_data = db["product_data"].find_one(
            {"_id": ObjectId(product["product_id"])},
            {
                "_id": 0,
                "product_name": 1,
                "price": 1,
                "category": 1,
                "labels": 1,
                "tech_data": 1,
                "tech_process": 1,
                "image_url": 1
            }
        )
        product.update(product_data)
    if not cart:
        return []
    list(cart)
    cart = convert_objectid_to_str(cart)
    # logging.warning(cart)
    return cart

def remove_from_cart(product_id, user_id):
    db = get_database_client()
    cart = db["cart"].find_one({"user_id": user_id})
    if not cart:
        raise ValueError("Cart not found")
    products = cart["products"]
    for product in products:
        if product["product_id"] == product_id:
            products.remove(product)
            break
    db["cart"].update_one({"user_id": user_id}, {"$set": {"products": products}})
    return products

def update_cart(product_id, quantity, user_id):
    db = get_database_client()
    cart = db["cart"].find_one({"user_id": user_id})
    if not cart:
        raise ValueError("Cart not found")
    products = cart["products"]
    for product in products:
        if product["product_id"] == product_id:
            product["quantity"] = quantity
            break
    db["cart"].update_one({"user_id": user_id}, {"$set": {"products": products}})
    return products

def clear_cart(user_id):
    db = get_database_client()
    db["cart"].delete_one({"user_id": user_id})
    return True

def get_cart_total(user_id):
    db = get_database_client()
    cart = db["cart"].find_one({"user_id": user_id})
    if not cart:
        return 0
    total = 0
    products = cart["products"]
    for product in products:
        product_data = db["product_data"].find_one({"_id": ObjectId(product["product_id"])})
        total += product_data["price"] * product["quantity"]
    return total

def get_cart_count(user_id):
    db = get_database_client()
    cart = db["cart"].find_one({"user_id": user_id})
    if not cart:
        return 0
    return len(cart["products"])


def purchase_product_service(user_id: str):
    """
    This function fetches the cart for a user and processes the purchase
    """
    try:
        logging.info(f"Starting purchase process for user_id: {user_id}")
        
        data = get_cart_total(user_id)
        # logging.info(f"Cart total for user_id {user_id}: {data}")
        
        db = get_database_client()
        clear = get_cart(user_id)
        # logging.info(f"Cart data for user_id {user_id}: {clear}")
        
        clear['total'] = data
        clear['date'] = datetime.now().isoformat()
        clear['status'] = 'purchased'
        
        db['purchase_history'].insert_one(clear)
        # logging.info(f"Purchase history updated for user_id {user_id}")
        
        clear_cart(user_id)
        # logging.info(f"Cart cleared for user_id {user_id}")
        
        return {"message": "Purchase successful"}
    except Exception as e:
        logging.error(f"An error occurred during purchase for user_id {user_id}: {str(e)}")
        raise
    
def get_user_purchase_history(user_id: str):
    """
    This function fetches the purchase history for a user
    """
    db = get_database_client()
    data = db['purchase_history'].find({"user_id": user_id}).sort("date", -1)
    data = list(data)
    for item in data:
        if 'date' in item:
            item['date'] = item['date'].isoformat()
    # logging.warning(data)
    data = convert_objectid_to_str(data)
    return data