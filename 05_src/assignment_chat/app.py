# app.py
# MarketMaven Chat Application
# Gradio interface for the AI Stock Market Advisor

import gradio as gr
from main import market_maven_chat
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('.env')
load_dotenv('.secrets')

# Create Gradio chat interface
chat = gr.ChatInterface(
    fn=market_maven_chat,
    type="messages",
    title="📈 MarketMaven - AI Stock Market Advisor",
    description="""
    Welcome! I'm MarketMaven, your friendly guide to stocks, markets, and finance films!
    Ask me about stock prices, market trends, movie recommendations on financial themes, or even help with basic financial calculations.   
    """,
    examples=[
        "What's the current price of AAPL?",
        "Compare MSFT and GOOGL",
        "Recommend movies about financial crises",
        "Calculate return from $5000 to $6500",
        "What day is today?",
        "How many days until 2025-12-25?"
    ],
    theme=gr.themes.Origin(),
    chatbot=gr.Chatbot(height=400)
)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting MarketMaven Chat System...")
    print("=" * 60)
    print("\n📋 SETUP CHECKLIST:")
    print("✓ Service 1: Marketstack API (Stock Market Data)")
    print("✓ Service 2: ChromaDB Semantic Search (Movies)")
    print("✓ Service 3: OpenAI Function Calling (Calculations)")
    print("✓ Guardrails: Implemented")
    print("✓ Conversation Memory: Enabled")
    
    print("\n🔑 ENVIRONMENT VARIABLES:")
    print(f"  OPENAI_API_KEY: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ NOT SET'}")
    print(f"  MARKETSTACK_API_KEY: {'✓ Set' if os.getenv('MARKETSTACK_API_KEY') else '✗ NOT SET'}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  WARNING: OPENAI_API_KEY not set!")
        print("   Set it in .secrets file or export OPENAI_API_KEY='your-key'")
    
    if not os.getenv('MARKETSTACK_API_KEY'):
        print("\n⚠️  WARNING: MARKETSTACK_API_KEY not set!")
        print("   Get FREE key at: https://marketstack.com/signup/free")
        print("   Set it in .secrets file or export MARKETSTACK_API_KEY='your-key'")
    
    print("\n" + "=" * 60)
    print("🌐 LAUNCHING WEB INTERFACE...")
    print("=" * 60)
    
    chat.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        debug=True
    )
