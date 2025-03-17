import os 
import uuid
from datetime import datetime
from PIL import Image
import json 
import markdown
import docx


class Document:
    """
    Document class for handling different types of documents.
    Uses a task-based approach where files are processed and then deleted.
    """
    def __init__(self, file_path, file_name, file_type):
        # Generate a unique ID for this document
        self.id = str(uuid.uuid4())
        
        # store file information 
        self.file_path = file_path # Where the file is saved on disk
        self.file_name = file_name # Original name of the file
        self.file_type = file_type # MIME type (e.g., 'text/plain', 'application/pdf')
        
        # Record when this document was uploaded
        self.upload_time = datetime.now()
        
        # Placeholders for content that will be extracted
        self.content = None
        self.extracted_text = None
        
    # Add this import at the top of the file

    def extract_text(self):
        """Extract text content from the document based on its type."""
        try:
            # Check if we need to determine the file type from extension
            if self.file_type == 'application/octet-stream':
                # Try to determine type from file extension
                if self.file_name.endswith('.md') or self.file_name.endswith('.markdown'):
                    self.file_type = 'text/markdown'
                elif self.file_name.endswith('.txt'):
                    self.file_type = 'text/plain'
                elif self.file_name.endswith('.json'):
                    self.file_type = 'application/json'
                elif self.file_name.endswith('.docx'):
                    self.file_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            
            # For text-based files (plain text, markdown, etc.)
            if self.file_type in ['text/plain', 'text/markdown']:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    self.extracted_text = file.read()
                    
            # For JSON files
            elif self.file_type == 'application/json':
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # Convert JSON to a formatted string
                    self.extracted_text = json.dumps(data, indent=2)
            
            # For Word (docx) files
            elif self.file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or self.file_name.endswith('.docx'):
                doc = docx.Document(self.file_path)
                full_text = []
                for para in doc.paragraphs:
                    full_text.append(para.text)
                self.extracted_text = '\n'.join(full_text)
                    
            # For image files
            elif self.file_type.startswith('image/'):
                # For images, we'll rely on the LLM to describe the image
                self.extracted_text = f"[Image: {self.file_name}]"
                
            # For unsupported file types
            else:
                self.extracted_text = f"Unsupported file type: {self.file_type}"
                
            return self.extracted_text
            
        except Exception as e:
            # Handle any errors during extraction
            self.extracted_text = f"Error extracting text: {str(e)}"
            return self.extracted_text


    
    def cleanup(self):
        """Delete the document file from disk."""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            return True
        return False
    
    def to_dict(self):
        """Convert document to dictionary for serialization."""
        return {
            "id": self.id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "upload_time": self.upload_time.isoformat(), 
            "has_extracted_text": self.extracted_text is not None
        }
        