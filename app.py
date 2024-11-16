from flask import Flask, render_template
from config.settings import get_config
from dev.urls import dev_fest_bp
from dev.utils import init_database, init_llm_client
import logging


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))
    logging.basicConfig(level=app.config["LOG_LEVEL"], format=app.config["LOG_FORMAT"])
    app.logger.setLevel(app.config["LOG_LEVEL"])
    app.register_blueprint(dev_fest_bp, url_prefix="/api/devfest")
    @app.route("/")
    def index():
        return "Welcome to DevFest"
    @app.route("/products")
    def products():
        return render_template("index.html")
    @app.route("/products/<productId>")
    def product(productId):
        return render_template("product.html", productId=productId)
    @app.route("/cart")
    def cart():
        return render_template("cart.html")
    @app.route("/purchase_history")
    def purchase_history():
        return render_template("purchase_history.html")
    
    return app
if __name__ == "__main__":
    app = create_app()
    init_database(app.config["MONGODB_URI"],app.config["MONGODB_DB"])
    # init_langchain_client(app.config["OPENAI_API_KEY"], app.config["OPENAI_API_URL"])
    init_llm_client(app.config["OPENAI_API_KEY"], app.config["OPENAI_API_URL"])
    app.run(host="0.0.0.0", port=5000)   