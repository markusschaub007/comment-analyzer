from analyzer import parse_uploaded_files, get_word_rank, get_rank, format_rank
import streamlit as st
import io

st.set_page_config(page_title="Comment Analyzer", layout="wide")

st.title("Comment Analyzer")

uploaded_files = st.file_uploader(
    "Upload .srt files", 
    type=["srt"], 
    accept_multiple_files=True,
    key="file_uploader"
)

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
        st.error("Parsing errors encountered:")
        for error in errors:
            st.error(f"  • {error}")
    
    # Display results if we have data
    if chats:
        st.success(f"Successfully parsed {len(chats)} chat messages")
        
        # Top words
        st.subheader("Top Words")
        words_ranked = get_word_rank(chats, 10)
        words_formatted = format_rank(words_ranked, column2="Word")
        st.dataframe(words_formatted, use_container_width=True)
        
        # Top chatters
        st.subheader("Top Chatters")
        chatters_ranked = get_rank(chats, "Chatter", 10)
        chatters_formatted = format_rank(chatters_ranked, column2="Chatter", column3="Chats")
        st.dataframe(chatters_formatted, use_container_width=True)
        
        # Top streams
        st.subheader("Top Streams")
        streams_ranked = get_rank(chats, "Stream", 10)
        streams_formatted = format_rank(streams_ranked, column2="Stream", column3="Chats")
        st.dataframe(streams_formatted, use_container_width=True)
        
        # Word cloud
        st.subheader("Word Cloud")
        words_ranked = get_word_rank(chats, 2000)
        word_frequency = dict(words_ranked)
        
        import wordcloud
        wc = wordcloud.WordCloud(width=1920, height=1080, max_words=1000)
        wc.generate_from_frequencies(word_frequency)
        
        # Display wordcloud
        st.image(wc.to_array(), use_container_width=True)
    elif not errors:
        st.info("No chat messages found in the uploaded files")

