## GDG Presentation for *MongoDB for AI powered CLient applications* November 16, 2024
### By: [Mboh Bless Pearl N](https://www.linkedin.com/in/mbohbless/)
#### [GDG Kigali and MongoDB User Group](https://www.mongodb.com/community/forums/t/responsible-ai-kigali-mug-meetup-at-devfest-kigali-2024/300904)

### Introduction 
The project shows how we can switch from a baic or regular pattern for performing a purchase for a product. The web application is built with a simple front-end and a back-end that is powered by MongoDB. The application is built with the following technologies:
- HTML
- CSS
- JavaScript
- Python[Flask]

for the application the html pages are served by the flask server and the data is stored in mongodb. For the API endpoints, the they are prefixed with `/api/devfest/` and the following endpoints are available:
- `/api/devfest/products` - This endpoint returns all the products in the database
- `/api/devfest/products/<product_id>` - This endpoint returns a single product with the specified product_id
- `/api/devfest/products/category/<category>` - This endpoint returns all the products in the specified category
- `/api/devfest/products/label/<label>` - This endpoint returns all the products with the specified label
- `/api/devfest/products/tech_data/<tech_data>` - This endpoint returns all the products with the specified tech_data
and many more in this file:
- [utls.py](dev/urls.py)

Theapplication later deviats from the basic approach of performing operations on the client site. WIth this now, a conversational customer support agent is then built where the user chat's with a bot to perform the purchase. The bot is built with the following technologies:
- Python
- Flask
- MongoDB
- Chainlit
<!--  -->
for the mean time, the application is confident for the getting ot products based on the user product request, adding a specified item to the user's cart, fetching the user's cart and then performing a purchase for the user. 
### Installation
To experiment with this application as follows:
1. Clone the repository
```bash
git clone https://github.com/MbohBless/Mongo-AI-powered.git
```
2. Change into the directory
```bash
cd Mongo-AI-powered
```
3. Install the dependencies
```bash
pip install -r requirements.txt
```
<!- -->
<!-- for the env there are  -->
4. Create a `.env` file in the root directory and add the following:
```env
MONGODB_URI= # your mongodb uri
MONGODB_DB= # your mongodb database
OPENAI_API_KEY= # your openai api key
OPENAI_API_URL= # your openai api url (remove if you are directly using openai)
```
5. For the data I used, if interested you can reach out to me for the data through my email: [mbohblesspearl@gmail.com]. Then i could work on a loading script for you.

6. Run the application: Because you have 2 applications which as the Flask application and the chainlit application. Either you can run them in the same terminal or in different terminals. 
```bash
python app.py
```
```bash
python chatbot.py
```
7. Visit `http://localhost:5000` to view the application
8. Visit `http://localhost:8000` to view the chatbot

### Conclusion
The application is a simple demonstration of how we can switch from the basic approach of performing operations on the client site to a conversational customer support agent. The application is built with Flask, MongoDB and Chainlit. The application is still in its early stages and more features will be added in the future.

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgements
- [GDG Kigali](https://gdg.community.dev/gdg-kigali/)
- [MongoDB User Group](https://www.mongodb.com/community/forums/t/responsible-ai-kigali-mug-meetup-at-devfest-kigali-2024/300904)
- [Chainlit](https://chainlit.com/)
- [OpenAI](https://openai.com/)
- [Mboh Bless Pearl N](https://www.linkedin.com/in/mbohbless/)
- [Langchain](https://langchain.com/)

### Contact
For any questions or suggestions, please feel free to reach out to me at [mbohblesspearl@gmail.com](mailto:mbohblesspearl@gmail.com)

### Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. For major changes, please open an issue first to discuss what you would like to change.





