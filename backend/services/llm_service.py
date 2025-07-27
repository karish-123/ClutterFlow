# # backend/services/llm_service.py
# import asyncio
# import logging
# import time
# import re
# from typing import Dict, List, Optional
# from dataclasses import dataclass
# import json
# import google.generativeai as genai
# from config.settings import settings

# logger = logging.getLogger(__name__)

# @dataclass
# class LLMResult:
#     content: str
#     model_used: str
#     tokens_used: Optional[int]
#     processing_time: float
#     metadata: Dict

# class LLMService:
#     def __init__(self):
#         self.model_name = "gemini-1.5-flash"
#         self.max_tokens = 2048
#         self.timeout = 30
        
#         # Configure Gemini
#         genai.configure(api_key=settings.gemini_api_key)
#         self.model = genai.GenerativeModel('gemini-1.5-flash')
        
#         # Generation config
#         self.generation_config = genai.types.GenerationConfig(
#             temperature=0.7,
#             top_p=0.9,
#             max_output_tokens=self.max_tokens,
#         )

#     async def health_check(self) -> bool:
#         """Check if Gemini API is accessible"""
#         try:
#             # Try a simple generation to test API connectivity
#             test_prompt = "Hello"
#             response = await asyncio.to_thread(
#                 self.model.generate_content,
#                 test_prompt,
#                 generation_config=self.generation_config
#             )
            
#             if response and response.text:
#                 logger.info("✅ Gemini API health check passed")
#                 return True
#             else:
#                 logger.error("❌ Gemini API returned empty response")
#                 return False
                
#         except Exception as e:
#             logger.error(f"❌ Gemini API health check failed: {e}")
#             return False

#     def chunk_text(self, text: str, max_chunk_size: int = None) -> List[str]:
#         """Split large text into smaller chunks for processing"""
#         if max_chunk_size is None:
#             max_chunk_size = 30000  # Gemini can handle larger chunks
        
#         # Simple chunking by sentences to avoid cutting in the middle
#         sentences = re.split(r'[.!?]+', text)
#         chunks = []
#         current_chunk = ""
        
#         for sentence in sentences:
#             sentence = sentence.strip()
#             if not sentence:
#                 continue
            
#             # If adding this sentence would exceed limit, start new chunk
#             if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
#                 chunks.append(current_chunk.strip())
#                 current_chunk = sentence
#             else:
#                 current_chunk += " " + sentence if current_chunk else sentence
        
#         # Add the last chunk
#         if current_chunk.strip():
#             chunks.append(current_chunk.strip())
        
#         return chunks

#     def estimate_tokens(self, text: str) -> int:
#         """Rough estimation of tokens (1 token ≈ 4 characters)"""
#         return len(text) // 4

#     async def _generate_response(self, prompt: str) -> LLMResult:
#         """Core method to interact with Gemini"""
#         start_time = time.time()
        
#         try:
#             response = await asyncio.to_thread(
#                 self.model.generate_content,
#                 prompt,
#                 generation_config=self.generation_config
#             )
            
#             processing_time = time.time() - start_time
            
#             if not response or not response.text:
#                 raise Exception("Empty response from Gemini")
            
#             return LLMResult(
#                 content=response.text.strip(),
#                 model_used=self.model_name,
#                 tokens_used=self.estimate_tokens(response.text),
#                 processing_time=processing_time,
#                 metadata={
#                     'prompt_tokens': self.estimate_tokens(prompt),
#                     'total_tokens': self.estimate_tokens(prompt + response.text),
#                     'finish_reason': 'completed'
#                 }
#             )
            
#         except Exception as e:
#             logger.error(f"Error generating response with Gemini: {e}")
#             raise Exception(f"LLM generation failed: {str(e)}")

#     async def summarize_text(self, text: str, summary_type: str = "brief") -> LLMResult:
#         """Generate a summary of the given text"""
#         # Handle different summary types
#         if summary_type == "brief":
#             instruction = "Write a brief 2-3 sentence summary of the following text:"
#             max_length = "Keep it under 200 words."
#         elif summary_type == "detailed":
#             instruction = "Write a detailed summary of the following text, covering all key points:"
#             max_length = "Aim for 300-500 words."
#         elif summary_type == "bullet_points":
#             instruction = "Create a bullet-point summary of the following text:"
#             max_length = "Use 5-10 bullet points."
#         else:
#             instruction = "Summarize the following text:"
#             max_length = "Keep it concise."

