import os
from flask import Flask, request, jsonify 
import openai
from textblob import TextBlob

app = Flask(__name__)

# OpenAI API key from environment variable
openai.api_key = os.getenv("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")

# Product details and initial price
product = "Laptop"
initial_price = 35000

# Price range
min_price = 32000
max_discount = 3000

# Function to extract price from user input
def extract_price(user_input):
    try:
        price = int(''.join(filter(str.isdigit, user_input)))
        return price
    except ValueError:
        return None

# Function to analyze sentiment using TextBlob
def analyze_sentiment(user_input):
    analysis = TextBlob(user_input)
    sentiment = analysis.sentiment.polarity  # Polarity: -1 (negative) to +1 (positive)
    return sentiment

# Function to negotiate price with ChatGPT
def negotiate_price(user_offer, user_input):
    sentiment = analyze_sentiment(user_input)
    discount = 0

    # Define discount based on sentiment
    if sentiment > 0.5:
        discount = max_discount  # Larger discount for positive sentiment
    elif sentiment < -0.2:  
        discount = 0  # No discount for very negative sentiment
    else:
        discount = max_discount // 2  # Smaller discount for neutral sentiment

    final_price = initial_price - discount

    prompt = (f"The user has offered ${user_offer} for a {product}. "
              f"The initial price is ${initial_price}. "
              f"The discount is ${discount}, making the final price ${final_price}. "
              f"Respond as a salesperson negotiating a price. "
              f"Sentiment of the user is {sentiment:.2f}.")

    # OpenAI API to get a response from ChatGPT
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )

    return response.choices[0].text.strip()

# Route for chatbot conversation
@app.route('/chat', methods=['POST'])
def chatbot():
    user_input = request.json.get("message")
    user_price_offer = extract_price(user_input)

    if user_price_offer is not None:
        response = negotiate_price(user_price_offer, user_input)
    else:
        response = f"I can offer you a {product} for ${initial_price}. Would you like to negotiate?"

    return jsonify({"response": response})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

