# Assignment 2
The goal of this assignment is to design and implement an AI system with a conversational interface.

## Overview

MarketMaven is a conversational system that combines **stock market data**, **semantic movie search**, and **financial calculations** into a unified chat interface.

## Services Implementation

### Service 1: Marketstack API Integration

**Technology:** Marketstack REST API  
**Purpose:** Fetch real-time stock market data

**Implementation Details:**
- Uses Marketstack's free tier API for stock data
- Fetches end-of-day (EOD) and intraday stock prices
- **Transforms API responses into natural language** (NOT verbatim)
- Features:
  - Single stock lookup (e.g., "What's AAPL?")
  - Stock comparison (e.g., "Compare MSFT and GOOGL")
  - Price change calculations and analysis
  - Volume and trading range information

**Transformation Example:**
- **API Response:** `{"close": 150.25, "open": 148.50, "high": 151.00, "low": 147.80}`
- **Transformed Output:** "Here's what I found for AAPL: The stock closed at $150.25. That's up $1.75 (1.18%) from the opening price of $148.50. The stock had a positive day! During trading, it ranged from a low of $147.80 to a high of $151.00."


### Service 2: Semantic Search with ChromaDB

**Technology:** ChromaDB with OpenAI embeddings  
**Purpose:** Search movie database based on semantic similarity

**Implementation Details:**
- **Persistent storage** using ChromaDB's PersistentClient
- Dataset: 10 finance/business-themed movies
- Embeddings: OpenAI's `text-embedding-3-small` model
- Search algorithm: Vector similarity search on plot descriptions

**Dataset Theme:**
Selected finance and business movies to align with the stock market advisor personality:
- The Big Short (2015)
- The Wolf of Wall Street (2013)
- Margin Call (2011)
- Wall Street (1987)
- Moneyball (2011)
- The Founder (2016)
- The Social Network (2010)
- Boiler Room (2000)
- Too Big to Fail (2011)
- Rogue Trader (1999)

**Embedding Process:**
1. Movie plots are embedded using OpenAI's API
2. Embeddings are stored in ChromaDB with persistent file storage
3. Search queries are embedded and matched against stored vectors
4. Top N most similar movies are returned


### Service 3: Function Calling

**Technology:** OpenAI Function Calling API  
**Purpose:** Enable structured computations and data retrieval

**Implemented Functions:**

1. **`get_current_datetime()`**
   - Returns current date, time, day of week, month, and year
   - Use case: "What day is it today?"

2. **`calculate_days_until(target_date_str)`**
   - Calculates days between today and a target date
   - Use case: "How many days until 2025-12-31?"

3. **`calculate_investment_return(initial_amount, final_amount)`**
   - Calculates ROI percentage and profit/loss
   - Use case: "Calculate return from $1000 to $1500"

**Why Function Calling?**
- Enables precise calculations that LLMs struggle with
- Provides real-time data (current date/time)
- Structured output for financial computations
- More reliable than asking LLM to calculate


## Guardrails & Safety

1. **System Prompt Protection**
   - Detects prompt injection attempts
   - Blocks requests to reveal/modify system instructions
   - Pattern matching for common injection techniques

2. **Restricted Topics**
   - Cats/Dogs
   - Horoscopes/Zodiac signs
   - Taylor Swift
   - Returns polite refusal messages

3. **Input Validation**
   - Checks all user inputs before processing
   - Sanitizes ticker symbols and dates
   - Error handling for malformed requests




## Deployment Instructions

**Prerequisites:**
```bash
- gradio
- openai
- chromadb
- requests
- numpy
```


## File Structure

```
./05_src/assignment_chat/
├── app.py                      # app code
├── main.py                     # main python package
├── prompts.py                  # prompts
└── readne.md                   # This file
```