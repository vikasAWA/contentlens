import os 
import google.generativeai as genai 
from dotenv import load_dotenv

load_dotenv()

class Processor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Configure the GEMINI API with our key
        genai.configure(api_key=api_key)
        
        # Initializing the gemini model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    # In models/processor.py
    def process_document(self, document, instructions):
        """Process a document according to the given instructions."""
        if not document.extracted_text:
            document.extract_text()
        
        # For images, use Gemini Pro Vision
        if document.file_type.startswith('image/'):
            try:
                # Initialize the vision model
                vision_model = genai.GenerativeModel('gemini-2.0-flash')
                
                # Create image part
                image_parts = [{"mime_type": document.file_type, "data": open(document.file_path, "rb").read()}]
                
                # Create prompt
                prompt = f"Instructions: {instructions}\n\nAnalyze this image and respond according to the instructions."
                
                # Generate content with image
                response = vision_model.generate_content([prompt, *image_parts])
                return response.text
                
            except Exception as e:
                return f"Error processing image: {str(e)}"
        
        # For text-based documents
        prompt = f"""
        Instructions from user: {instructions}
        
        Document content (from {document.file_name}, type: {document.file_type}):
        
        {document.extracted_text}
        
        Process the above document content according to the user's instructions.
        Format your response in markdown.
        """
        
        response = self.model.generate_content(prompt)
        return response.text


