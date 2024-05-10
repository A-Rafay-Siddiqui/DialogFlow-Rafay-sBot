from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Extract order ID from the webhook request
        req_data = request.get_json()
        order_id = req_data.get('queryResult', {}).get('parameters', {}).get('number')
        
        # Make POST request to fetch shipment date
        shipment_api_endpoint = 'https://orderstatusapi-dot-organization-project-311520.uc.r.appspot.com/api/getOrderStatus'
        response = requests.post(shipment_api_endpoint, json={'orderId': order_id})
        
        # Check if the request was successful
        if response.ok:
            # Extract shipment date from response and convert format
            shipment_date_iso = response.json()['shipmentDate']
            shipment_date_human_readable = datetime.strptime(shipment_date_iso, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%A, %d %b %Y')
            
            # Construct webhook response
            webhook_response = {
                'fulfillmentMessages': [
                    {
                        'text': {
                            'text': [f'Your order {order_id} will be shipped on {shipment_date_human_readable}']
                        }
                    }
                ]
            }
            
            # Send webhook response
            return jsonify(webhook_response)
        else:
            # Return an error response if the request fails
            return jsonify({'error': 'Failed to fetch shipment date'}), 500
    except Exception as e:
        print('Error processing webhook request:', e)
        # Return an error response if something goes wrong
        return jsonify({'error': 'An error occurred while processing your request'}), 500

if __name__ == '__main__':
    app.run(debug=True)
