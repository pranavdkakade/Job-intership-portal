"""
Single Topic RAG Service
Uses FAISS to retrieve relevant questions from question banks
"""

import pickle
import random
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from django.conf import settings


class SingleTopicRAG:
    """RAG service for single topic question retrieval"""
    
    def __init__(self, topic: str):
        """
        Initialize RAG for a specific topic
        Args:
            topic: 'sql' or 'python'
        """
        self.topic = topic.lower()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Paths
        self.base_dir = Path(settings.MEDIA_ROOT)
        self.vector_store_dir = self.base_dir / 'vector_stores' / self.topic
        self.index_path = self.vector_store_dir / 'faiss_index.bin'
        self.questions_path = self.vector_store_dir / 'questions.pkl'
        self.metadata_path = self.vector_store_dir / 'metadata.pkl'
        
        # Load vector store
        self.index = None
        self.questions = []
        self.metadata = []
        self._load_vector_store()
        
        # Track used questions to avoid repetition
        self.used_question_indices = set()
    
    def _load_vector_store(self):
        """Load FAISS index and questions from disk"""
        try:
            if not self.index_path.exists():
                raise FileNotFoundError(
                    f"Vector store not found for {self.topic}. "
                    f"Please run: python manage.py build_question_banks"
                )
            
            self.index = faiss.read_index(str(self.index_path))
            
            with open(self.questions_path, 'rb') as f:
                self.questions = pickle.load(f)
            
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            print(f"✅ Loaded {len(self.questions)} {self.topic} questions")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load vector store for {self.topic}: {e}")
    
    def get_question_by_difficulty(
        self, 
        difficulty: str = "medium",
        question_number: int = 1
    ) -> str:
        """
        Get a question based on difficulty level
        Args:
            difficulty: 'easy', 'medium', 'hard'
            question_number: Question number in the interview (1-5)
        Returns:
            A relevant question string
        """
        # Map difficulty to search strategy
        if difficulty == "easy":
            return self._get_random_question()
        elif difficulty == "hard":
            return self._get_complex_question()
        else:
            return self._get_random_question()
    
    def _get_random_question(self) -> str:
        """Get a random unused question"""
        available_indices = set(range(len(self.questions))) - self.used_question_indices
        
        if not available_indices:
            # Reset if all questions used
            self.used_question_indices.clear()
            available_indices = set(range(len(self.questions)))
        
        selected_idx = random.choice(list(available_indices))
        self.used_question_indices.add(selected_idx)
        
        return self.questions[selected_idx]
    
    def _get_complex_question(self) -> str:
        """
        Get a more complex question (longer questions tend to be more detailed)
        """
        available_indices = set(range(len(self.questions))) - self.used_question_indices
        
        if not available_indices:
            self.used_question_indices.clear()
            available_indices = set(range(len(self.questions)))
        
        # Sort by length and pick from top 30%
        available_questions = [(idx, len(self.questions[idx])) 
                               for idx in available_indices]
        available_questions.sort(key=lambda x: x[1], reverse=True)
        
        # Pick from top 30% complex questions
        top_count = max(1, len(available_questions) // 3)
        selected_idx = random.choice([idx for idx, _ in available_questions[:top_count]])
        
        self.used_question_indices.add(selected_idx)
        return self.questions[selected_idx]
    
    def search_similar_questions(
        self, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for questions similar to a query
        Args:
            query: Search query text
            top_k: Number of results to return
        Returns:
            List of dicts with question and metadata
        """
        # Generate query embedding
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.questions):  # Valid index
                results.append({
                    'question': self.questions[idx],
                    'distance': float(dist),
                    'metadata': self.metadata[idx] if idx < len(self.metadata) else {}
                })
        
        return results
    
    def get_diverse_questions(self, count: int = 5) -> List[str]:
        """
        Get diverse questions ensuring variety
        Uses clustering or sampling to ensure diversity
        """
        if count > len(self.questions):
            count = len(self.questions)
        
        # Simple approach: divide question space into segments
        segment_size = len(self.questions) // count
        selected_questions = []
        
        for i in range(count):
            start_idx = i * segment_size
            end_idx = start_idx + segment_size
            
            # Pick random from this segment
            segment_indices = list(range(start_idx, min(end_idx, len(self.questions))))
            if segment_indices:
                # Filter out used questions
                available = [idx for idx in segment_indices 
                           if idx not in self.used_question_indices]
                
                if not available:
                    available = segment_indices
                
                selected_idx = random.choice(available)
                selected_questions.append(self.questions[selected_idx])
                self.used_question_indices.add(selected_idx)
        
        return selected_questions
    
    def reset_session(self):
        """Reset used questions tracking for new interview session"""
        self.used_question_indices.clear()
    
    def get_total_questions(self) -> int:
        """Get total number of questions available"""
        return len(self.questions)


def get_question_for_topic(
    topic: str, 
    question_number: int,
    difficulty: str = "medium"
) -> str:
    """
    Convenience function to get a question for a topic
    Args:
        topic: 'sql' or 'python'
        question_number: Question number (1-5)
        difficulty: 'easy', 'medium', 'hard'
    Returns:
        A question string
    """
    # Map question number to difficulty
    if question_number == 1:
        difficulty = "easy"
    elif question_number in [2, 3]:
        difficulty = "medium"
    else:
        difficulty = "hard"
    
    try:
        rag = SingleTopicRAG(topic)
        question = rag.get_question_by_difficulty(difficulty, question_number)
        return question
    except Exception as e:
        # Fallback to AI generation if RAG fails
        print(f"Error in RAG: {e}, falling back to AI generation")
        return None
