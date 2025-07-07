import google.generativeai as genai
genai.configure(api_key="AIzaSyD1iUaHZjJuB7fVP-Z_KwIc-5E87PLNZCw")

model = genai.GenerativeModel("gemini-2.5-pro")
response = model.generate_content("Explain what fatigue means in medical terms.")
print(response.text)
