import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Set up the Google Generative AI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Flask app
app = Flask(__name__)

# Root route for basic check
@app.route('/')
def home():
    return "Welcome to the Medical Chatbot API! Use /get_response for chatbot queries."

# Define a simulated database of doctors
doctors_db = [
    {"name": "Dr. John Smith", "specialty": "Cardiologist", "phone": "+1234567890", "email": "john.smith@hospital.com"},
    {"name": "Dr. Alice Brown", "specialty": "Neurologist", "phone": "+9876543210", "email": "alice.brown@hospital.com"},
    {"name": "Dr. David Lee", "specialty": "Orthopedic", "phone": "+1928374650", "email": "david.lee@hospital.com"},
    {"name": "Dr. Emily White", "specialty": "Dermatologist", "phone": "+1122334455", "email": "emily.white@hospital.com"},
    {"name": "Dr. Michael Green", "specialty": "Pediatrician", "phone": "+9988776655", "email": "michael.green@hospital.com"}
]

# Disease information, prevention, and remedies
disease_info = {
    "back pain": {
        "information": "Back pain is a common condition that can affect people of all ages.",
        "prevention": "To prevent back pain, practice good posture, avoid heavy lifting, and engage in regular exercise.",
        "remedies": "Over-the-counter pain relievers, rest, and ice or heat therapy may help alleviate back pain."
    },
    "fever": {
        "information": "Fever is a common symptom of many illnesses, ranging from viral infections to more serious conditions.",
        "prevention": "Preventing fever involves proper hygiene, getting vaccinated, and avoiding exposure to infected individuals.",
        "remedies": "Rest, drinking plenty of fluids, and fever-reducing medications like acetaminophen can help manage fever."
    },
    "headache": {
        "information": "Headaches can be caused by stress, dehydration, or underlying medical conditions like migraines.",
        "prevention": "To prevent headaches, stay hydrated, manage stress, and maintain good posture.",
        "remedies": "Over-the-counter pain medications can help relieve headaches. If headaches persist, consult a doctor."
    },
}

# Disease-to-specialty recommendation function
def recommend_doctor(disease):
    disease = disease.lower()
    specialties = {
        "back pain": ["Orthopedic", "Physiotherapist"],
        "fever": ["General Physician", "Infectious Disease Specialist"],
        "headache": ["Neurologist"]
    }

    if disease in specialties:
        specialty_list = specialties[disease]
    else:
        return "Sorry, no specialties found for the disease you mentioned."

    recommended_doctors = [doctor for doctor in doctors_db if doctor["specialty"] in specialty_list]
    if not recommended_doctors:
        return "Sorry, no doctors found for this disease."

    recommendations = []
    for doctor in recommended_doctors:
        recommendations.append(f"Name: {doctor['name']}\nSpecialty: {doctor['specialty']}\nPhone: {doctor['phone']}\nEmail: {doctor['email']}\n")
    return "\n".join(recommendations)

# Function to get a response from Gemini LLM (Gemini Pro model)
def get_gemini_response(question):
    """Get response from Gemini model"""
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    response = chat.send_message(question, stream=True)
    return response

# Define an endpoint for receiving the user query and returning a response
@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get('query', '')
    
    # Look for a disease in the query
    disease_keywords = list(disease_info.keys())
    matching_disease = None
    
    for disease in disease_keywords:
        if disease in user_input.lower():
            matching_disease = disease
            break

    if matching_disease:
        disease_data = disease_info[matching_disease]
        doctor_info = recommend_doctor(matching_disease)

        # Format the response to include disease info, prevention, remedy, and doctor recommendations
        response = {
            "disease_info": disease_data["information"],
            "prevention": disease_data["prevention"],
            "remedies": disease_data["remedies"],
            "doctor_recommendations": doctor_info
        }
    else:
        # Otherwise, use Gemini LLM for a generic response
        response = get_gemini_response(user_input)
        response = {"response": "\n".join([chunk.text for chunk in response])}
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
