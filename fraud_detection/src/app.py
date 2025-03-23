import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

import grpc
from concurrent import futures
import joblib

model = joblib.load('fraud_model2.pkl')

# Create a class to define the server functions, derived from
# fraud_detection_pb2_grpc.HelloServiceServicer
class FraudDetectionService(fraud_detection_grpc.FraudDetectionServiceServicer):
    # Create an RPC function to say hello
    def FraudDetection(self, request, context):
        try:
            features = [[float(request.card_number), float(request.order_amount)]]
            prediction = model.predict(features)

            is_fraud = bool(prediction[0])
        
        except Exception as e:
            print("Error during prection: ", e)
            is_fraud = True # Handle errors as fraudulent
        
        response = fraud_detection.FraudDetectionResponse()
        response.is_fraud = is_fraud
        print("Fraud detection result:", is_fraud)
        return response
        

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    fraud_detection_grpc.add_FraudDetectionServiceServicer_to_server(FraudDetectionService(), server)
    # Listen on port 50051
    port = "50051"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("FraudDetection started. Listening on port 50051.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()