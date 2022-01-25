import streamlit as st

from download_subtitles import (divide_sentence, download_subtitle,
                                make_summary, vtt2text)
from logger import log


def get_subtitle(video_id, sentence_num: int = 10):
    vtt_path = download_subtitle(video_id)
    text = vtt2text(vtt_path)
    origin = divide_sentence(text)
    summary = make_summary(origin, sentence_num=10)
    log.debug(summary)
    return summary, origin


st.title("Video Summary")
sentence_num = st.slider("・要約後の文の数", min_value=0, max_value=100, step=1, value=10)
video_id = st.text_input(label="・video_id (ヒント: https://www.youtube.com/watch?v={video_id})", value="xlDGAr5FAvA")
run_summary = st.button("実行")


if run_summary:
    summary, origin = get_subtitle(video_id, sentence_num=sentence_num)
    st.subheader("実行結果")
    st.text(summary)
    with st.expander("原文"):
        st.write(origin)
