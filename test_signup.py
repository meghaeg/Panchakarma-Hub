#!/usr/bin/env python3

import requests
import json
import sys

def test_signup():
    url = "http://localhost:5000/auth/signup"
    
    # Test patient signup with exact form data
    patient_data = {
        "role": "patient",
        "name": "Mothi Balaaji",
        "aadhar": "605457658021",
        "age": 20,
        "dob": "2005-09-03",
        "email": "mothibalaaji@gmail.com",
        "phone": "9360925952",
        "address": "Erode",
        "blood_group": "AB+",
        "health_issues": "Wheezing",
        "medications": "Inhaler",
        "password": "mothi123"
    }
    
    print("Testing signup endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(patient_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=patient_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Success: {result.get('success')}")
                print(f"Message: {result.get('message')}")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
        else:
            print(f"Error: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        print("Is the Flask server running on localhost:5000?")
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_signup()
