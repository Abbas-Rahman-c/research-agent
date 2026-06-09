import streamlit as st
import httpx

API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(
    page_title="Career Research Agent",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Career Research Agent")
st.caption("Powered by Groq + Azure AI Search (Foundry IQ)")
st.markdown("Ask anything about AI engineering careers, salaries, skills, or interview prep.")

# Example questions
st.markdown("**Try asking:**")
col1, col2 = st.columns(2)
with col1:
    if st.button("💰 AI engineer salaries"):
        st.session_state.question = "What is the salary of an AI engineer in 2026?"
    if st.button("🛠️ Skills to learn"):
        st.session_state.question = "What skills should I learn for a high paying AI job?"
with col2:
    if st.button("📄 Resume tips"):
        st.session_state.question = "How do I write a strong AI engineering resume?"
    if st.button("🎯 Interview prep"):
        st.session_state.question = "How do I prepare for an AI engineering interview?"

st.divider()

question = st.text_input(
    "Your question",
    value=st.session_state.get("question", ""),
    placeholder="e.g. What skills do I need for a high paying AI job?"
)

if st.button("Research", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    elif len(question.strip()) < 5:
        st.warning("Please ask a more specific question.")
    else:
        with st.spinner("Decomposing question → Searching Foundry IQ → Synthesizing answer..."):
            try:
                response = httpx.post(
                    API_URL,
                    json={"question": question},
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()

                st.success("Done!")

                st.subheader("Answer")
                st.write(data["answer"])

                with st.expander("Reasoning steps"):
                    st.markdown("**Question broken into:**")
                    for i, sq in enumerate(data["sub_questions"], 1):
                        st.markdown(f"{i}. {sq}")

                with st.expander("Sources used"):
                    for source in data["sources"]:
                        st.markdown(f"- {source}")

            except httpx.TimeoutException:
                st.error("Request timed out — the agent is taking too long. Please try again.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    st.error("Invalid question. Please try rephrasing.")
                else:
                    st.error("Something went wrong. Please try again.")
            except httpx.ConnectError:
                st.error("Cannot connect to backend. Make sure FastAPI is running on port 8000.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

st.divider()
st.caption("Agents League Hackathon 2026 · Microsoft Foundry IQ")