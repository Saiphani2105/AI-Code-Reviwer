import streamlit as st
import google.generativeai as genai
import re

# Configure API Key
api_key = st.secrets["GOOGLE_API_KEY"]      ## Give your Google API Key
genai.configure(api_key=api_key)

# System Instruction for AI Code Review
system_prompt = """You are a Python code reviewer. Provide feedback on:
- Code quality and best practices.
- Performance optimizations.
- Readability and maintainability.
- Security improvements.
Return formatted responses with clear explanations and Python code blocks when needed."""

# Load AI Model
model = genai.GenerativeModel(
    model_name="models/gemini-2.0-flash-exp", 
    system_instruction=system_prompt
)

@st.cache_resource
def review_code(user_code):
    """Function to review Python code using Gemini AI with caching."""
    try:
        # Validate Python syntax
        compile(user_code, '<string>', 'exec')
        
        # Generate AI response
        response = model.generate_content(user_code)
        
        # Handle response
        if hasattr(response, "text"):
            return response.text.strip()
        elif hasattr(response, "candidates") and isinstance(response.candidates, list) and len(response.candidates) > 0:
            return response.candidates[0].text.strip()
        else:
            return "❌ Error: Unexpected response format."
    except SyntaxError as e:
        st.warning(f"⚠️ Invalid Python code: {e}")
        return None
    except Exception as e:
        st.error("🚨 An error occurred during code review.")
        st.exception(e)
        return None

# Streamlit UI
st.title("📢 AI Code Reviewer")
st.write("🔍 Enter your Python code below and receive AI-powered feedback.")

# Text area for user input
user_code = st.text_area(
    "📝 Python Code:", 
    height=200, 
    placeholder="Write or paste your Python code here..."
)

if st.button("🚀 Generate Review") and user_code:
    if not user_code.strip():
        st.warning("⚠️ Please enter some Python code to review.")
        st.stop()
    
    with st.spinner("🤖 Analyzing your code..."):
        feedback = review_code(user_code)
    
    if feedback:
        # Extract Python code blocks and explanations using regex
        code_blocks = re.split(r'```python|```', feedback, flags=re.IGNORECASE)
        with st.expander("💡 AI Review Feedback", expanded=True):
            for block in code_blocks:
                cleaned_block = block.strip()
                if cleaned_block:
                    # Check if the block is code or text
                    if re.search(r'\b(def |import |=|return |class |for |while |if |elif |else )', cleaned_block):
                        st.code(cleaned_block, language="python")
                    else:
                        st.write(cleaned_block)
    else:
        st.error("❌ Code review failed. Please check your input or try again.")
