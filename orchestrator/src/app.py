import sys
import os
import logging
logging.basicConfig(level=logging.INFO)

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

import grpc

def call_fraud_detection(card_number, order_amount):
    # Establish a connection with the fraud-detection gRPC service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        # Call the service through the stub object.
        request_obj = fraud_detection.FraudDetectionRequest(card_number=card_number, order_amount=order_amount)
        response = stub.FraudDetection(request_obj)
    return response.is_fraud


suggestions_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, suggestions_grpc_path)
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

def get_suggestions(user_books):
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionsServiceStub(channel)
        book_messages = []
        for book in user_books:
            # Only extract the keys defined in the proto.
            book_msg = suggestions.Book(
                bookId=book.get('bookId', ''),
                title=book.get('title', ''),
                author=book.get('author', '')
            )
            book_messages.append(book_msg)
        response = stub.Suggestions(suggestions.SuggestionsRequest(user_books=book_messages))
    suggested_books = [
        {"bookId": book.bookId, "title": book.title, "author": book.author}
        for book in response.suggested_books
        ]
    return suggested_books

transaction_verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, transaction_verification_grpc_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

def verify_transaction(transaction_data):
    book_messages = []
    for book in transaction_data.get('items',[]):
            # Only extract the keys defined in the proto.
            book_msg = transaction_verification.Book(
                bookId=book.get('bookId', ''),
                book_quantity = str(book.get('quantity', 1))
            )
            book_messages.append(book_msg)
    
    # Create the request object.
    request = transaction_verification.TransactionVerificationRequest(
            user_books = book_messages,
            user_name=transaction_data.get('user', {}).get('name', ''),
            user_email=transaction_data.get('user', {}).get('contact', ''),
            card_number=transaction_data.get('creditCard', {}).get('number', ''),
            card_expiry=transaction_data.get('creditCard', {}).get('expirationDate', ''),
            card_cvv=transaction_data.get('creditCard', {}).get('cvv', ''),
            billing_street=transaction_data.get('billingAddress', {}).get('street', ''),
            billing_city=transaction_data.get('billingAddress', {}).get('city', ''),
            billing_state=transaction_data.get('billingAddress', {}).get('state', ''),
            billing_zip=transaction_data.get('billingAddress', {}).get('zip', ''),
            shipping_method=transaction_data.get('shippingMethod', ''),
            #gift_wrapping=transaction_data.get('giftWrapping', False),
            terms_accepted=transaction_data.get('termsAccepted', False)
            #user_comment=transaction_data.get('userComment', '')
        )
    
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
        
        # Call the service through the stub object.
        response = stub.TransactionVerification(request)
    return response.is_valid

# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request
from flask_cors import CORS
import json

# Create a simple Flask app.
app = Flask(__name__)
# Enable CORS for the app.
CORS(app, resources={r'/*': {'origins': '*'}})

# Define a GET endpoint.
@app.route('/', methods=['GET'])
def index():

    # Book suggestions
    user_books = [
         {"title": "Metro 2033", "author": "Dmitry Glukhovsky", "quantity": 1},
         {"title": "Roadside Picnic", "author": "Arkady Strugatsky and Boris Strugatsky", "quantity": 2}
     ]
    
    #suggestions = get_suggestions(user_books)
    # I should have a list of books that the user has bought
    
    # Return the response.
    return response

@app.route('/checkout', methods=['POST'])
def checkout():
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """

    # Reads request data from frontend as JSON
    request_data = json.loads(request.data)
    # user_books = request_data.get('items')
    # user_data = request_data.get('user')
    # credit_card_data = request_data.get('creditCard')
    # billing_address = request_data.get('billingAddress')
    # shipping_method = request_data.get('shippingMethod')
    # gift_wrapping = request_data.get('giftWrapping')
    # terms_accepted = request_data.get('termsAccepted')
    # user_comment = request_data.get('userComment') 
    
    #transaction_data = [user_books, user_data, credit_card_data, billing_address, shipping_method, gift_wrapping, terms_accepted, user_comment]

    transaction_data = {
        "user": request_data.get("user"),
        "creditCard": request_data.get("creditCard"),
        "billingAddress": request_data.get("billingAddress"),
        "shippingMethod": request_data.get("shippingMethod"),
        "giftWrapping": request_data.get("giftWrapping"),
        "termsAccepted": request_data.get("termsAccepted"),
        "userComment": request_data.get("userComment"),
        "items": request_data.get("items"),
    }

    import uuid
    try:
        orderID = str(uuid.uuid4())
        print(f"Order ID: {orderID}")
        logging.info("Received transaction data", extra={"orderID": orderID, "transaction_data": transaction_data})
        # Print request object data
        #print("Transaction Data:", transaction_data)



        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            logging.info("Starting thread for FraudDetection")
            future_fraud = executor.submit(call_fraud_detection, transaction_data.get('creditCard', {}).get('number', ''), transaction_data.get('creditCard', {}).get('order_amount', ''))
            logging.info("Starting thread for Suggestions")
            future_suggest = executor.submit(get_suggestions, transaction_data.get('items', {}))
            logging.info("Starting thread for TransactionVerification")
            future_verification = executor.submit(verify_transaction, transaction_data)
            
            
            greeting = future_fraud.result()
            logging.info("Thread for FraudDetection finished")
            suggestions = future_suggest.result()
            logging.info("Thread for Suggestions finished")
            transaction_verification = future_verification.result()
            logging.info("Thread for TransactionVerification finished")
        

        order_status_response = {
            'orderId': orderID,
            'status': 'Order Approved' if transaction_verification else 'Order Denied',
            #'status': transaction_verification,
            'suggestedBooks': suggestions
        }
        
        logging.info("Checkout completed", extra={"order_status_response": order_status_response})
        return order_status_response
    
    except Exception as e:
        logging.exception("Checkout endpoint failed")
        return {"error": str(e)}


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
