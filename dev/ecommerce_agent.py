import bs4
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from pymongo import MongoClient
from typing import Any, Dict, List
from langchain.agents import AgentType, initialize_agent, Tool
from .service import (get_categories,
                      get_ecommerce_data,
                      get_ecommerce_data_by_category,
                      vector_search_data, seatch_by_name_regex,
                      add_to_cart,
                      get_cart, remove_from_cart,
                      update_cart, clear_cart,
                      get_cart_total,
                      get_cart_count,
                      purchase_product_service,
                      get_user_purchase_history,
                      )

from langchain.output_parsers import StructuredOutputParser
from .utils import get_langchain_client
from langchain.memory import MongoDBChatMessageHistory
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback
from config.settings import get_config
from langchain_openai import ChatOpenAI
import re
import logging

class EcommerceAgent:
    def __init__(self, mongodb_uri: str, database_name: str):
        self.llm = ChatOpenAI(
            api_key=get_config().OPENAI_API_KEY,
            model="gpt-4o-mini",
            base_url=get_config().OPENAI_API_URL
        )
        # Initialize tools with detailed descriptions
        # Store current user_id
        self.current_user_id = None
        self.output_parser = StructuredOutputParser.from_response_schemas([{
            "name": "action",
            "description": "The action to take (e.g. 'AddToCart', 'GetCart')",
            "type": "string"
        }, {
            "name": "input",
            "description": "The input for the action",
            "type": "string" 
        }])
        self.tools = [
            Tool(
                name="GetCategories",
                func=get_categories,
                description="Get all available product categories in the store"
            ),
            Tool(
                name="SearchProducts",
                func=vector_search_data,
                description="Search for products using vector similarity search. Input should be a detailed product description."
            ),
            Tool(
                name="SearchByName",
                func=seatch_by_name_regex,
                description="Search for products by name using regex matching. Input should be the product name or keywords."
            ),
            Tool(
                name="GetProductsByCategory",
                func=get_ecommerce_data_by_category,
                description="Get all products in a specific category. Input should be the category name."
            ),
            Tool(
                name="AddToCart",
                func=self._handle_add_to_cart_sync,
                description="Add a product to cart. Input format: 'product_id,quantity' or just 'product_id' for quantity=1"
            ),
            Tool(
                name="GetCart",
                func=self._handle_get_cart,
                description="Get the current contents of the shopping cart"
            ),
            Tool(
                name="UpdateCart",
                func=update_cart,
                description="Update the quantity of a product in the cart. Input should be a dictionary with 'product_id' and 'quantity'."
            ),
            Tool(
                name="RemoveFromCart",
                func=remove_from_cart,
                description="Remove a product from the cart. Input should be the product_id."
            ),
            Tool(
                name="GetCartTotal",
                func=get_cart_total,
                description="Get the total price of all items in the cart"
            ),
            Tool(
                name="GetCartCount",
                func=get_cart_count,
                description="Get the total number of items in the cart"
            ),
            Tool(
                name="PurchaseProducts",
                func=self._handle_purchase_async,
                description="Complete the purchase of items in the cart"
            ),
            Tool(
                name="GetPurchaseHistory",
                func=get_user_purchase_history,
                description="Get the user's purchase history"
            )
        ]

                # Enhanced system message for better cart handling
        system_message = """You are an intelligent e-commerce assistant that helps customers with shopping and cart management.
            When handling product queries and cart operations:
            1. If a customer shows interest in a product, confirm their interest before adding to cart
            2. Always confirm quantity before adding items to cart
            3. After any cart operation, summarize the cart status
            4. Handle price discussions in appropriate currency format
            5. Remember to check product availability before cart operations
            6. Maintain context of previous interactions when suggesting products

            For cart operations:
            - Before adding to cart, confirm: product, quantity, and price
            - After cart modifications, always show: updated total, item count
            - If removing items, ask for confirmation
            - For quantity updates, verify the new quantity is valid

            Example conversation flow:
            Customer: "I'm interested in the gaming laptop you mentioned"
            You: "Great choice! The [laptop model] is priced at $999. Would you like me to add it to your cart? Please confirm and specify the quantity."
            Customer: "Yes, add one please"
            [Add to cart operation]
            You: "I've added 1 [laptop model] to your cart. Your cart now contains 1 item(s) with a total of $999. Is there anything else you'd like to know?"

            Remember to maintain a helpful and conversational tone while ensuring accurate cart operations."""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        # Initialize agent with enhanced settings
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=5,  # Increased for complex cart operations
            early_stopping_method="generate",
            handle_parsing_errors=True,
            output_parser=self.output_parser,
        )

        self.mongodb_uri = mongodb_uri
        self.database_name = database_name

    async def _handle_product_search(self, query: str) -> str:
        """Handle product search with enhanced response formatting including product IDs"""
        try:
            results = await vector_search_data(query)
            if not results:
                results = await seatch_by_name_regex(query)
            
            # Enhanced formatting to prominently include product IDs
            formatted_results = []
            for product in results[:3]:  # Limit to top 3 matches
                # Ensure we handle both possible ID field names
                product_id = product.get('_id') or product.get('id')
                if not product_id:
                
                    continue
                    
                formatted_results.append(
                    f"Product ID: {product_id}\n"  # Prominently display ID first
                    f"Name: {product['name']}\n"
                    f"Price: ${product['price']}\n"
                    f"Description: {product['description']}\n"
                    f"Reference: When interested in this product, please use Product ID: {product_id}\n"  # Reminder about ID usage
                )
            
            if not formatted_results:
                return "No products found matching your criteria."
                
            return "Here are the products I found:\n\n" + "\n".join(formatted_results)
        except Exception as e:
            return f"Error searching products: {str(e)}"
    def _handle_add_to_cart_sync(self, input_str: str) -> str:
        """Synchronous wrapper for add to cart"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self._handle_add_to_cart_async(input_str))

    async def _handle_add_to_cart_async(self, input_str: str) -> str:
        """Async handler for add to cart operations"""
        try:
            # Parse input
            parts = input_str.split(',')
            product_id = parts[0].strip()
            quantity = int(parts[1].strip()) if len(parts) > 1 else 1

            if not self.current_user_id:
                return "Error: User not authenticated"

            # Add to cart
            add_to_cart(
                product_id=product_id,
                quantity=quantity,
                user_id=self.current_user_id
            )
            logging.warn(f"Added {quantity} x {product_id} to cart")

            # Get cart status
            total =  get_cart_total(
                self.current_user_id
            )
            
            return f"Added {quantity} x {product_id} to cart. Cart total: ${total:.2f}"

        except Exception as e:
            return f"Cart operation failed: {str(e)}"

    async def _handle_add_to_cart(self, product_id: str, quantity: int, user_id: str) -> str:
        """Handle add to cart operations with proper user_id handling"""
        try:
            if not product_id:
                return "Product ID is required."

            # Validate product exists
            product =  get_ecommerce_data(product_id)
            if not product:
                return f"Product not found with ID: {product_id}. Please check the Product ID and try again."

            # Add to  with user_id
            result = await add_to_cart(product_id, quantity, user_id)
            
            # Get updated cart status
            cart =  get_cart()
            total =  get_cart_total()
            count =  get_cart_count()

            return (f"Added {quantity} x {product['name']} (Product ID: {product_id}) to cart.\n"
                   f"Cart now contains {count} items.\n"
                   f"Total: ${total:.2f}")
        except Exception as e:
            return f"Error adding to cart: {str(e)}"


    def _handle_get_cart(self, _: str = "") -> str:
        """Get cart contents with formatted output including product IDs"""
        try:
            if not self.current_user_id:
                return "Error: User not authenticated"
                
            cart =  get_cart(user_id=self.current_user_id)
            total =  get_cart_total(user_id=self.current_user_id)
            count =  get_cart_count(user_id=self.current_user_id)

            if not cart:
                return "Your cart is empty."

            cart_items = []
            logging.warn(f"Cart contents: {cart}")
            for item in cart["products"]:
                product_id = item.get('product_id')
                cart_items.append(
                    f"- {item['quantity']} x {item['product_name']} "
                    f"(Product ID: {product_id}) "
                    f"(${item['price']} each)"
                )

            return ("\n".join(cart_items) +
                f"\nTotal items: {count}\n"
                f"Total price: ${total:.2f}")
        except Exception as e:
            return f"Error retrieving cart: {str(e)}"
    def get_chat_history(self, session_id: str) -> MongoDBChatMessageHistory:
        """
        Retrieve or create a chat history for the given session ID using MongoDB.
        
        Args:
            session_id (str): The unique identifier for the chat session
            
        Returns:
            MongoDBChatMessageHistory: Chat history instance for the session
        """
        try:
            # Initialize MongoDB chat history
            chat_history = MongoDBChatMessageHistory(
                connection_string=self.mongodb_uri,
                database_name=self.database_name,
                collection_name="chat_histories",
                session_id=session_id
            )
            
            return chat_history
            
        except Exception as e:
            print(f"Error initializing chat history: {str(e)}")
            # Fallback to in-memory chat history if MongoDB fails
            return ChatMessageHistory()
    def _handle_purchase_async(self, input_str: str = "") -> str:
        """Async handler for purchase operations"""
        try:
            if not self.current_user_id:
                return "Error: User not authenticated"
                
            logging.warn(f"Processing purchase for user: {self.current_user_id}")
            
            # Get cart before purchase
            cart = get_cart(user_id=self.current_user_id)
            if not cart:
                return "Cart is empty. Nothing to purchase."
                
            logging.warn(f"Cart contents: {cart}")
            
            result =  purchase_product_service(user_id=self.current_user_id)
            
            logging.warn(f"Purchase result: {result}")
            
            if not result:
                return "Purchase failed: No response from service"
                
            return f"Purchase completed successfully. Order ID: {result.get('order_id', 'N/A')}"
            
        except Exception as e:
            logging.error(f"Purchase error: {str(e)}")
            return f"Purchase failed: {str(e)}"
        
        

    async def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Process user message with enhanced cart operation handling"""
        try:
            # Store the current user_id for use in tool operations
            self.current_user_id = session_id
            
            # Get chat history
            chat_history = self.get_chat_history(session_id)
            
            # Check for cart-related intent
            cart_intent = self._detect_cart_intent(user_message)
            
            # Track token usage
            with get_openai_callback() as cb:
                # Generate response
                response = await self.agent.arun(
                    input=user_message,
                    chat_history=chat_history.messages
                )
                
                # Add messages to history
                chat_history.add_user_message(user_message)
                chat_history.add_ai_message(response)
                
                # If cart operation was performed, get updated cart status
                if cart_intent:
                    cart_status = self._handle_get_cart()
                    response += f"\n\nCart Status:\n{cart_status}"
                
                return {
                    "response": response,
                    "token_usage": {
                        "total_tokens": cb.total_tokens,
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens
                    },
                    "cart_updated": cart_intent
                }
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "error": str(e)
            }
        finally:
            # Clear the current_user_id after processing
            self.current_user_id = None

    def _detect_cart_intent(self, message: str) -> bool:
        """Detect if message contains cart-related intent"""
        cart_keywords = [
            r"add to cart",
            r"buy",
            r"purchase",
            r"get it",
            r"take it",
            r"remove from cart",
            r"update cart",
            r"change quantity",
            r"empty cart",
            r"clear cart"
        ]
        return any(re.search(pattern, message.lower()) for pattern in cart_keywords)



ecommerce_agent = EcommerceAgent(
    get_config().MONGODB_URI, "amazon_product_data")
