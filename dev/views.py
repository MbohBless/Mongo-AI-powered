from flask import request, jsonify
# from  .service import process_data, fetch_data_from_source
from .service import (get_ecommerce_data, get_ecommerce_data_by_label, get_ecommerce_data_by_id, get_ecommerce_data_by_category, get_ecommerce_data_by_tech_data, vector_search_data,
                      get_categories, add_to_cart, get_cart, remove_from_cart, update_cart, clear_cart, get_cart_total, get_cart_count, purchase_product_service, get_user_purchase_history, seatch_by_name_regex)
from .utils import validate_data, jsonify_error_response, jsonify_success_response
import logging
from .ecommerce_agent import ecommerce_agent


def fetch_all_ecommerce_data():
    """
    This function fetches all the data from the source
    """
    try:
        page = request.args.get("page", 0)
        limit = request.args.get("limit", 10)
        data = get_ecommerce_data(page, limit)
        return jsonify_success_response(data)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)

# get categories


def fetch_categories():
    """
    This function fetches all the data from the source
    """
    try:
        data = get_categories()
        return jsonify_success_response(data)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)

# id is passed as parameter


def fetch_ecommerce_data_by_id(productId: str):
    """
    This function fetches data from the source
    """
    try:
        data = get_ecommerce_data_by_id(str(productId))
        return jsonify_success_response(data)
    except Exception as e:
        if str(e) == "Product not found":
            return jsonify_error_response([str(e)], message="Product not found", status_code=404)
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def fetch_ecommerce_data_by_category(category: str):
    """
    This function fetches data from the source
    """
    try:
        page = request.args.get("page", 0)
        limit = request.args.get("limit", 10)
        data = get_ecommerce_data_by_category(category, page, limit)
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def fetch_ecommerce_data_by_label(label: str):
    """
    This function fetches data from the source
    """
    try:
        page = request.args.get("page", 0)
        limit = request.args.get("limit", 10)
        data = get_ecommerce_data_by_label(label, page, limit)
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def fetch_ecommerce_data_by_tech_data(tech_data: str):
    """
    This function fetches data from the source
    """
    try:
        page = request.args.get("page", 0)
        limit = request.args.get("limit", 10)
        data = get_ecommerce_data_by_tech_data(tech_data, page, limit)
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def search_ecommerce_data():
    """
    This function searches for data from the source
    """
    try:
        page = request.args.get("page", 0)
        limit = request.args.get("limit", 10)
        # get body data
        query = request.json.get("query")
        logging.warning(query)
        data = vector_search_data(query, page, limit)
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def fetch_data_by_name():
    """
    This function fetches data from the source
    """
    try:
        product_name = request.args.get("product_name")
        data = seatch_by_name_regex(product_name)
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def add_to_cart_view():
    """
    This function adds a product to the cart
    """
    try:
        data = request.json
        validate_data(data, ["product_id", "quantity", "user_id"])
        # process the data
        data = add_to_cart(
            data["product_id"], data["quantity"], data["user_id"]
        )
        return jsonify_success_response(data)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def get_cart_view():
    """
    This function fetches the cart for a user
    """
    try:
        user_id = request.args.get("user_id")
        data = get_cart(user_id)
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def remove_from_cart_view():
    """
    This function removes a product from the cart
    """
    try:
        data = request.json
        validate_data(data, ["product_id", "user_id"])
        # process the data
        data = remove_from_cart(
            data["product_id"], data["user_id"]
        )
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def update_cart_view():
    """
    This function updates the cart for a user
    """
    try:
        data = request.json
        validate_data(data, ["product_id", "quantity", "user_id"])
        # process the data
        data = update_cart(
            data["product_id"], data["quantity"], data["user_id"]
        )
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def clear_cart_view():
    """
    This function clears the cart for a user
    """
    try:
        user_id = request.args.get("user_id")
        data = clear_cart(user_id)
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def get_cart_total_view():
    """
    This function fetches the total for a user's cart
    """
    try:
        user_id = request.args.get("user_id")
        data = get_cart_total(user_id)
        return jsonify_success_response(data)
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def get_cart_count_view():
    """
    This function fetches the count for a user's cart
    """
    try:
        user_id = request.args.get("user_id")
        data = get_cart_count(user_id)
        return jsonify_success_response({"count": data
                                         })
    except Exception as e:
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def purchase_product_view():
    """
    This function fetches the cart for a user
    """
    try:
        user_id = request.args.get("user_id")
        data = purchase_product_service(user_id)
        return jsonify_success_response(data)
    except Exception as e:
        # logging.error(f"An error occurred: {str(e)}")
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)


def get_user_purchase_history_view():
    """
    This function fetches the purchase history for a user
    """
    try:
        user_id = request.args.get("user_id")
        data = get_user_purchase_history(user_id)
        return jsonify_success_response(data)
    except Exception as e:
        # logging.error(f"An error occurred: {str(e)}")
        return jsonify_error_response([str(e)], message="An error occurred", status_code=400)
async def chat_with_agent():
    """
    Handles AI agent chat interactions 
    """
    try:
        user_id = request.args.get("user_id", "default_user")
        user_message = request.json.get("message")
        
        if not user_message:
            return jsonify_error_response(
                ["Message is required"], 
                message="Message required", 
                status_code=400
            )
            
        # Change from direct call to using process_message method
        response = await ecommerce_agent.process_message(
            session_id=user_id,
            user_message=user_message
        )
        # print(type(response))
        logging.info(f"Chat agent response: {response}")
        logging.warn(type(response))
        return jsonify_success_response(response)
        
    except Exception as e:
        logging.error(f"Chat agent error: {str(e)}")
        return jsonify_error_response(
            [str(e)], 
            message="Failed to process message", 
            status_code=500
        )