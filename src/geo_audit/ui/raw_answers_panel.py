import streamlit as st


def render_raw_answers_panel(raw_answers):
    st.subheader("5. Raw AI Answers / Evidence Log")
    st.caption("Open each item to inspect the original AI answer used for scoring.")

    for item in raw_answers:
        with st.expander(f"{item['prompt_category']}"):
            st.markdown(f"**Prompt:** {item['prompt']}")
            st.write(item["answer"])
