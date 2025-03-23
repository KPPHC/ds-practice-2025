import json
import os
import sys
import time
from google import genai
import logging
logging.basicConfig(level=logging.INFO)



def get_llm_response(prompt, max_retries=3, delay=2):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # The api key environment variable needs to be added to docker-compose.yaml to work.
    client = genai.Client(api_key=GEMINI_API_KEY)
    #client = genai.Client(api_key=10)
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response
        except Exception as e:
            print(f"Attempt {attempt+1} failed with error: {e}")
            time.sleep(delay * (attempt + 1))
    raise Exception("LLM API failed after several retries")
    
# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
suggestions_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, suggestions_grpc_path)
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

import grpc
from concurrent import futures

# Create a class to define the server functions
class SuggestionsService(suggestions_grpc.SuggestionsServiceServicer):    
    def Suggestions(self, request, context):        
        
        logging.info("Received request with {} books".format(len(request.user_books)))
        
        books_str = ", ".join([f"{book.title} by {book.author}" for book in request.user_books])
        prompt = f"""
            Provide 5 book suggestions for a buyer who has purchased: {books_str}
            Return only a JSON array of dictionaries with keys 'bookId', 'title', and 'author'.
            Example format:
            [
                {{"bookId": "123", "title": "Book Title", "author": "Author Name"}},
                {{"bookId": "456", "title": "Another Book", "author": "Another Author"}}
            ]
         
            """
        # Generate suggestions, exponential backoff with max_retries=3 and delay=2
        try:
            response = get_llm_response(prompt)
        except Exception as e:
            context.set_details(f"Error generating suggestions: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return suggestions.SuggestionsResponse()

        # Clean up the response text - remove markdown code block indicators
        cleaned_response = response.text.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]  # Remove ```
        cleaned_response = cleaned_response.strip()  # Remove any extra whitespace

        #Cleaned response mapped as dictionary
        try:
            suggestions_list = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            # Handle JSON parse errors appropriately.
            context.set_details(f"JSON parse error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return suggestions.SuggestionsResponse()
        
        #Response object called, populated and returned
        response  = suggestions.SuggestionsResponse()
        for suggestion in suggestions_list:
            book_msg = suggestions.Book(
                bookId=suggestion.get("bookId", ""),
                title=suggestion.get("title", ""),
                author=suggestion.get("author", "")
            )
            response.suggested_books.append(book_msg)
        
        logging.info("Returning {} suggestions".format(len(response.suggested_books)))
        return response


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    suggestions_grpc.add_SuggestionsServiceServicer_to_server(SuggestionsService(), server)
    # Listen on port 50053
    port = "50053"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("SuggestionsService started. Listening on port 50053.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()