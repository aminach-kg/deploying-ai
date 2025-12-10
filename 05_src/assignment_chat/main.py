# main.py
# MarketMaven - AI Stock Market Advisor
# Main logic for the chat system

from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
import re
import os

# Load environment variables
load_dotenv("../.env")
load_dotenv("../.secrets")

# Initialize OpenAI client
client = OpenAI()

# Get model from environment or use default
open_ai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

## Service 1: Marketstack Stock Market API

class StockMarketService:
    """Service that fetches stock market data from Marketstack API and transforms it naturally"""
    
    def __init__(self):
        self.api_key = os.getenv("MARKETSTACK_API_KEY", "")
        self.base_url = "http://api.marketstack.com/v1"
    
    def get_stock_info(self, symbol):
        """Fetch latest stock data for a symbol"""
        try:
            endpoint = f"{self.base_url}/eod/latest"
            params = {
                "access_key": self.api_key,
                "symbols": symbol.upper()
            }
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    return data['data'][0]
            return None
        except Exception as e:
            print(f"Marketstack API Error: {e}")
            return None
    
    def transform_stock_data(self, stock_data, symbol):
        """Transform API response into natural language (NOT verbatim)"""
        if not stock_data:
            return f"I couldn't find stock information for {symbol.upper()}. Please verify the ticker symbol."
        
        close_price = stock_data.get('close', 0)
        open_price = stock_data.get('open', 0)
        high = stock_data.get('high', 0)
        low = stock_data.get('low', 0)
        volume = stock_data.get('volume', 0)
        
        price_change = close_price - open_price
        percent_change = (price_change / open_price * 100) if open_price > 0 else 0
        
        response = f"Here's what I found for {symbol.upper()}: "
        response += f"The stock closed at ${close_price:.2f}. "
        
        if price_change > 0:
            response += f"That's up ${abs(price_change):.2f} ({abs(percent_change):.2f}%) from the opening price of ${open_price:.2f}. "
            response += "The stock had a positive day! "
        elif price_change < 0:
            response += f"That's down ${abs(price_change):.2f} ({abs(percent_change):.2f}%) from the opening price of ${open_price:.2f}. "
            response += "The stock experienced some decline. "
        else:
            response += f"It stayed flat at the opening price of ${open_price:.2f}. "
        
        response += f"During trading, it ranged from a low of ${low:.2f} to a high of ${high:.2f}. "
        
        if volume > 1000000:
            response += f"There was significant trading activity with {volume:,.0f} shares exchanged."
        else:
            response += f"Trading volume was {volume:,.0f} shares."
        
        return response
    
    def compare_stocks(self, symbol1, symbol2):
        """Compare two stocks"""
        stock1 = self.get_stock_info(symbol1)
        stock2 = self.get_stock_info(symbol2)
        
        if not stock1 or not stock2:
            return f"I couldn't compare {symbol1.upper()} and {symbol2.upper()}. Please check both symbols."
        
        price1 = stock1.get('close', 0)
        price2 = stock2.get('close', 0)
        
        response = f"Comparing {symbol1.upper()} and {symbol2.upper()}:\n\n"
        response += f"{symbol1.upper()} is trading at ${price1:.2f}, "
        response += f"while {symbol2.upper()} is at ${price2:.2f}. "
        
        if price1 > price2:
            diff = ((price1 - price2) / price2) * 100
            response += f"{symbol1.upper()} is priced {diff:.1f}% higher."
        else:
            diff = ((price2 - price1) / price1) * 100
            response += f"{symbol2.upper()} is priced {diff:.1f}% higher."
        
        return response

## Service 2: Semantic Search on Movie Dataset

