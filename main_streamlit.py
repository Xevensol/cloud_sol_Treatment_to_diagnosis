import streamlit as st
import re
import os
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import requests

st.markdown(
    """
    <style>
    /* Apply black text color globally */
    body, .stMarkdown, .stText, .stRadio, .stCheckbox, .stSelectbox, .stSlider, .stTextInput, .stNumberInput, .stTextarea, .stFileUploader, .stDateInput, .stTimeInput, .stColorPicker, .stJson, .stMetric, .stDataFrame, .stExpander, .stTable {
        color: black !important;
    }

    /* Apply white background to the button */
    .stButton > button {
        background-color: white !important;
        color: black !important;  /* Set text color to black */
        border: 2px solid black !important;  /* Set border to black */
    }

    /* Prevent background from being overridden */
    .stApp {
        background-color: white !important;
    }

    /* Hover effect for the button */
    .stButton > button:hover {
        background-color: #f0f0f0 !important;  /* Light grey hover effect */
        border-color: black !important;
    }

    </style>
    
    <style>
    /* Center-align the button */
    .center-button {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .stButton {
        display: flex;
        justify-content: center;
        width: 100%;
    }

    /* Styling for the spinner to make it black */
    .stSpinner > div {
        background-color: white !important;
        color: black !important;
    }
    
    </style>
    
    <style>
        .stTextInput input {
            background-color: white;
            border: 2px solid black;
            color: black;
        }
    </style>
    
    """,
    unsafe_allow_html=True
)

# Set up your app's functionality (keeping your original code intact)
openai_api_key = os.getenv('OPENAI_API_KEY')

prompt = """
You are a medical coding validation assistant.
You have knowledge of ICD 10 AM and CPT codes.
Your task is to evaluate the relevance of multiple CPT codes against multiple ICD-10 codes.
Follow the instructions carefully:

1. You will receive input as {codes}.
2. Evaluate the relevance of each CPT code against each ICD-10 code by using summary of each code.
3. Relevance is determined as:
     - If a CPT code is not relevant to each ICD-10 codes, it should be considered as irrelevant.
     - If a CPT code is relevant to even a single ICD-10 code, it should be considered as relevant
4. If all CPT codes are relevant, then give output strictly in this format:
   - All CPT codes are relevant to ICD codes
5. If there are irrelevant CPT codes, then give output strictly in this format in the form of bullet points listing only irrelevant CPT codes:
   - 99201
   - 45380
6. The input format for ICD-10 code is that it consists of a letter, followed by numbers, a decimal point, and additional characters for further specification of the condition (Example: A01.0).
7. The input format for CPT code is that it consists of a 5-digit numeric code used to represent medical, surgical, and diagnostic procedures or services (Example: 99213).
8. If the input is malformed or does not follow the above formats, return:
   Invalid input

Input {codes}
"""

content_prompt = ChatPromptTemplate.from_template(prompt)

# Custom function to display success messages with black text
def subheader_func(message):
    st.markdown(
        f"""
        <div style="color: black; background-color: #DFF2BF; border: 0.5px solid #4CAF50; padding: 5px; border-radius: 5px;">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )

def warning_message(message):
    st.markdown(
        f"""
        <div style="color: white; background-color: #FF0000; border: 0.5px solid #4CAF50; padding: 5px; border-radius: 5px;">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )
    
def output_message(message):
    st.markdown(
        f"""
        <div style="color: black; padding: 5px; border-radius: 5px; font-size: 25px;">
            <b>{message}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

def output_final(message):
    st.markdown(
        f"""
        <div style="color: black; padding: 5px; border-radius: 5px; font-size: 15px;">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )

def reformat_bullet_points(text):
    reformatted = re.sub(r"- (\d+)", r"\n- \1", text.strip())
    reformatted = re.sub(r"\s*\.\s*$", "", reformatted)
    return reformatted

def get_code_description(codes):
    url = f"https://medical-codes-542808340038.us-central1.run.app/get_icd_descriptions?codes={codes}"

    payload = {'codes': codes}

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return f"Error: Received status code {response.status_code}"
    
    except Exception as e:
        return f"Error: {str(e)}"

def evaluate_codes(codes):
    try:
        model = ChatOpenAI(model='gpt-4o-mini', temperature=0, openai_api_key=openai_api_key)
        parser = StrOutputParser()
        chain = content_prompt | model | parser
        response = chain.invoke({"codes": codes})
        return response

    except Exception as e:
        return f"Error: {str(e)}"

# Center the logo using Markdown
st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 30vh; margin: 0;">
        <img src="https://cloudsolutions.com.sa/images/headers/cloudsolutions-logo.png" alt="Logo" style="width: 150px; height: 150px;">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align: center; font-size: 30px;'>Treatment-to-Diagnosis Matching Using AI</h1>",
    unsafe_allow_html=True
)


# Manage session state for dynamic inputs
if 'icd_10_codes' not in st.session_state:
    st.session_state.icd_10_codes = []
if 'cpt_codes' not in st.session_state:
    st.session_state.cpt_codes = []

# Input for ICD-10 codes
with st.expander("Enter ICD-10 codes"):
    icd_code = st.text_input("ICD-10 Code")
    if st.button("Add", key="button_1"):
        if icd_code:
            st.session_state.icd_10_codes.append(icd_code)
                          
# Display ICD-10 codes
if st.session_state.icd_10_codes:
    subheader_func("Added ICD-10 Codes")
    # Display each CPT code on a new line
    for code in st.session_state.icd_10_codes:
        output_final("- "+ code)

# Input for CPT codes
with st.expander("Enter CPT codes"):
    cpt_code = st.text_input("CPT Code")
    if st.button("Add", key="button_2"):
        if cpt_code:
            st.session_state.cpt_codes.append(cpt_code)

# Display CPT codes
if st.session_state.cpt_codes:
    subheader_func("Added CPT Codes")
    # Display each CPT code on a new line
    for code in st.session_state.cpt_codes:
        output_final("- "+ code)

# Evaluate button and spinner
with st.container():
    st.markdown('<div class="center-button">', unsafe_allow_html=True)
    if st.button("Generate"):
        # Start spinner while code is running
        with st.spinner('Evaluating codes...'):
            if st.session_state.icd_10_codes and st.session_state.cpt_codes:
                codes = {
                    "icd_10": [{"code": code} for code in st.session_state.icd_10_codes],
                    "cpt_code": [{"code": code} for code in st.session_state.cpt_codes],
                }

                all_codes = st.session_state.icd_10_codes + st.session_state.cpt_codes
                codes_string = ",".join(all_codes)
                codes_data = get_code_description(codes_string)
                summary_dict = {item['code']: item['summary'] for item in codes_data['data']}

                for key in codes:
                    for code_entry in codes[key]:
                        code = code_entry['code']
                        if code in summary_dict:
                            code_entry['summary'] = summary_dict[code]
                output = evaluate_codes(codes)
                final_output = reformat_bullet_points(output)
                
                if final_output == "- All CPT codes are relevant to ICD codes":
                    output_message("Relevant CPT Codes")
                else:
                    output_message("Irrelevant CPT Codes")

                output_final(final_output)
            else:
                warning_message("Please enter both ICD-10 and CPT codes.")
    st.markdown('</div>', unsafe_allow_html=True)

# Add "Clear All" button at the end to clear both ICD-10 and CPT codes
if st.button("Clear All Codes", key="clear_button_all"):
    # Clear the lists in session state
    st.session_state.icd_10_codes.clear()  # Clears all ICD-10 codes
    st.session_state.cpt_codes.clear()  # Clears all CPT codes
    st.rerun()  # Force a rerun to update the UI

