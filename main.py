from fasthtml.common import *
from monsterui.all import *
import os 
from models import Document, Processor
import uuid
import markdown
import asyncio
from starlette.responses import RedirectResponse
from starlette.background import BackgroundTask


os.makedirs('uploads', exist_ok=True)
os.makedirs('downloads', exist_ok=True)


app, rt = fast_app(
    hdrs=(
        Theme.blue.headers(),  # Already blue-based, but we'll enhance it
        Link(rel="stylesheet", href="/static/css/custom.css", type="text/css"), 
        NotStr("""
        <a href="https://github.com/vikasAWA" class="github-corner" aria-label="View source on GitHub">
          <svg width="80" height="80" viewBox="0 0 250 250" style="fill:#151513; color:#fff; position: absolute; top: 0; border: 0; right: 0;" aria-hidden="true">
            <path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path>
            <path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path>
            <path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path>
          </svg>
        </a>
        <style>.github-corner:hover .octo-arm{animation:octocat-wave 560ms ease-in-out}@keyframes octocat-wave{0%,100%{transform:rotate(0)}20%,60%{transform:rotate(-25deg)}40%,80%{transform:rotate(10deg)}}@media (max-width:500px){.github-corner:hover .octo-arm{animation:none}.github-corner .octo-arm{animation:octocat-wave 560ms ease-in-out}}</style>
        """)
    ),
    static_path="static"
)

# Add this after your app initialization
@app.middleware("http")
async def check_session_expiry(request, call_next):
    """Clean up files when session expires or page is refreshed."""
    response = await call_next(request)
    
    # If this is a new page load (not an asset request)
    if request.url.path == "/" and request.method == "GET":
        # Clean up any existing documents
        for file_id, doc_info in list(documents.items()):
            result_path = doc_info["result_path"]
            if os.path.exists(result_path):
                os.remove(result_path)
                print(f"Deleted result file on page refresh: {result_path}")
        
        # Clear the documents dictionary
        documents.clear()
    
    return response

def logo():
    return DivLAligned(
        Span("Content", cls="text-center text-3xl font-bold text-white"),
        Span("Lens", cls="font-bold text-gray-700"),
        UkIcon("search", cls="text-blue-500 ml-1"),
        cls="text-2xl"
    )


processor = Processor() # Creating the processor 

# temporary storage
documents = {}

def markdown_to_html(md_text):
    """Convert markdown text to HTML for display."""
    return markdown.markdown(md_text)


