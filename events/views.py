from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
from .forms import EventRegistrationForm
import pytz
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from events.models import MpesaTransaction
import logging
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView

# Event registration view

def register_event_view(request):
    if request.method == "POST":
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            # Saves the form data if valid
            form.save()
            phone_number = form.cleaned_data['phone_number']  # Get phone number from the  form
            amount = 1  # The set amount,  i will change this later
            stk_push_success = initiate_mpesa_stk_push(phone_number,amount)

            # Redirect to the thank you page if the STK push is successful
            if stk_push_success:
                return redirect('events:thank_you')
            else:
                # Error message if STK push fails
                messages.error(request, "Payment failed. Please try again.")
                return render(request, 'register_event.html', {'form': form})
    else:
        form = EventRegistrationForm()

    return render(request, 'register_event.html', {'form': form})

def thank_you_view(request):
    return render(request, 'thank_you.html')



def generate_password(shortcode, passkey, timestamp):
    password_string = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(password_string.encode('utf-8')).decode('utf-8')


def get_access_token():
    consumer_key = 'WumSttSJpeqk2HONJJtTg0w1oRaPVwQZF22HpRI8VAbVZx5K'
    consumer_secret = 'MEtFVM2mp9O2WKAT8GBI3IKA6Vn88AJ7nytMgTblsw9RJtT1WwGcllftp0uGjehH'
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{consumer_key}:{consumer_secret}'.encode()).decode()}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP codes >= 400
        data = response.json()
        if "access_token" in data:
            return data["access_token"]
        else:
            raise ValueError("Access token not found in response")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access token: {e}")
        raise
    except ValueError as ve:
        print(f"Unexpected response format: {ve}")
        raise



def initiate_mpesa_stk_push(phone_number,amount):
    try:
        # Mpesa credentials
        shortcode = '174379'
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        amount = amount
        phone_number = phone_number
        callback_url = 'https://3add-41-212-105-164.ngrok-free.app/callback/'
        # timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = generate_password(shortcode, passkey, timestamp)

        # Payload for the API
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(amount),
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": "TestAccount",
            "TransactionDesc": "Payment for service"
        }
        
        access_token = get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        logger.debug("Initiating MPesa STK Push")
        logger.debug(f"URL: {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {payload}")

        # Make the API request
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        # Log response details
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Data: {response.text}")

        if response.status_code == 200:
            response_data = response.json()
            logger.info("Payment request successful.")
            return JsonResponse(response_data)
        else:
            logger.error("Payment request failed.")
            return JsonResponse(
                {"error": "Payment request failed", "details": response.json()},
                status=response.status_code
            )
    except requests.exceptions.RequestException as e:
        logger.exception("A network error occurred.")
        return JsonResponse({"error": "A network error occurred", "details": str(e)}, status=500)
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        return JsonResponse({"error": "An unexpected error occurred", "details": str(e)}, status=500)


transaction_date = now()

logger = logging.getLogger(__name__)

class MpesaExpressCallback(APIView):
    """
    Handles the MPesa Express Callback from Safaricom
    """

    def post(self, request, *args, **kwargs):
        try:
            logger.debug(f"Callback data received: {request.data}")
            
            callback_body = request.data.get("Body", {}).get("stkCallback", {})
            if not callback_body:
                return Response({"error": "Invalid callback data"}, status=HTTP_400_BAD_REQUEST)

            # Extract fields
            checkout_request_id = callback_body.get("CheckoutRequestID", "")
            merchant_request_id = callback_body.get("MerchantRequestID", "")
            result_code = callback_body.get("ResultCode", 1)  # Default to error code
            result_desc = callback_body.get("ResultDesc", "Unknown error")
            
            # Process metadata
            metadata = callback_body.get("CallbackMetadata", {}).get("Item", [])
            amount, receipt_number, phone_number, transaction_date = None, None, None, None

            for item in metadata:
                if item["Name"] == "Amount":
                    amount = item["Value"]
                elif item["Name"] == "MpesaReceiptNumber":
                    receipt_number = item["Value"]
                elif item["Name"] == "PhoneNumber":
                    phone_number = item["Value"]
                elif item["Name"] == "TransactionDate":
                    transaction_date = item["Value"]

            # Convert transaction date
            if transaction_date:
                transaction_datetime = datetime.strptime(
                    str(transaction_date), "%Y%m%d%H%M%S"
                )
                aware_transaction_datetime = pytz.utc.localize(transaction_datetime)
            else:
                aware_transaction_datetime = None

            # Log extracted data
            logger.info(f"CheckoutRequestID: {checkout_request_id}")
            logger.info(f"MpesaReceiptNumber: {receipt_number}")

            # Save to database
            MpesaTransaction.objects.create(
                CheckoutRequestID=checkout_request_id,
                MerchantRequestID=merchant_request_id,
                ResultCode=result_code,
                ResultDesc=result_desc,
                Amount=amount,
                MpesaReceiptNumber=receipt_number,
                TransactionDate=aware_transaction_datetime,
                PhoneNumber=phone_number,
            )

            return Response({"status": "success", "message": "Callback handled successfully"}, status=HTTP_200_OK)

        except Exception as e:
            logger.exception("Error processing MPesa callback.")
            return Response({"error": "An error occurred", "details": str(e)}, status=HTTP_400_BAD_REQUEST)