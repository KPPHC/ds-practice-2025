import json
import os
import sys

    # This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
transaction_verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, transaction_verification_grpc_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

import grpc
from concurrent import futures

def luhn_algorithm(card_number):
    isSecond = False
    n_digits = len(card_number)
    sum_digits = 0

    for i in range(n_digits - 1, -1, -1):
        d = ord(card_number[i]) - ord('0')
        if (isSecond == True):
            d = d*2
        sum_digits += d // 10
        sum_digits += d % 10

        isSecond = not isSecond

    if (sum_digits % 10 == 0):
        return True
    else:
        return False

# Create a class to define the server functions
class TransactionVerificationService(transaction_verification_grpc.TransactionVerificationServiceServicer):    
    def TransactionVerification(self, request, context):        
        for book in request.user_books:
            print("Received bookId {} in quantity: {}".format(book.bookId, book.book_quantity))
        
        card_number = request.card_number
        user_name = request.user_name
        user_email = request.user_email
        card_expiry = request.card_expiry
        card_cvv = request.card_cvv
        billing_street = request.billing_street
        billing_city = request.billing_city
        billing_state = request.billing_state
        billing_zip = request.billing_zip
        shipping_method = request.shipping_method
        terms_accepted = request.terms_accepted

        # Check for empty fields
        fields = {
            "card_number": card_number,
            "user_name": user_name,
            "user_email": user_email,
            "card_expiry": card_expiry,
            "card_cvv": card_cvv,
            "billing_street": billing_street,
            "billing_city": billing_city,
            "billing_state": billing_state,
            "billing_zip": billing_zip,
            "shipping_method": shipping_method,
            "terms_accepted": terms_accepted
        }

        result = luhn_algorithm(request.card_number)

        response = transaction_verification.TransactionVerificationResponse(
            is_valid=True,
            reason="Transaction verification passed"
        )

        
        reasons = []

        if not terms_accepted:
            reasons.append("Terms must be accepted")

        for field_name, field_value in fields.items():
            if not field_value:
                reasons.append(f"{field_name} is empty")

        if not result:
            reasons.append("Credit card number is invalid")

        if reasons:
            response = transaction_verification.TransactionVerificationResponse(
                is_valid=False,
                reason="; ".join(reasons)
            )
        else:
            response = transaction_verification.TransactionVerificationResponse(
                is_valid=True,
                reason="Transaction verification passed"
            )

        return response

        # print("Received credit card number: {}".format(request.card_number))
        # print("Received user_name: {}".format(request.user_name))
        # print("Received user_email: {}".format(request.user_email))
        # print("Received card_expiry: {}".format(request.card_expiry))
        # print("Received card_cvv: {}".format(request.card_cvv))
        # print("Received billing_street: {}".format(request.billing_street))
        # print("Received billing_city: {}".format(request.billing_city))
        # print("Received billing_state: {}".format(request.billing_state))
        # print("Received billing_zip: {}".format(request.billing_zip))
        # print("Received shipping_method: {}".format(request.shipping_method))
        # print("Received terms_accepted: {}".format(request.terms_accepted))
        

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    transaction_verification_grpc.add_TransactionVerificationServiceServicer_to_server(TransactionVerificationService(), server)
    # Listen on port 50052
    port = "50052"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("TransactionVerificationService started. Listening on port 50052.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()