# Defining main page 
@rt("/")
def get():
    """Handle GET requests to the home page."""
    return Titled(
        "🔍 ContentLens | AI-Powered Document Insights",
        Container(
            # Hero section with gradient background
            # Add a gradient hero section at the top of your main page
            Section(
                logo(),
                P("See your documents through the lens of AI", 
                cls=(TextT.muted, "text-center mb-6 text-white opacity-90")),
                cls="rounded-lg mt-5 p-8 mb-8 bg-gradient-to-r from-blue-400 to-indigo-700",
                
            ),
            
            # Main content in a card
            Card(
                # Example instructions in a collapsible section
                Div(
                    H4("📝 Example Instructions", cls="font-bold"),
                    Ul(
                        Li("Summarize this document in 3 lines."),
                        Li("Extract the key points as bullet points"),
                        Li("Convert this content to a formal email"),
                        Li("Analyze the sentiment of this text"),
                        Li("Translate this content to Spanish"),
                        Li("What's going on in this image?"),
                        cls=ListT.disc
                    ),
                    cls="mb-6"
                ),
                Div(
                    H4("Privacy Notice:", cls="text-orange-600"),
                    Ul(
                        Li("Uploaded files are deleted immediately after processing"),
                        Li("Results are deleted after download or when you process another document"),
                        Li("All data is automatically deleted when the page is refreshed"),
                        cls=ListT.disc
                    ),
                    cls="mt-4 p-3 border border-orange-200 bg-orange-50 text-gray-800"
                ),
                # Upload form
                Form(
                    method="post",
                    action="/upload",
                    enctype="multipart/form-data"
                )(
                    Fieldset(
                        # File upload with icon
                        Div(
                            H4("Select Document", cls="font-semibold mb-2"),
                            Label(
                                DivLAligned(
                                    UkIcon("file-up", height=6, width=6, cls="theme-accent-color"),
                                    Span("Choose a file", cls="ml-2")
                                ),
                                Input(
                                    type="file", 
                                    name="document", 
                                    required=True,
                                    accept=".txt,.md,.markdown,.json,.docx,image/*",
                                    id="document-input",
                                    onchange="document.getElementById('upload-status').textContent = 'File selected: ' + this.files[0].name; document.getElementById('upload-status').style.display = 'block';",
                                    
                                ),
                                # Add a status element right after the input
                                Div(
                                    id="upload-status",
                                    cls="mt-2 p-2 border border-blue-300 bg-blue-50 text-gray-800 rounded hidden"
                                ),
                                cls="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer"
                            ),
                            P("Supported formats: TXT, MD, JSON, DOCX, and images", cls=TextT.muted),
                            cls="mb-6"
                        ),
                        
                        # Instructions textarea
                        Div(
                            H4("Instructions", cls="font-semibold mb-2"),
                            TextArea(
                                name="instructions", 
                                placeholder="Enter instructions for processing your document...",
                                required=True,
                                rows=5,
                                cls="w-full p-3 border rounded-md"
                            ),
                            cls="mb-6"
                        ),
                    ),
                    

                    # Submit button
                    DivCentered(
                        Button(
                            DivLAligned(UkIcon("wand"), Span("Process Document", cls="ml-2")),
                            type="submit", 
                            cls=(ButtonT.primary, "px-6 py-3")
                        )
                    )
                ),
                
                header=H3("Upload Your Document", cls="text-xl font-bold"),
                cls="max-w-2xl mx-auto"
            ),
            
            # Footer
            Div(
                P("ContentLens • Powered by Gemini AI • Built with FastHTML and MonsterUI", 
                cls=(TextT.muted, "text-center")),
                cls="mt-8"
            ),
            
            cls=ContainerT.xl
        )
    )

@rt("/upload")
async def post(req):
    form = await req.form()
    uploaded_file = form.get("document")
    instructions = form.get("instructions")
    
    if not uploaded_file or not instructions:
        return Titled(
            "Error",
            P("Please provide both a document and instructions"), 
            A("Go Back", href="/", cls=ButtonT.primary)
        )
        
    # Add this file size check
    file_size = len(await uploaded_file.read())
    await uploaded_file.seek(0)  # Reset file pointer after reading
    
    # 10MB limit (adjust as needed)
    if file_size > 10 * 1024 * 1024:  
        return Titled(
            "Error",
            P("File too large. Please upload files smaller than 10MB."),
            A("Go Back", href="/", cls=ButtonT.primary)
        )
        
    file_id = str(uuid.uuid4())
    file_name = uploaded_file.filename
    file_path = f"uploads/{file_id}_{file_name}"
    
    # Saving the file 
    with open(file_path, "wb") as f:
        f.write(await uploaded_file.read())
        
    # Creating Document object
    document = Document(file_path, file_name, uploaded_file.content_type)
    
    try:
        # Extract text from the document
        document.extract_text()
        
        # Process the document with the LLM
        result = processor.process_document(document, instructions)
        
        # Save the result to a file
        result_path = f"downloads/{file_id}_result.md"
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(result)
            
        # Delete the original uploaded file since we don't need it anymore
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
            print(f"Deleted uploaded file after processing: {document.file_path}")
        
        # Store the document and result path for download  
        documents[file_id] = {
            "result_path": result_path,
            "file_name": file_name
        }
        
        # Show the result
        # Show the result (in your post function)
        return Titled(
            "Processing Results",
            Container(
                Section(
                    H1("Processing Complete", cls="text-center text-2xl font-bold"),
                    P("Your document has been processed according to your instructions.", 
                    cls=(TextT.muted, "text-center")),
                    cls=(SectionT.primary, "rounded-lg p-6 mb-6")
                ),
                
                Card(
                    Grid(
                        Div(
                            H4("Document", cls="font-semibold mb-2"),
                            P(file_name, cls="break-all"),
                        ),
                        Div(
                            H4("Instructions", cls="font-semibold mb-2"),
                            P(instructions, cls="break-all"),
                        ),
                        cols=2,
                        gap=4,
                        cls="mb-4"
                    ),
                    
                    Divider(),
                      # Add this notice at the bottom of the card
                    Div(
                        P("Note: Your processed document will be deleted after download or when you start a new process.", 
                        cls=TextT.muted),
                        cls="mt-4 text-center"
                    ),
                    
                    Div(
                        H3("Result:", cls="text-xl font-bold mb-4"),
                        Div(
                            Safe(markdown_to_html(result)), 
                            cls="result-container bg-gray-50 p-4 rounded-md overflow-auto max-h-96 text-gray-800"
                        ),
                        cls="mb-6"
                    ),
                    
                    DivCentered(
                        # In your results page, update the download button
                        A(
                            DivLAligned(UkIcon("download"), "Download Result"),
                            href=f"/download/{file_id}", 
                            cls=(ButtonT.primary, "mr-4"),
                            uk_tooltip="Download now - this file will be deleted afterward"
                        ),
                        # Update your "Process Another" button
                        A(
                            DivLAligned(UkIcon("redo"), "Process Another Document"),
                            href="/process-another",
                            cls=ButtonT.secondary,
                            uk_tooltip="Current results will be deleted",
                            onclick="return confirm('Start a new process? Your current results will be deleted.');"
                        ),
                        cls="space-x-4"
                    ),
                    
                    header=H3("Processing Results", cls="text-xl font-bold"),
                    cls="max-w-4xl mx-auto"
                ),
                
                cls=ContainerT.xl
            )
        )

    except Exception as e:
        # Clean up the uploaded file if there's an error
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Example for an error page
        return Titled(
            "Error",
            Container(
                Card(
                    Div(
                        UkIcon("alert-triangle", height=12, width=12, cls="text-red-500 mx-auto mb-4"),
                        H2("An Error Occurred", cls="text-xl font-bold text-center mb-4"),
                        P(f"Error message: {str(e)}", cls="text-center mb-6"),
                        DivCentered(
                            A("Go Back", href="/", cls=ButtonT.primary)
                        ),
                    ),
                    cls="max-w-md mx-auto p-6"
                ),
                cls=ContainerT.sm
            )
        )

        
