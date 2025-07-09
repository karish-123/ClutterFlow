# backend/test_llm.py
# Quick test script for LLM service

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import llm_service

async def test_llm_service():
    print("🔍 Testing LLM Service...")
    
    # Test 1: Health Check
    print("\n1. Testing Ollama connection...")
    is_healthy = await llm_service.health_check()
    if not is_healthy:
        print("❌ Ollama is not running or model not available")
        print("Make sure you've run: ollama serve & ollama pull mistral:7b")
        return
    
    # Test 2: Text Summarization
    print("\n2. Testing text summarization...")
    sample_text = """
    Artificial Intelligence (AI) is a rapidly growing field that focuses on creating 
    intelligent machines capable of performing tasks that typically require human intelligence. 
    Machine learning, a subset of AI, uses algorithms to learn patterns from data without 
    being explicitly programmed. Deep learning, a further subset of machine learning, 
    uses neural networks with multiple layers to process complex data. AI applications 
    include natural language processing, computer vision, robotics, and autonomous vehicles. 
    The field has seen tremendous growth in recent years due to advances in computing power, 
    data availability, and algorithmic improvements.
    """
    
    try:
        summary_result = await llm_service.summarize_text(sample_text, "brief")
        print(f"✅ Summary generated:")
        print(f"   Content: {summary_result.content}")
        print(f"   Processing time: {summary_result.processing_time:.2f}s")
        print(f"   Tokens used: {summary_result.tokens_used}")
    except Exception as e:
        print(f"❌ Summarization failed: {e}")
        return
    
    # Test 3: Topic Classification
    print("\n3. Testing topic classification...")
    try:
        classification_result = await llm_service.classify_topic(sample_text)
        print(f"✅ Classification generated:")
        print(f"   Content: {classification_result.content}")
        print(f"   Metadata: {classification_result.metadata}")
    except Exception as e:
        print(f"❌ Classification failed: {e}")
        return
    
    # Test 4: Keyword Extraction
    print("\n4. Testing keyword extraction...")
    try:
        keywords_result = await llm_service.extract_keywords(sample_text, 5)
        print(f"✅ Keywords extracted:")
        print(f"   Content: {keywords_result.content}")
        print(f"   Keywords: {keywords_result.metadata.get('keywords', [])}")
    except Exception as e:
        print(f"❌ Keyword extraction failed: {e}")
        return
    
    print("\n🎉 All LLM tests passed! Ready for integration.")

if __name__ == "__main__":
    asyncio.run(test_llm_service())