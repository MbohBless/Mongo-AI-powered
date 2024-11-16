# from Flask import Blueprint
from flask import Blueprint
from .views import (fetch_all_ecommerce_data, fetch_ecommerce_data_by_id, fetch_ecommerce_data_by_category,
                    fetch_ecommerce_data_by_label, fetch_ecommerce_data_by_tech_data, search_ecommerce_data, 
                    fetch_categories, fetch_data_by_name, add_to_cart_view, get_cart_view, remove_from_cart_view,
                    update_cart_view, clear_cart_view, get_cart_total_view, get_cart_count_view, purchase_product_view,
                    get_user_purchase_history_view,chat_with_agent)
dev_fest_bp = Blueprint("devfest", __name__)

dev_fest_bp.add_url_rule(
    "/products", view_func=fetch_all_ecommerce_data, methods=["GET"])
dev_fest_bp.add_url_rule("/products/<productId>",
                         view_func=fetch_ecommerce_data_by_id, methods=["GET"])
dev_fest_bp.add_url_rule("/products/category/<category>",
                         view_func=fetch_ecommerce_data_by_category, methods=["GET"])
dev_fest_bp.add_url_rule("/products/label/<label>",
                         view_func=fetch_ecommerce_data_by_label, methods=["GET"])
dev_fest_bp.add_url_rule("/products/tech_data/<tech_data>",
                         view_func=fetch_ecommerce_data_by_tech_data, methods=["GET"])
dev_fest_bp.add_url_rule("/products/vector/search",
                         view_func=search_ecommerce_data, methods=["POST"])
dev_fest_bp.add_url_rule("/products/name/search",
                         view_func=fetch_data_by_name, methods=["GET"])
dev_fest_bp.add_url_rule("/products/categories",
                         view_func=fetch_categories, methods=["GET"])

#
dev_fest_bp.add_url_rule(
    "/cart/add", view_func=add_to_cart_view, methods=["POST"])
dev_fest_bp.add_url_rule("/cart/get", view_func=get_cart_view, methods=["GET"])
dev_fest_bp.add_url_rule(
    "/cart/remove", view_func=remove_from_cart_view, methods=["PUT"])
dev_fest_bp.add_url_rule(
    "/cart/update", view_func=update_cart_view, methods=["PUT"])
dev_fest_bp.add_url_rule(
    "/cart/clear", view_func=clear_cart_view, methods=["DELETE"])
dev_fest_bp.add_url_rule(
    "/cart/total", view_func=get_cart_total_view, methods=["GET"])
dev_fest_bp.add_url_rule(
    "/cart/count", view_func=get_cart_count_view, methods=["GET"])
dev_fest_bp.add_url_rule(
    "/cart/purchase", view_func=purchase_product_view, methods=["POST"])
dev_fest_bp.add_url_rule(
    "/cart/history", view_func=get_user_purchase_history_view, methods=["GET"])


dev_fest_bp.add_url_rule("/agent/conversation",view_func=chat_with_agent, methods=["POST"])