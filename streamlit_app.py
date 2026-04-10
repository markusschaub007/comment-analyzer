from analyzer import parse_uploaded_files, get_word_rank, get_rank, format_rank
import streamlit as st
import io
import wordcloud
import pandas as pd

st.set_page_config(
    page_title="Comment Analyzer Beta", layout="wide", initial_sidebar_state="expanded"
)

with st.sidebar:
    st.header("File Upload")

    uploaded_files = st.file_uploader(
        "Upload .srt files",
        type=["srt"],
        accept_multiple_files=True,
        key="file_uploader",
    )

st.title("Comment Analyzer Beta")


if uploaded_files:

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
        chats_df = pd.DataFrame(
            chats,
            columns=[
                "StreamName",
                "StreamTime",
                "Number",
                "Time",
                "Chatter",
                "Message",
            ],
        )
        total_streams = chats_df["StreamName"].nunique()
        total_chatters = chats_df["Chatter"].nunique()
        total_chats = len(chats_df)

        all_chatters = sorted(chats_df["Chatter"].dropna().unique().tolist())
    
        streams_df = (
            chats_df.groupby(["StreamName", "StreamTime"])
            .agg(Chats=("Message", "size"), Chatters=("Chatter", "nunique"))
            .reset_index()
        )
        chatters_df = (
            chats_df.groupby("Chatter")
            .agg(Chats=("Message", "size"), Streams=("StreamName", "nunique"))
            .reset_index()
            .sort_values(["Chats", "Chatter"], ascending=[False, True])
        )

        st.subheader("Overview")
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Total Streams", f"{total_streams:,}")
        with c2:
            st.metric("Total Chatters", f"{total_chatters:,}")
        with c3:
            st.metric("Total Chats", f"{total_chats:,}")

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
            streams_ranked = get_rank(chats, "StreamName", 10)
            streams_formatted = format_rank(
                streams_ranked, column2="Stream", column3="Chats"
            )
            st.dataframe(streams_formatted, width="content")

        # Chatters
        st.subheader("Chatters")
        st.dataframe(
            chatters_df.style.format(
                {
                    "Chats": "{:,}",
                    "Streams": "{:,}",
                }
            ),
            hide_index=True,
        )

        # Streams
        st.subheader("Streams")
        st.dataframe(
            streams_df.style.format(
                {
                    "Chats": "{:,}",
                    "Chatters": "{:,}",
                }
            ),
            hide_index=True,
        )

        # Chats
        st.subheader("Chats")

        choices = ["All"] + all_chatters

        selected_chatter = st.selectbox(
            "Filter by chatter",
            options=choices,
            index=0,
        )

        if selected_chatter == "All":
            filterd_chats_df = chats_df
        else:
            filterd_chats_df = chats_df[chats_df["Chatter"] == selected_chatter]

        st.dataframe(filterd_chats_df, hide_index=True)

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

else:
    st.info(
        "Please upload one or more .srt files in the sidebar to analyze the chat messages"
    )