@rt("/upload")
def get():
    """Handle GET requests to the upload URL by redirecting to home."""
    return RedirectResponse(url="/", status_code=303)

        
# Add this route to handle downloads

@rt("/download/{file_id}")
async def get(file_id: str):
    """Handle GET requests to download processed results."""
    # Check if the file_id exists in our documents dictionary
    if file_id not in documents:
        return Titled(
            "Error",
            P("Document not found. It may have expired or been deleted."),
            A("Go Back", href="/", cls=ButtonT.primary)
        )
    
    # Get the document info
    doc_info = documents[file_id]
    result_path = doc_info["result_path"]
    file_name = doc_info["file_name"]
    
    # Check if the result file exists
    if not os.path.exists(result_path):
        return Titled(
            "Error",
            P("Result file not found. It may have been deleted."),
            A("Go Back", href="/", cls=ButtonT.primary)
        )
    
    # Create a temporary file with the same content
    temp_file_path = f"downloads/temp_{file_id}.md"
    with open(result_path, "r", encoding="utf-8") as src, open(temp_file_path, "w", encoding="utf-8") as dst:
        dst.write(src.read())
    
    # Delete the original file
    os.remove(result_path)
    print(f"Deleted original result file: {result_path}")
    
    # Remove from memory
    documents.pop(file_id, None)
    print(f"Removed document {file_id} from memory")
    
    # Serve the temporary file
    response = FileResponse(
        temp_file_path,
        filename=f"{file_name}_result.md",
        media_type="text/markdown"
    )
    
    # Set up a background task to delete the temporary file after a few seconds
    async def cleanup_temp():
        await asyncio.sleep(5)  # Wait longer to ensure file is sent
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Deleted temporary file: {temp_file_path}")
    
    response.background = BackgroundTask(cleanup_temp)
    
    return response

@rt("/process-another")
async def get():
    """Handle clicking 'Process Another Document' button."""
    # Clear all documents and their files
    for file_id, doc_info in list(documents.items()):
        result_path = doc_info["result_path"]
        if os.path.exists(result_path):
            os.remove(result_path)
            print(f"Deleted result file when starting new process: {result_path}")
    
    # Clear the documents dictionary
    documents.clear()
    
    # Redirect to home page
    return RedirectResponse(url="/", status_code=303)



serve()