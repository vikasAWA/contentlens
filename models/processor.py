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
        
    def process_document(self, document, instructions):
        """
        Process a document according to the given instructions.
        
        Args:
            document (Document): The document to process
            instructions (str): Instructions for processing
            
        Returns:
            str: The processed result in markdown format
        """
        if not document.extracted_text:
            document.extract_text()
            
        # Creating a prompt for the AI model
        prompt = f"""
        Instructions: {instructions}
        
        Document content:
        {document.extracted_text}
        
        Please process according to the instructions and return the result in markdown format.
        """
        
        response = self.model.generate_content(prompt)
        
        return response.text