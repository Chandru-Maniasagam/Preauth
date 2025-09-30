"""
Firestore client for RCM SaaS Application
"""

from google.cloud import firestore
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime

from app.config import DatabaseConfig


class FirestoreClient:
    """Firestore client for database operations"""
    
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collections = DatabaseConfig.COLLECTIONS
    
    def create_document(self, collection: str, document_id: str = None, data: Dict[str, Any] = None) -> str:
        """Create a new document in Firestore"""
        try:
            collection_ref = self.db.collection(self.collections[collection])
            
            if document_id:
                doc_ref = collection_ref.document(document_id)
                doc_ref.set(data or {})
                return document_id
            else:
                doc_ref = collection_ref.add(data or {})
                return doc_ref[1].id
                
        except Exception as e:
            logging.error(f"Error creating document in {collection}: {str(e)}")
            raise
    
    def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore"""
        try:
            doc_ref = self.db.collection(self.collections[collection]).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logging.error(f"Error getting document from {collection}: {str(e)}")
            raise
    
    def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Update a document in Firestore"""
        try:
            doc_ref = self.db.collection(self.collections[collection]).document(document_id)
            doc_ref.update(data)
            return True
            
        except Exception as e:
            logging.error(f"Error updating document in {collection}: {str(e)}")
            raise
    
    def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document from Firestore"""
        try:
            doc_ref = self.db.collection(self.collections[collection]).document(document_id)
            doc_ref.delete()
            return True
            
        except Exception as e:
            logging.error(f"Error deleting document from {collection}: {str(e)}")
            raise
    
    def query_collection(self, collection: str, filters: List[tuple] = None, 
                        order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Query a collection with filters"""
        try:
            query = self.db.collection(self.collections[collection])
            
            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            logging.error(f"Error querying collection {collection}: {str(e)}")
            raise
    
    def batch_write(self, operations: List[Dict[str, Any]]) -> bool:
        """Perform batch write operations"""
        try:
            batch = self.db.batch()
            
            for operation in operations:
                op_type = operation.get('type')
                collection = operation.get('collection')
                document_id = operation.get('document_id')
                data = operation.get('data', {})
                
                doc_ref = self.db.collection(self.collections[collection]).document(document_id)
                
                if op_type == 'create':
                    batch.set(doc_ref, data)
                elif op_type == 'update':
                    batch.update(doc_ref, data)
                elif op_type == 'delete':
                    batch.delete(doc_ref)
            
            batch.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error in batch write: {str(e)}")
            raise