class MovieSearchService:
    """Service that performs semantic search on a movie plot dataset"""
    
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        
        self.collection_name = "movies"
        self.setup_collection()
    
    def setup_collection(self):
        """Setup ChromaDB collection with sample movie data"""
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print("✓ Loaded existing movie collection")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            
            movies = [
                {
                    "id": "1",
                    "title": "The Big Short",
                    "plot": "A group of investors bet against the US mortgage market during the housing bubble. They discover how corrupt and fragile the financial system is as they navigate the 2008 crisis.",
                    "year": "2015",
                    "genre": "Drama/Biography"
                },
                {
                    "id": "2",
                    "title": "The Wolf of Wall Street",
                    "plot": "A New York stockbroker rises to massive wealth through corruption and fraud. The film chronicles his wild lifestyle and eventual downfall as federal agents investigate his firm.",
                    "year": "2013",
                    "genre": "Biography/Comedy"
                },
                {
                    "id": "3",
                    "title": "Margin Call",
                    "plot": "Key players at an investment bank over a 24-hour period during the early stages of the 2008 financial crisis. They discover their firm is holding toxic assets that could destroy the company.",
                    "year": "2011",
                    "genre": "Drama/Thriller"
                },
                {
                    "id": "4",
                    "title": "Wall Street",
                    "plot": "A young stockbroker becomes involved with a ruthless corporate raider. He learns about greed, ambition, and corruption in the high-stakes world of finance.",
                    "year": "1987",
                    "genre": "Drama"
                },
                {
                    "id": "5",
                    "title": "Moneyball",
                    "plot": "The Oakland A's general manager uses analytics and statistics to assemble a competitive baseball team on a limited budget. It's about challenging conventional wisdom with data-driven decisions.",
                    "year": "2011",
                    "genre": "Biography/Drama"
                },
                {
                    "id": "6",
                    "title": "The Founder",
                    "plot": "The story of how Ray Kroc transformed McDonald's from a small burger restaurant into a global franchise empire. It explores ambition, business strategy, and entrepreneurship.",
                    "year": "2016",
                    "genre": "Biography/Drama"
                },
                {
                    "id": "7",
                    "title": "The Social Network",
                    "plot": "The founding of Facebook and the legal battles that followed. It depicts innovation, betrayal, and the rapid growth of a tech startup into a billion-dollar company.",
                    "year": "2010",
                    "genre": "Biography/Drama"
                },
                {
                    "id": "8",
                    "title": "Boiler Room",
                    "plot": "A college dropout gets a job at a suburban investment firm which puts him on the fast track to success. He soon discovers the firm's schemes and illegal practices.",
                    "year": "2000",
                    "genre": "Crime/Drama"
                }
            ]
            
            self.collection.add(
                documents=[m["plot"] for m in movies],
                metadatas=[{"title": m["title"], "year": m["year"], "genre": m["genre"]} for m in movies],
                ids=[m["id"] for m in movies]
            )
            print("✓ Created and populated movie collection")
    
    def search_movies(self, query, n_results=3):
        """Perform semantic search on movie plots"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results['documents'][0]:
                return "I couldn't find any movies matching your query."
            
            response = "Based on your interests, here are some movies you might enjoy:\n\n"
            
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                response += f"**{i+1}. {metadata['title']}** ({metadata['year']}) - {metadata['genre']}\n"
                response += f"   {doc}\n\n"
            
            return response
        except Exception as e:
            print(f"Search error: {e}")
            return "I encountered an error while searching for movies."

## Service 3: Function Calling Functions

def get_current_datetime():
    """Get current date and time"""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "month": now.strftime("%B"),
        "year": now.year
    }

def calculate_days_until(target_date_str):
    """Calculate days until a target date"""
    try:
        target = datetime.strptime(target_date_str, "%Y-%m-%d")
        today = datetime.now()
        delta = target - today
        return {
            "days": delta.days,
            "target_date": target_date_str,
            "is_past": delta.days < 0
        }
    except:
        return {"error": "Invalid date format. Please use YYYY-MM-DD"}

def calculate_investment_return(initial_amount, final_amount):
    """Calculate investment return percentage"""
    try:
        initial = float(initial_amount)
        final = float(final_amount)
        return_pct = ((final - initial) / initial) * 100
        profit = final - initial
        return {
            "return_percentage": round(return_pct, 2),
            "profit_loss": round(profit, 2),
            "initial": initial,
            "final": final
        }
    except:
        return {"error": "Invalid amounts provided"}

# Tools definition for OpenAI
tools = [
    {
        "type": "function",
        "name": "get_current_datetime",
        "description": "Get the current date, time, day of week, and month",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "calculate_days_until",
        "description": "Calculate the number of days from today until a specific date",
        "parameters": {
            "type": "object",
            "properties": {
                "target_date_str": {
                    "type": "string",
                    "description": "The target date in YYYY-MM-DD format"
                }
            },
            "required": ["target_date_str"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "calculate_investment_return",
        "description": "Calculate the return on investment given initial and final amounts",
        "parameters": {
            "type": "object",
            "properties": {
                "initial_amount": {
                    "type": "number",
                    "description": "The initial investment amount"
                },
                "final_amount": {
                    "type": "number",
                    "description": "The final investment value"
                }
            },
            "required": ["initial_amount", "final_amount"],
            "additionalProperties": False
        }
    }
]

## Guardrails

class Guardrails:
    """Implement safety guardrails for the chat system"""
    
    RESTRICTED_TOPICS = {
        "cat": ["cat", "cats", "kitten", "feline"],
        "dog": ["dog", "dogs", "puppy", "canine"],
        "horoscope": ["horoscope", "horoscopes", "astrology reading"],
        "zodiac": ["zodiac", "zodiac sign", "astrological sign", "star sign"],
        "taylor swift": ["taylor swift", "taylor alison swift", "t swift", "tswift"]
    }
    
    INJECTION_PATTERNS = [
        r"ignore\s+(?:previous|above|all|prior)\s+(?:instructions|prompts|directions|commands)",
        r"show\s+(?:me\s+)?(?:your\s+)?(?:system\s+)?prompt",
        r"what\s+(?:is|are)\s+your\s+(?:instructions|rules|guidelines|system prompt)",
        r"reveal\s+your\s+(?:prompt|instructions)",
        r"print\s+your\s+(?:system\s+)?prompt",
        r"display\s+your\s+instructions",
        r"forget\s+(?:all|your|previous)\s+instructions",
        r"new\s+instructions",
        r"system\s*:\s*you\s+are",
        r"disregard\s+(?:all|previous)"
    ]
    
    @staticmethod
    def check_restricted_topics(message):
        """Check if message contains restricted topics"""
        message_lower = message.lower()
        
        for topic_key, variations in Guardrails.RESTRICTED_TOPICS.items():
            for variation in variations:
                if variation in message_lower:
                    return True, topic_key
        
        return False, None
    
    @staticmethod
    def check_prompt_injection(message):
        """Check for system prompt injection attempts"""
        message_lower = message.lower()
        
        for pattern in Guardrails.INJECTION_PATTERNS:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    @staticmethod
    def get_restricted_response(topic):
        """Generate response for restricted topics"""
        responses = {
            "cat": "I'm sorry, but I don't discuss cats. Let's talk about stocks, movies, or market trends instead!",
            "dog": "I'm sorry, but I don't discuss dogs. How about we explore some investment opportunities?",
            "horoscope": "I'm sorry, but I don't provide horoscope readings. I prefer data-driven stock analysis!",
            "zodiac": "I'm sorry, but I don't discuss zodiac signs. Let's focus on market trends and financial insights!",
            "taylor swift": "I'm sorry, but I don't discuss Taylor Swift. Let me help you with stocks or movie recommendations instead!"
        }
        return responses.get(topic, "I'm sorry, but that topic is restricted.")
    
    @staticmethod
    def get_injection_response():
        """Generate response for prompt injection attempts"""
        return "🛡️ I notice you're trying to access my system instructions. I can't share those, but I'm happy to help you with stock market data, movie recommendations, or general questions about investing!"

## Initialize Services
stock_service = StockMarketService()
movie_service = MovieSearchService()
guardrails = Guardrails()

## Helper Functions

def should_use_stock_api(message):
    """Detect if stock service should be used"""
    message_lower = message.lower()
    stock_keywords = ["stock", "share", "ticker", "market", "price", "trading", "nasdaq", "dow"]
    ticker_pattern = r'\b[A-Z]{1,5}\b'
    has_ticker = bool(re.search(ticker_pattern, message))
    has_keyword = any(keyword in message_lower for keyword in stock_keywords)
    return has_keyword or has_ticker

def should_use_movies(message):
    """Detect if movie service should be used"""
    movie_keywords = ["movie", "film", "watch", "recommend", "cinema", "show"]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in movie_keywords)

def extract_ticker_symbols(message):
    """Extract stock ticker symbols from message"""
    pattern = r'\b[A-Z]{1,5}\b'
    tickers = re.findall(pattern, message)
    exclude = ['I', 'A', 'THE', 'AND', 'OR', 'FOR', 'TO', 'IN', 'ON', 'AT', 'BY', 'IS', 'IT']
    tickers = [t for t in tickers if t not in exclude]
    return tickers

def sanitize_history(history: list[dict]) -> list[dict]:
    """Clean history to keep only role and content"""
    clean_history = []
    for msg in history:
        clean_history.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })
    return clean_history

## Main Chat Function

def market_maven_chat(message: str, history: list[dict] = []) -> str:
    """Main chat function for MarketMaven"""
    
    # Check guardrails
    is_restricted, topic = guardrails.check_restricted_topics(message)
    if is_restricted:
        return guardrails.get_restricted_response(topic)
    
    if guardrails.check_prompt_injection(message):
        return guardrails.get_injection_response()
    
    # Check for stock queries (Service 1)
    if should_use_stock_api(message):
        tickers = extract_ticker_symbols(message)
        
        if len(tickers) == 1:
            stock_data = stock_service.get_stock_info(tickers[0])
            return stock_service.transform_stock_data(stock_data, tickers[0])
        elif len(tickers) == 2:
            return stock_service.compare_stocks(tickers[0], tickers[1])
        elif tickers:
            stock_data = stock_service.get_stock_info(tickers[0])
            return stock_service.transform_stock_data(stock_data, tickers[0])
    
    # Check for movie queries (Service 2)
    if should_use_movies(message):
        return movie_service.search_movies(message)
    
    # Get instructions
    from prompts import return_instructions_root
    instructions = return_instructions_root()
    
    # Prepare conversation
    user_msg = {
        "role": "user",
        "content": message
    }
    
    conversation_input = sanitize_history(history) + [user_msg]
    
    # Call OpenAI with function calling (Service 3)
    response = client.responses.create(
        model=open_ai_model,
        instructions=instructions,
        input=conversation_input,
        tools=tools,
    )
    
    conversation_input += response.output
    
    # Handle function calls
    for item in response.output:
        if item.type == "function_call":
            args = json.loads(item.arguments)
            
            # Execute appropriate function
            if item.name == "get_current_datetime":
                function_result = get_current_datetime()
            elif item.name == "calculate_days_until":
                function_result = calculate_days_until(**args)
            elif item.name == "calculate_investment_return":
                function_result = calculate_investment_return(**args)
            else:
                function_result = {"error": "Unknown function"}
            
            # Add function result to conversation
            func_call_output = {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(function_result)
            }
            
            conversation_input = conversation_input + [func_call_output]
            
            # Get final response
            response = client.responses.create(
                model=open_ai_model,
                instructions=instructions,
                tools=tools,
                input=conversation_input
            )
            break
    
    return response.output_text