# backend/services/llm_service.py
import ollama
import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class LLMResult:
    content: str
    model_used: str
    tokens_used: Optional[int]
    processing_time: float
    metadata: Dict

class LLMService:
    def __init__(self):
        self.base_url = getattr(settings, 'ollama_base_url', 'http://localhost:11434')
        self.model_name = getattr(settings, 'ollama_model', 'mistral:7b')
        self.max_tokens = getattr(settings, 'max_tokens', 2000)
        self.timeout = getattr(settings, 'ollama_timeout', 60)
        
        # Initialize Ollama client
        self.client = ollama.Client(host=self.base_url)
        
    async def health_check(self) -> bool:
        """Check if Ollama service is running and model is available"""
        try:
            # Check if Ollama is running
            models_response = await asyncio.to_thread(self.client.list)
            
            # Extract model names from Model objects
            model_names = []
            if hasattr(models_response, 'models'):
                for model in models_response.models:
                    if hasattr(model, 'model'):
                        model_names.append(model.model)
            
            print(f"Debug - Available models: {model_names}")  # Debug print
            
            # Check if our model is available (check both mistral:7b and mistral:latest)
            is_available = any(self.model_name in name or name.startswith('mistral') for name in model_names)
            
            if is_available:
                logger.info(f"✅ Ollama health check passed. Model {self.model_name} is available")
                print(f"✅ Model {self.model_name} found!")
            else:
                logger.warning(f"⚠️ Model {self.model_name} not found. Available: {model_names}")
                print(f"⚠️ Model {self.model_name} not found. Available: {model_names}")
                
            return is_available
            
        except Exception as e:
            logger.error(f"❌ Ollama health check failed: {e}")
            print(f"❌ Health check error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def chunk_text(self, text: str, max_chunk_size: int = None) -> List[str]:
        """Split large text into smaller chunks for processing"""
        if max_chunk_size is None:
            max_chunk_size = self.max_tokens
            
        # Simple chunking by sentences to avoid cutting in the middle
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed limit, start new chunk
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimation of tokens (1 token ≈ 4 characters)"""
        return len(text) // 4
    
    async def _generate_response(self, prompt: str) -> LLMResult:
        """Core method to interact with Ollama"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.client.generate,
                model=self.model_name,
                prompt=prompt,
                stream=False,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': self.max_tokens
                }
            )
            
            processing_time = time.time() - start_time
            
            return LLMResult(
                content=response['response'].strip(),
                model_used=self.model_name,
                tokens_used=self.estimate_tokens(response['response']),
                processing_time=processing_time,
                metadata={
                    'prompt_tokens': self.estimate_tokens(prompt),
                    'total_tokens': self.estimate_tokens(prompt + response['response']),
                    'done_reason': response.get('done_reason', 'completed')
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise Exception(f"LLM generation failed: {str(e)}")
    
    async def summarize_text(self, text: str, summary_type: str = "brief") -> LLMResult:
        """Generate a summary of the given text"""
        
        # Handle different summary types
        if summary_type == "brief":
            instruction = "Write a brief 2-3 sentence summary of the following text:"
            max_length = "Keep it under 200 words."
        elif summary_type == "detailed":
            instruction = "Write a detailed summary of the following text, covering all key points:"
            max_length = "Aim for 300-500 words."
        elif summary_type == "bullet_points":
            instruction = "Create a bullet-point summary of the following text:"
            max_length = "Use 5-10 bullet points."
        else:
            instruction = "Summarize the following text:"
            max_length = "Keep it concise."
        
        # If text is too long, chunk it and summarize each chunk
        if len(text) > self.max_tokens * 3:  # roughly 6000 characters
            chunks = self.chunk_text(text, self.max_tokens // 2)
            chunk_summaries = []
            
            for i, chunk in enumerate(chunks):
                chunk_prompt = f"{instruction}\n\nText chunk {i+1}:\n{chunk}\n\n{max_length}"
                chunk_result = await self._generate_response(chunk_prompt)
                chunk_summaries.append(chunk_result.content)
            
            # Combine chunk summaries
            combined_summary = "\n".join(chunk_summaries)
            final_prompt = f"Combine these summaries into one cohesive {summary_type} summary:\n\n{combined_summary}\n\n{max_length}"
            
            return await self._generate_response(final_prompt)
        else:
            # Single summary for shorter text
            prompt = f"{instruction}\n\nText:\n{text}\n\n{max_length}"
            return await self._generate_response(prompt)
    
    async def classify_topic(self, text: str, categories: Optional[List[str]] = None) -> LLMResult:
        """Classify the document into topics and categories"""
        
        default_categories = [
            "business", "personal", "academic", "legal", 
            "medical", "technical", "financial", "travel", "other"
        ]
        
        categories_to_use = categories if categories else default_categories
        categories_str = ", ".join(categories_to_use)
        
        prompt = f"""Analyze the following text and provide a classification in JSON format:

Text to analyze:
{text[:2000]}...  

Please respond with ONLY a valid JSON object in this exact format:
{{
    "primary_topic": "main topic in 2-3 words",
    "category": "one of: {categories_str}",
    "confidence": 0.95,
    "tags": ["keyword1", "keyword2", "keyword3"],
    "reasoning": "brief explanation of classification"
}}

Ensure the JSON is valid and uses only the categories provided."""
        
        result = await self._generate_response(prompt)
        
        # Try to extract JSON from response
        try:
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_match:
                classification_data = json.loads(json_match.group())
                result.metadata.update(classification_data)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Could not parse classification JSON: {e}")
            # Fallback classification
            result.metadata.update({
                "primary_topic": "unknown",
                "category": "other",
                "confidence": 0.5,
                "tags": [],
                "reasoning": "Failed to parse LLM response"
            })
        
        return result
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> LLMResult:
        """Extract relevant keywords and phrases from text"""
        
        prompt = f"""Extract the most important keywords and phrases from the following text.
Provide exactly {max_keywords} keywords/phrases, ranked by importance.

Text:
{text[:2000]}...

Respond with ONLY a JSON array of strings, like:
["keyword1", "keyword2", "important phrase", "keyword3", ...]

Make sure the JSON is valid."""
        
        result = await self._generate_response(prompt)
        
        # Try to extract keywords array
        try:
            keywords_match = re.search(r'\[.*\]', result.content, re.DOTALL)
            if keywords_match:
                keywords = json.loads(keywords_match.group())
                result.metadata['keywords'] = keywords
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Could not parse keywords JSON: {e}")
            result.metadata['keywords'] = []
        
        return result
    
    async def answer_question(self, text: str, question: str) -> LLMResult:
        """Answer a question based on the document content"""
        
        prompt = f"""Based on the following document content, answer this question: "{question}"

Document content:
{text[:3000]}...

Question: {question}

Please provide a clear, concise answer based only on the information in the document. If the answer cannot be found in the document, say "The answer is not available in this document." """
        
        return await self._generate_response(prompt)

# Global LLM service instance
llm_service = LLMService()