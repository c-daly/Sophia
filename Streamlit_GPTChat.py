import streamlit as st
from wrappers.OpenAIWrapper import ChatWrapperOpenAI
import openai


# Main chat loop
#while True:
    # Display chat history
    #a.display_chat_history()

    # Get user input
#    prompt = input("User: ")
#    a.messages.append({"role": "user", "content": prompt})

    # Get assistant response
#    response = a.get_assistant_response()
#    print(f"Assistant: {response}")
#    a.messages.append({"role": "assistant", "content": response})


# Add a title
st.title("Coding Assistant")
# Create a text area to display past input

# Create an input field
input_text = st.text_input("Enter your input", value="", max_chars=None, key=None)

# Create a submit button
if st.button("Submit"):
    if 'a' not in st.session_state:
        st.session_state.a = ChatWrapperOpenAI()
    a = st.session_state.a
    # Call the placeholder function with the input
    # agent.past_input += output
    # st.write(agent.past_input)
    # st.experimental_rerun()
    # Display the output
    a.messages.append({"role": "user", "content": input_text})
    response = a.get_assistant_response()
    a.messages.append({"role": "assistant", "content": response})
    #st.write(f"Assistant: {response}")
    st.write(a.messages)
    st.session_state.a = a

