"""
Question Bank Processor
Extracts questions from PDF files and creates FAISS vector stores
"""

import os
import pickle
import pypdf
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from django.conf import settings


class QuestionBankProcessor:
    """Process question bank PDFs and create FAISS indexes"""
    
    def __init__(self, topic: str):
        """
        Initialize processor for a specific topic
        Args:
            topic: 'sql' or 'python'
        """
        self.topic = topic.lower()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
        
        # Base paths
        self.base_dir = Path(settings.MEDIA_ROOT)
        self.question_bank_dir = self.base_dir / 'question_banks' / self.topic
        self.vector_store_dir = self.base_dir / 'vector_stores' / self.topic
        
        # Create directories if they don't exist
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.index_path = self.vector_store_dir / 'faiss_index.bin'
        self.questions_path = self.vector_store_dir / 'questions.pkl'
        self.metadata_path = self.vector_store_dir / 'metadata.pkl'
    
    def extract_questions_from_pdf(self, pdf_path: Path) -> List[str]:
        """
        Extract questions from PDF file
        Handles various Q&A formats by extracting only questions
        """
        questions = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
                
                # Split by double newlines or question patterns
                # This helps separate Q&A blocks
                import re
                
                # Pattern to match question numbers: "1.", "Q1.", "Question 1:", etc.
                question_pattern = r'(?:^|\n)(\d+\.|\b[Qq]\d+\.?|\b[Qq]uestion\s+\d+:?)(.+?)(?=\n\d+\.|\n[Qq]\d+|\n[Qq]uestion|\Z)'
                
                matches = re.findall(question_pattern, full_text, re.DOTALL | re.MULTILINE)
                
                for number, content in matches:
                    # Clean the content
                    content = content.strip()
                    
                    # Remove answer sections using multiple patterns
                    answer_patterns = [
                        r'(?i)\s*answer\s*:\s*.*',  # Answer: ...
                        r'(?i)\s*ans\s*:\s*.*',     # Ans: ...
                        r'(?i)\s*a\s*:\s*.*',       # A: ...
                        r'(?i)\s*solution\s*:\s*.*',# Solution: ...
                        r'(?i)\s*sol\s*:\s*.*',     # Sol: ...
                    ]
                    
                    question_only = content
                    for pattern in answer_patterns:
                        # Split at first answer marker
                        parts = re.split(pattern, question_only, maxsplit=1)
                        if len(parts) > 0:
                            question_only = parts[0].strip()
                    
                    # Add question number back
                    full_question = f"{number} {question_only}"
                    
                    # Validate: should end with question mark or be descriptive
                    if len(question_only) > 15:  # Minimum length
                        questions.append(full_question)
                
                # Fallback: if regex fails, use line-by-line approach
                if not questions:
                    lines = full_text.split('\n')
                    current_question = ""
                    skip_until_next_question = False
                    
                    for line in lines:
                        line = line.strip()
                        
                        if not line:
                            continue
                        
                        # Check for answer markers - skip everything after
                        if any(line.lower().startswith(marker) for marker in 
                               ['answer:', 'ans:', 'a:', 'solution:', 'sol:']):
                            if current_question:
                                questions.append(current_question.strip())
                                current_question = ""
                            skip_until_next_question = True
                            continue
                        
                        # Check for question start patterns
                        if re.match(r'^\d+\.|\b[Qq]\d+\.?|\b[Qq]uestion\s+\d+:?', line):
                            if current_question:
                                questions.append(current_question.strip())
                            current_question = line
                            skip_until_next_question = False
                        elif not skip_until_next_question:
                            current_question += " " + line
                    
                    if current_question:
                        questions.append(current_question.strip())
        
        except Exception as e:
            print(f"Error extracting from {pdf_path}: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        # Final cleaning
        cleaned_questions = []
        for q in questions:
            # Final check: remove any answer text that slipped through
            q_lower = q.lower()
            for marker in ['answer:', 'ans:', 'a:', 'solution:', 'sol:']:
                if marker in q_lower:
                    marker_index = q_lower.index(marker)
                    q = q[:marker_index].strip()
                    break
            
            # Only keep substantial questions
            if len(q) > 15 and not q.lower().startswith(('answer', 'ans', 'solution')):
                cleaned_questions.append(q)
        
        return cleaned_questions
    
    def create_vector_store(self):
        """
        Process all PDFs in question bank directory and create FAISS index
        """
        all_questions = []
        metadata = []
        
        # Find all PDFs in the topic directory
        pdf_files = list(self.question_bank_dir.glob('*.pdf'))
        
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in {self.question_bank_dir}")
        
        print(f"Processing {len(pdf_files)} PDF(s) for {self.topic}...")
        
        for pdf_file in pdf_files:
            print(f"  Extracting from: {pdf_file.name}")
            questions = self.extract_questions_from_pdf(pdf_file)
            
            for idx, question in enumerate(questions):
                all_questions.append(question)
                metadata.append({
                    'source': pdf_file.name,
                    'index': idx,
                    'topic': self.topic
                })
        
        if not all_questions:
            raise ValueError(f"No questions extracted from PDFs in {self.question_bank_dir}")
        
        print(f"Extracted {len(all_questions)} questions")
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.model.encode(all_questions, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        print("Creating FAISS index...")
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)
        index.add(embeddings)
        
        # Save everything
        print("Saving to disk...")
        faiss.write_index(index, str(self.index_path))
        
        with open(self.questions_path, 'wb') as f:
            pickle.dump(all_questions, f)
        
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"✅ Vector store created successfully!")
        print(f"   - Index: {self.index_path}")
        print(f"   - Questions: {len(all_questions)}")
        print(f"   - Dimensions: {dimension}")
        
        return len(all_questions)
    
    def verify_vector_store(self) -> Dict:
        """
        Verify that vector store exists and is valid
        Returns: Dict with status and info
        """
        if not self.index_path.exists():
            return {'exists': False, 'error': 'Index file not found'}
        
        if not self.questions_path.exists():
            return {'exists': False, 'error': 'Questions file not found'}
        
        try:
            index = faiss.read_index(str(self.index_path))
            with open(self.questions_path, 'rb') as f:
                questions = pickle.load(f)
            
            return {
                'exists': True,
                'total_questions': len(questions),
                'index_size': index.ntotal,
                'dimensions': index.d,
                'topic': self.topic
            }
        except Exception as e:
            return {'exists': False, 'error': str(e)}


def initialize_all_topics():
    """
    Initialize vector stores for all topics
    """
    topics = ['sql', 'python']
    results = {}
    
    for topic in topics:
        print(f"\n{'='*50}")
        print(f"Processing {topic.upper()}")
        print('='*50)
        
        try:
            processor = QuestionBankProcessor(topic)
            count = processor.create_vector_store()
            results[topic] = {'success': True, 'count': count}
        except Exception as e:
            print(f"❌ Error processing {topic}: {e}")
            results[topic] = {'success': False, 'error': str(e)}
    
    return results
