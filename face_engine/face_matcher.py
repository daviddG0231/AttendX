"""
AttendX Face Matching Module

Uses FAISS for efficient similarity search among registered student embeddings.
"""

import numpy as np
import json
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class FaceMatcher:
    """
    Efficient face matching using FAISS (Facebook AI Similarity Search).
    
    Maintains an index of registered student face embeddings and performs
    fast nearest-neighbor search for real-time face identification.
    """
    
    def __init__(self, embedding_dim: int = 512, threshold: float = 0.4):
        """
        Initialize FAISS-based face matcher.
        
        Args:
            embedding_dim: Dimension of face embeddings (512 for ArcFace)
            threshold: Maximum cosine distance for a match (lower = stricter)
        """
        self.embedding_dim = embedding_dim
        self.threshold = threshold
        self.index = None
        self.student_ids: List[str] = []
        self.student_names: Dict[str, str] = {}
        self.embeddings: List[np.ndarray] = []
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Create empty FAISS index."""
        try:
            import faiss
            
            # Use IndexFlatIP for cosine similarity (inner product on normalized vectors)
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            logger.info(f"✅ FAISS index initialized (dim={self.embedding_dim})")
            
        except ImportError:
            logger.error("FAISS not installed. Run: pip install faiss-cpu")
            raise
    
    def register_student(self, student_id: str, student_name: str, 
                        embeddings: List[np.ndarray]) -> bool:
        """
        Register a student's face embeddings in the index.
        
        Multiple embeddings per student improve recognition accuracy
        (minimum 5 as per project requirements).
        
        Args:
            student_id: Unique student identifier
            student_name: Student's display name
            embeddings: List of 512-d face embeddings (min 5 recommended)
            
        Returns:
            True if registration successful
        """
        if not embeddings:
            logger.warning(f"No embeddings provided for student {student_id}")
            return False
        
        try:
            # Average the embeddings for a more robust representation
            avg_embedding = np.mean(embeddings, axis=0).astype(np.float32)
            avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)  # Normalize
            
            # Add to FAISS index
            self.index.add(avg_embedding.reshape(1, -1))
            
            # Store mapping
            self.student_ids.append(student_id)
            self.student_names[student_id] = student_name
            self.embeddings.append(avg_embedding)
            
            logger.info(f"✅ Registered student: {student_name} ({student_id}) "
                       f"with {len(embeddings)} embeddings")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register student {student_id}: {e}")
            return False
    
    def identify(self, embedding: np.ndarray, top_k: int = 1) -> List[Tuple[str, str, float]]:
        """
        Identify a face by searching the FAISS index.
        
        Args:
            embedding: 512-d face embedding to identify
            top_k: Number of top matches to return
            
        Returns:
            List of (student_id, student_name, similarity_score) tuples.
            Empty list if no match found above threshold.
        """
        if self.index.ntotal == 0:
            return []
        
        try:
            # Normalize query embedding
            query = embedding.astype(np.float32).reshape(1, -1)
            query = query / np.linalg.norm(query)
            
            # Search FAISS index
            similarities, indices = self.index.search(query, min(top_k, self.index.ntotal))
            
            results = []
            for sim, idx in zip(similarities[0], indices[0]):
                if idx < 0 or idx >= len(self.student_ids):
                    continue
                
                # Convert cosine similarity to distance
                # Similarity: 1.0 = identical, 0.0 = orthogonal
                distance = 1.0 - sim
                
                if distance <= self.threshold:
                    student_id = self.student_ids[idx]
                    student_name = self.student_names.get(student_id, "Unknown")
                    results.append((student_id, student_name, float(sim)))
            
            return results
            
        except Exception as e:
            logger.error(f"Face identification failed: {e}")
            return []
    
    def identify_batch(self, embeddings: List[np.ndarray]) -> List[List[Tuple[str, str, float]]]:
        """
        Identify multiple faces in batch for efficiency.
        
        Args:
            embeddings: List of face embeddings
            
        Returns:
            List of identification results for each embedding
        """
        return [self.identify(emb) for emb in embeddings if emb is not None]
    
    def remove_student(self, student_id: str) -> bool:
        """
        Remove a student from the index.
        
        Note: FAISS doesn't support direct removal, so we rebuild the index.
        """
        if student_id not in self.student_ids:
            return False
        
        try:
            import faiss
            
            idx = self.student_ids.index(student_id)
            
            # Remove from lists
            self.student_ids.pop(idx)
            self.student_names.pop(student_id, None)
            self.embeddings.pop(idx)
            
            # Rebuild FAISS index
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            if self.embeddings:
                embeddings_array = np.array(self.embeddings).astype(np.float32)
                self.index.add(embeddings_array)
            
            logger.info(f"✅ Removed student {student_id} from index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove student {student_id}: {e}")
            return False
    
    def save_index(self, directory: str = "data"):
        """Save FAISS index and metadata to disk."""
        try:
            import faiss
            
            os.makedirs(directory, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, os.path.join(directory, "faiss_index.bin"))
            
            # Save embeddings
            if self.embeddings:
                np.save(os.path.join(directory, "embeddings.npy"), 
                       np.array(self.embeddings))
            
            # Save student mappings
            metadata = {
                'student_ids': self.student_ids,
                'student_names': self.student_names
            }
            with open(os.path.join(directory, "student_ids.json"), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Index saved to {directory}/ "
                       f"({self.index.ntotal} students)")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def load_index(self, directory: str = "data") -> bool:
        """Load FAISS index and metadata from disk."""
        try:
            import faiss
            
            index_path = os.path.join(directory, "faiss_index.bin")
            metadata_path = os.path.join(directory, "student_ids.json")
            embeddings_path = os.path.join(directory, "embeddings.npy")
            
            if not os.path.exists(index_path):
                logger.info("No existing index found, starting fresh")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load embeddings
            if os.path.exists(embeddings_path):
                self.embeddings = list(np.load(embeddings_path))
            
            # Load student mappings
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                self.student_ids = metadata['student_ids']
                self.student_names = metadata['student_names']
            
            logger.info(f"✅ Index loaded from {directory}/ "
                       f"({self.index.ntotal} students)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    @property
    def num_registered(self) -> int:
        """Number of registered students."""
        return self.index.ntotal if self.index else 0