#         # Gemini can handle larger text, but still chunk very large documents
#         if len(text) > 40000:  # ~40k characters
#             chunks = self.chunk_text(text, 30000)
#             chunk_summaries = []
            
#             for i, chunk in enumerate(chunks):
#                 chunk_prompt = f"{instruction}\n\nText chunk {i+1}:\n{chunk}\n\n{max_length}"
#                 chunk_result = await self._generate_response(chunk_prompt)
#                 chunk_summaries.append(chunk_result.content)
            
#             # Combine chunk summaries
#             combined_summary = "\n".join(chunk_summaries)
#             final_prompt = f"Combine these summaries into one cohesive {summary_type} summary:\n\n{combined_summary}\n\n{max_length}"
#             return await self._generate_response(final_prompt)
#         else:
#             # Single summary for shorter text
#             prompt = f"{instruction}\n\nText:\n{text}\n\n{max_length}"
#             return await self._generate_response(prompt)

#     async def classify_topic(self, text: str, available_subjects: Optional[List[str]] = None) -> LLMResult:
#         """Classify the document into topics and categories using actual database subjects"""
        
#         # If no subjects provided, use default categories as fallback
#         if not available_subjects:
#             available_subjects = [
#                 "business", "personal", "academic", "legal",
#                 "medical", "technical", "financial", "travel", "other"
#             ]
        
#         subjects_str = ", ".join(available_subjects)
        
#         prompt = f"""Analyze the following text and classify it using ONLY the available subjects listed below.

# Available subjects to choose from:
# {subjects_str}

# Text to analyze:
# {text[:3000]}

# Instructions:
# 1. Read the text carefully
# 2. Choose the BEST matching subject from the available subjects list above
# 3. If the text clearly matches one of the subjects, be confident (0.8+ confidence)
# 4. Only use "other" if the text truly doesn't match any available subject
# 5. The primary_topic MUST be exactly one of the subjects from the list above

# Respond with ONLY valid JSON in this exact format:
# {{
#     "primary_topic": "exact subject name from the list above",
#     "category": "academic",
#     "confidence": 0.85,
#     "tags": ["relevant", "keywords", "from", "text"],
#     "reasoning": "why you chose this specific subject from the available options"
# }}

# Remember: primary_topic must be EXACTLY one of these: {subjects_str}"""

#         result = await self._generate_response(prompt)
        
#         # Try to extract JSON from response
#         try:
#             # Find JSON in the response
#             json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
#             if json_match:
#                 classification_data = json.loads(json_match.group())
                
#                 # Validate that the chosen subject is in the available list
#                 chosen_subject = classification_data.get('primary_topic', 'other')
#                 if chosen_subject not in available_subjects:
#                     logger.warning(f"LLM chose subject '{chosen_subject}' not in available list. Defaulting to 'other'")
#                     classification_data['primary_topic'] = 'other'
#                     classification_data['confidence'] = 0.3
                
#                 result.metadata.update(classification_data)
#         except (json.JSONDecodeError, AttributeError) as e:
#             logger.warning(f"Could not parse classification JSON: {e}")
#             # Fallback classification
#             result.metadata.update({
#                 "primary_topic": "other",
#                 "category": "other", 
#                 "confidence": 0.3,
#                 "tags": [],
#                 "reasoning": "Failed to parse LLM response"
#             })
        
#         return result

#         result = await self._generate_response(prompt)
        
#         # Try to extract JSON from response
#         try:
#             # Find JSON in the response
#             json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
#             if json_match:
#                 classification_data = json.loads(json_match.group())
#                 result.metadata.update(classification_data)
#         except (json.JSONDecodeError, AttributeError) as e:
#             logger.warning(f"Could not parse classification JSON: {e}")
#             # Fallback classification
#             result.metadata.update({
#                 "primary_topic": "unknown",
#                 "category": "other", 
#                 "confidence": 0.5,
#                 "tags": [],
#                 "reasoning": "Failed to parse LLM response"
#             })
        
#         return result

#     async def extract_keywords(self, text: str, max_keywords: int = 10) -> LLMResult:
#         """Extract relevant keywords and phrases from text"""
#         prompt = f"""Extract the most important keywords and phrases from the following text.
# Provide exactly {max_keywords} keywords/phrases, ranked by importance.

