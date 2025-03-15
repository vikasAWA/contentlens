import os 
import uuid
from datetime import datetime
import PyPDF2
from PIL import Image
import json 
import markdown

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
        
    def extract_text(self):
        """Extract text content from the document based on its type."""
        # For plain text files
        if self.file_type == 'text/plain':
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.extracted_text = file.read()
        
        # For PDF files
        elif self.file_type == 'applicaton/pdf':
            text = ""
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    text += page.extract_text()
            self.extracted_text = text
        
        # For Json files
        elif self.file_type == 'application/json':
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Convert JSON to a formatted string
                self.extracted_text = json.dumps(data, indent=2)
                
        # For Markdown files
        elif self.file_type == 'test/markdown':
            with open(self.file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                self.extracted_text = md_content
                
         # For image files
        elif self.file_type.startswith('image/'):
            # For images, we'll rely on the LLM to describe the image
            self.extracted_text = f"[Image: {self.file_name}]"
            
        # For unsupported file types
        else:
            self.extracted_text = f"Unsupported file type: {self.file_type}"
            
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
        