from analyzer import parse_uploaded_files, get_word_rank, get_rank, format_rank
import streamlit as st
import io
import wordcloud
import pandas as pd

st.set_page_config(page_title="Comment Analyzer", layout="wide")

with st.sidebar:
    st.header("File Upload")

    uploaded_files = st.file_uploader(
        "Upload .srt files",
        type=["srt"],
        accept_multiple_files=True,
        key="file_uploader",
    )

st.title("Comment Analyzer")


if uploaded_files:
    st.write(f"Uploaded {len(uploaded_files)} file(s)")

    # Prepare files for parsing
    files_to_parse = []
    for uploaded_file in uploaded_files:
        # Read the file content as string
        content = io.StringIO(uploaded_file.getvalue().decode("utf-8")).read()
        files_to_parse.append((uploaded_file.name, content))

    # Parse the files
    chats, errors = parse_uploaded_files(files_to_parse)

    # Display errors if any
    if errors:
        error_lines = "\n".join(f"- {error}" for error in errors)
        error_msg = f"Parsing errors encountered:\n\n{error_lines}"
        st.error(error_msg)

    # Display results if we have data
    if chats:
        st.success(f"Successfully parsed {len(chats)} chat messages")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Top words
            st.subheader("Top Words")
            words_ranked = get_word_rank(chats, 10)
            words_formatted = format_rank(words_ranked, column2="Word")
            st.dataframe(words_formatted, width="content")

        with col2:
            # Top chatters
            st.subheader("Top Chatters")
            chatters_ranked = get_rank(chats, "Chatter", 10)
            chatters_formatted = format_rank(
                chatters_ranked, column2="Chatter", column3="Chats"
            )
            st.dataframe(chatters_formatted, width="content")

        with col3:
            # Top streams
            st.subheader("Top Streams")
            streams_ranked = get_rank(chats, "Stream", 10)
            streams_formatted = format_rank(
                streams_ranked, column2="Stream", column3="Chats"
            )
            st.dataframe(streams_formatted, width="content")

        # Chats
        st.subheader("Chats")
        chats_df = pd.DataFrame(chats, columns=["Stream", "Chatter", "Message"])
        st.dataframe(chats_df, hide_index=True)

        # Word cloud
        st.subheader("Word Cloud")
        if st.button("Generate Word Cloud"):

            words_ranked = get_word_rank(chats, 2000)
            word_frequency = dict(words_ranked)

            wc = wordcloud.WordCloud(width=1920, height=1080, max_words=1000)
            wc.generate_from_frequencies(word_frequency)

            # Display wordcloud
            st.image(wc.to_array())

    elif not errors:
        st.info("No chat messages found in the uploaded files")