# Text:
# {text[:3000]}...

# Respond with ONLY a JSON array of strings, like:
# ["keyword1", "keyword2", "important phrase", "keyword3", ...]

# Make sure the JSON is valid."""

#         result = await self._generate_response(prompt)
        
#         # Try to extract keywords array
#         try:
#             keywords_match = re.search(r'\[.*\]', result.content, re.DOTALL)
#             if keywords_match:
#                 keywords = json.loads(keywords_match.group())
#                 result.metadata['keywords'] = keywords
#         except (json.JSONDecodeError, AttributeError) as e:
#             logger.warning(f"Could not parse keywords JSON: {e}")
#             result.metadata['keywords'] = []
        
#         return result

#     async def classify_with_db_subjects(self, text: str, db_service) -> LLMResult:
#         """Classify text using subjects from database"""
#         try:
#             # Get available subjects from database
#             subjects_result = db_service.supabase.table('subjects').select('name').execute()
            
#             if subjects_result.data:
#                 available_subjects = [subject['name'] for subject in subjects_result.data]
#                 logger.info(f"Using {len(available_subjects)} subjects from database: {available_subjects}")
#             else:
#                 logger.warning("No subjects found in database, using default categories")
#                 available_subjects = ["mathematics", "science", "history", "literature", "business", "technology", "other"]
            
#             return await self.classify_topic(text, available_subjects)
            
#         except Exception as e:
#             logger.error(f"Error fetching subjects from database: {e}")
#             # Fallback to default classification
#             return await self.classify_topic(text)

