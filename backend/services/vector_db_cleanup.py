"""
Service pour gérer le nettoyage de la base de données vectorielle et des fichiers de connaissances.
"""
import os
import shutil
from pathlib import Path
import json
from typing import List, Dict, Any, Tuple
from services.vector_db import VectorDBService

class VectorDBCleanupService:
    """Service pour gérer le nettoyage de la base de données vectorielle et des fichiers de connaissances."""
    
    def __init__(self, vector_db_service: VectorDBService):
        """Initialize the cleanup service."""
        self.vector_db_service = vector_db_service
        self.knowledge_dir = "./knowledge"
        self.vector_db_dir = "./database/vector_db"
        self.backup_dir = "./database/backups"
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def list_knowledge_files(self) -> List[Dict[str, Any]]:
        """
        List all knowledge files with their metadata.
        
        Returns:
            List of dictionaries with file information
        """
        if not os.path.exists(self.knowledge_dir):
            return []
        
        files_info = []
        
        for root, dirs, files in os.walk(self.knowledge_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.knowledge_dir)
                
                # Get file stats
                stats = os.stat(file_path)
                
                # Determine file type and category
                file_extension = os.path.splitext(file)[1].lower()
                category = "document"
                
                if file.endswith("_transcription.txt"):
                    category = "transcription"
                elif file_extension in [".txt", ".md"]:
                    category = "text"
                elif file_extension in [".pdf", ".docx", ".doc"]:
                    category = "document"
                elif file_extension in [".csv", ".json", ".xml"]:
                    category = "data"
                
                files_info.append({
                    "name": file,
                    "path": relative_path,
                    "full_path": file_path,
                    "extension": file_extension,
                    "size": stats.st_size,
                    "category": category,
                    "modified": stats.st_mtime,
                    "is_dir": False
                })
                
        # Sort by modified date (newest first)
        files_info.sort(key=lambda x: x["modified"], reverse=True)
        
        return files_info
    
    def backup_knowledge_files(self) -> Tuple[bool, str]:
        """
        Create a backup of all knowledge files.
        
        Returns:
            (success, message) tuple
        """
        try:
            import datetime
            import zipfile
            
            # Create timestamp for backup name
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"knowledge_backup_{timestamp}.zip")
            
            # Create zip archive
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.knowledge_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Add the file to the zip with a relative path
                        arcname = os.path.relpath(file_path, os.path.dirname(self.knowledge_dir))
                        zipf.write(file_path, arcname)
            
            return True, f"Backup created successfully at {backup_path}"
        
        except Exception as e:
            import traceback
            print(f"Error creating backup: {e}")
            print(traceback.format_exc())
            return False, f"Error creating backup: {str(e)}"
    
    def delete_knowledge_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Delete a specific knowledge file.
        
        Args:
            file_path: Path to the file to delete (relative to knowledge directory)
            
        Returns:
            (success, message) tuple
        """
        try:
            # Convert to absolute path
            abs_path = os.path.join(self.knowledge_dir, file_path)
            
            # Check if file exists
            if not os.path.exists(abs_path):
                return False, f"File not found: {file_path}"
            
            # Delete the file
            os.remove(abs_path)
            
            # Also delete related metadata files if they exist
            base_name = os.path.splitext(abs_path)[0]
            for ext in ["_metadata.json", ".metadata"]:
                metadata_path = f"{base_name}{ext}"
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
            
            return True, f"File deleted successfully: {file_path}"
        
        except Exception as e:
            import traceback
            print(f"Error deleting file: {e}")
            print(traceback.format_exc())
            return False, f"Error deleting file: {str(e)}"
    
    def delete_files_by_category(self, category: str) -> Tuple[bool, str]:
        """
        Delete all files of a specific category.
        
        Args:
            category: Category of files to delete (e.g., "transcription")
            
        Returns:
            (success, message) tuple
        """
        try:
            files_info = self.list_knowledge_files()
            category_files = [f for f in files_info if f["category"] == category]
            
            if not category_files:
                return False, f"No files found in category: {category}"
            
            deleted_count = 0
            for file_info in category_files:
                success, _ = self.delete_knowledge_file(file_info["path"])
                if success:
                    deleted_count += 1
            
            return True, f"Deleted {deleted_count} files from category: {category}"
        
        except Exception as e:
            import traceback
            print(f"Error deleting files by category: {e}")
            print(traceback.format_exc())
            return False, f"Error deleting files by category: {str(e)}"
    
    def clear_vector_db(self) -> Tuple[bool, str]:
        """
        Clear the vector database without deleting knowledge files.
        
        Returns:
            (success, message) tuple
        """
        try:
            # Check if vector DB directory exists
            if not os.path.exists(self.vector_db_dir):
                return False, "Vector database directory not found"
            
            # Clear vector DB directory
            for item in os.listdir(self.vector_db_dir):
                item_path = os.path.join(self.vector_db_dir, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            
            # Create empty directory structure
            os.makedirs(os.path.join(self.vector_db_dir, "faiss_index"), exist_ok=True)
            
            return True, "Vector database cleared successfully"
        
        except Exception as e:
            import traceback
            print(f"Error clearing vector database: {e}")
            print(traceback.format_exc())
            return False, f"Error clearing vector database: {str(e)}"
    
    def reindex_knowledge(self) -> Tuple[bool, str]:
        """
        Reindex all knowledge files.
        
        Returns:
            (success, message) tuple
        """
        try:
            # Call the reindex method from vector DB service
            success = self.vector_db_service.clear_and_reindex()
            
            if success:
                return True, "Knowledge reindexed successfully"
            else:
                return False, "Failed to reindex knowledge"
        
        except Exception as e:
            import traceback
            print(f"Error reindexing knowledge: {e}")
            print(traceback.format_exc())
            return False, f"Error reindexing knowledge: {str(e)}"
    
    def clear_all_knowledge(self) -> Tuple[bool, str]:
        """
        Clear all knowledge files AND the vector database.
        WARNING: This will delete all knowledge files!
        
        Returns:
            (success, message) tuple
        """
        try:
            # First, backup the knowledge files
            backup_success, backup_message = self.backup_knowledge_files()
            
            if not backup_success:
                return False, f"Failed to backup knowledge files before clearing: {backup_message}"
            
            # Clear the vector database
            self.clear_vector_db()
            
            # Clear knowledge directory
            if os.path.exists(self.knowledge_dir):
                for item in os.listdir(self.knowledge_dir):
                    item_path = os.path.join(self.knowledge_dir, item)
                    # Don't delete directories, just files
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path) and item != "transcriptions":
                        shutil.rmtree(item_path)
                
                # Recreate the transcriptions directory if deleted
                os.makedirs(os.path.join(self.knowledge_dir, "transcriptions"), exist_ok=True)
            
            return True, f"All knowledge files cleared. Backup created: {backup_message}"
        
        except Exception as e:
            import traceback
            print(f"Error clearing all knowledge: {e}")
            print(traceback.format_exc())
            return False, f"Error clearing all knowledge: {str(e)}"