# # Global LLM service instance
# llm_service = LLMService()
# backend/services/llm_service.py
import asyncio
import logging
import time
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import google.generativeai as genai
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
        self.model_name = "gemini-1.5-flash"
        self.max_tokens = 2048
        self.timeout = 30
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=self.max_tokens,
        )

    async def health_check(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            # Try a simple generation to test API connectivity
            test_prompt = "Hello"
            response = await asyncio.to_thread(
                self.model.generate_content,
                test_prompt,
                generation_config=self.generation_config
            )
            
            if response and response.text:
                logger.info("✅ Gemini API health check passed")
                return True
            else:
                logger.error("❌ Gemini API returned empty response")
                return False
                
        except Exception as e:
            logger.error(f"❌ Gemini API health check failed: {e}")
            return False

    def chunk_text(self, text: str, max_chunk_size: int = None) -> List[str]:
        """Split large text into smaller chunks for processing"""
        if max_chunk_size is None:
            max_chunk_size = 30000  # Gemini can handle larger chunks
        
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
        """Core method to interact with Gemini"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=self.generation_config
            )
            
            processing_time = time.time() - start_time
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            return LLMResult(
                content=response.text.strip(),
                model_used=self.model_name,
                tokens_used=self.estimate_tokens(response.text),
                processing_time=processing_time,
                metadata={
                    'prompt_tokens': self.estimate_tokens(prompt),
                    'total_tokens': self.estimate_tokens(prompt + response.text),
                    'finish_reason': 'completed'
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {e}")
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

        # Gemini can handle larger text, but still chunk very large documents
        if len(text) > 40000:  # ~40k characters
            chunks = self.chunk_text(text, 30000)
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

    async def classify_topic(self, text: str, available_subjects: Optional[List[str]] = None) -> LLMResult:
        """Classify the document into topics and categories using actual database subjects"""
        
        # If no subjects provided, use default categories as fallback
        if not available_subjects:
            available_subjects = [
                "business", "personal", "academic", "legal",
                "medical", "technical", "financial", "travel", "other"
            ]
        
        subjects_str = ", ".join(available_subjects)
        
        prompt = f"""Analyze the following text and classify it using ONLY the available subjects listed below.

Available subjects to choose from:
{subjects_str}

Text to analyze:
{text[:3000]}

Instructions:
1. Read the text carefully
2. Choose the BEST matching subject from the available subjects list above
3. If the text clearly matches one of the subjects, be confident (0.8+ confidence)
4. Only use "other" if the text truly doesn't match any available subject
5. The primary_topic MUST be exactly one of the subjects from the list above
6. Be case-sensitive and match the exact subject names

Respond with ONLY valid JSON in this exact format:
{{
    "primary_topic": "exact subject name from the list above",
    "category": "academic",
    "confidence": 0.85,
    "tags": ["relevant", "keywords", "from", "text"],
    "reasoning": "why you chose this specific subject from the available options"
}}

Remember: primary_topic must be EXACTLY one of these: {subjects_str}"""

        result = await self._generate_response(prompt)
        
        # Try to extract JSON from response
        try:
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_match:
                classification_data = json.loads(json_match.group())
                
                # Validate that the chosen subject is in the available list
                chosen_subject = classification_data.get('primary_topic', 'other')
                
                # Try exact match first
                if chosen_subject in available_subjects:
                    result.metadata.update(classification_data)
                    logger.info(f"✅ Exact match found: {chosen_subject}")
                else:
                    # Try case-insensitive match
                    chosen_lower = chosen_subject.lower()
                    match_found = False
                    
                    for subject in available_subjects:
                        if subject.lower() == chosen_lower:
                            classification_data['primary_topic'] = subject  # Use the correct case
                            result.metadata.update(classification_data)
                            logger.info(f"✅ Case-insensitive match found: {subject}")
                            match_found = True
                            break
                    
                    # Try partial match as last resort
                    if not match_found:
                        for subject in available_subjects:
                            if chosen_lower in subject.lower() or subject.lower() in chosen_lower:
                                classification_data['primary_topic'] = subject
                                classification_data['confidence'] = max(0.3, classification_data.get('confidence', 0.5) - 0.2)
                                result.metadata.update(classification_data)
                                logger.info(f"⚠️ Partial match found: {subject}")
                                match_found = True
                                break
                    
                    # If still no match, default to 'other' or create fallback
                    if not match_found:
                        logger.warning(f"❌ No match found for '{chosen_subject}'. Available: {available_subjects}")
                        # Try to use 'other' if it exists, otherwise use first available subject
                        fallback_subject = 'other' if 'other' in available_subjects else available_subjects[0]
                        classification_data['primary_topic'] = fallback_subject
                        classification_data['confidence'] = 0.3
                        classification_data['reasoning'] = f"No match found for '{chosen_subject}', defaulted to '{fallback_subject}'"
                        result.metadata.update(classification_data)
                        
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Could not parse classification JSON: {e}")
            logger.debug(f"Raw LLM response: {result.content}")
            
            # Fallback classification
            fallback_subject = 'other' if 'other' in available_subjects else available_subjects[0]
            result.metadata.update({
                "primary_topic": fallback_subject,
                "category": "other", 
                "confidence": 0.3,
                "tags": [],
                "reasoning": f"Failed to parse LLM response, defaulted to '{fallback_subject}'"
            })
        
        return result

    async def extract_keywords(self, text: str, max_keywords: int = 10) -> LLMResult:
        """Extract relevant keywords and phrases from text"""
        prompt = f"""Extract the most important keywords and phrases from the following text.
Provide exactly {max_keywords} keywords/phrases, ranked by importance.

Text:
{text[:3000]}...

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

    async def classify_with_db_subjects(self, text: str, db_service) -> LLMResult:
        """Classify text using subjects from database"""
        try:
            # Get available subjects from database
            # subjects_result = db_service.supabase.table('subjects').select('name').execute()
            subjects_result = db_service.supabase.table('user_subjects').select('subject_name').eq('is_active', True).execute()
            if subjects_result.data:
                available_subjects = [subject['name'].strip() for subject in subjects_result.data]  # Strip whitespace
                logger.info(f"📚 Using {len(available_subjects)} subjects from database")
                logger.debug(f"Available subjects: {available_subjects}")
            else:
                logger.warning("No subjects found in database, using default categories")
                available_subjects = ["Mathematics", "Science", "History", "Literature", "Business", "Technology", "Other"]
            
            # Ensure 'Other' or 'other' exists as fallback
            if not any(s.lower() == 'other' for s in available_subjects):
                available_subjects.append('Other')
            
            classification_result = await self.classify_topic(text, available_subjects)
            
            # Log the final classification
            final_topic = classification_result.metadata.get('primary_topic', 'Unknown')
            confidence = classification_result.metadata.get('confidence', 0.0)
            logger.info(f"🎯 Final classification: '{final_topic}' (confidence: {confidence:.2%})")
            
            return classification_result
            
        except Exception as e:
            logger.error(f"❌ Error fetching subjects from database: {e}")
            # Fallback to default classification
            return await self.classify_topic(text)

# Global LLM service instance
llm_service = LLMService()