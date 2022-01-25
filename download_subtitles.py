import re

import spacy
import webvtt
import youtube_dl
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.kl import KLSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.reduction import ReductionSummarizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
from tqdm import tqdm

from logger import log

log.debug("Loading model...")
nlp = spacy.load("ja_ginza_electra")
log.debug("done")


def vtt2text(vtt_path: str) -> str:
    log.debug("converting vtt to txt...")
    txt_path = re.sub(r".vtt$", ".txt", vtt_path)
    vtt = webvtt.read(vtt_path)

    lines = []
    transcript = ""
    for line in vtt:
        # Strip the newlines from the end of the text.
        # Split the string if it has a newline in the middle
        # Add the lines to an array
        lines.extend(line.text.strip().splitlines())

    # Remove repeated lines
    previous = None
    for line in lines:
        if line == previous:
            continue
        transcript += " " + line
        previous = line

    with open(txt_path, "w") as f:
        f.write(transcript)

    log.debug(f"done. ({txt_path})")
    return transcript


def download_subtitle(
    video_id: str, subtitle_lang: str = "ja", subtitle_format: str = "vtt"
) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = f"outputs/subtitle_{video_id}"
    options = {
        "writeautomaticsub": True,
        "subtitleslangs": [subtitle_lang],
        "subtitlesformat": subtitle_format,
        "skip_download": True,
        "outtmpl": output_path,
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([url])
    return f"{output_path}.{subtitle_lang}.{subtitle_format}"


def remove_space(text: str) -> str:
    replace_list = [" ", "　"]
    for w in replace_list:
        text = text.replace(w, "")
    return text.strip()


def divide_sentence(text: str):
    output_text: str = ""
    doc = nlp(text)
    for sent in tqdm(doc.sents):
        output_text += f"{remove_space(str(sent))}。"
    return output_text


def make_summary(text: str, sentence_num: int = 3) -> str:
    corpus = []
    originals = []
    doc = nlp(text)
    for s in doc.sents:
        originals.append(s)
        tokens = []
        for t in s:
            tokens.append(t.lemma_)
        corpus.append(" ".join(tokens))
    parser = PlaintextParser.from_string("".join(corpus), Tokenizer("japanese"))

    # choose summarizer
    summarizer = LexRankSummarizer()
    # summarizer = LsaSummarizer()
    # summarizer = ReductionSummarizer()
    # summarizer = LuhnSummarizer()
    # summarizer = SumBasicSummarizer()
    # summarizer = KLSummarizer()

    summarizer.stop_words = [" "]  # スペースも1単語として認識されるため、ストップワードにすることで除外する
    # sentencres_count指定
    summary = summarizer(document=parser.document, sentences_count=sentence_num)
    summary = [originals[corpus.index(sentence.__str__())] for sentence in summary]
    summary = [item.text for item in summary]
    return "\n".join(summary)

    # summarizers = [
    #    LexRankSummarizer(),
    #    LsaSummarizer(),
    #    ReductionSummarizer(),
    #    LuhnSummarizer(),
    #    SumBasicSummarizer(),
    #    KLSummarizer(),
    # ]
    # for summarizer in summarizers:
    #    try:
    #        summarizer.stop_words = [" "]  # スペースも1単語として認識されるため、ストップワードにすることで除外する
    #        # sentencres_count指定
    #        summary = summarizer(document=parser.document, sentences_count=sentence_num)
    #        log.debug(f"summarizer: {str(summarizer)}")
    #        log.debug(
    #            str(
    #                [
    #                    originals[corpus.index(sentence.__str__())]
    #                    for sentence in summary
    #                ]
    #            )
    #        )
    #    except Exception as e:
    #        log.error(f"An error is occured!: {e}")


if __name__ == "__main__":
    vtt_path = download_subtitle("xlDGAr5FAvA")
    text = vtt2text(vtt_path)
    text = divide_sentence(text)
    summary = make_summary(text, sentence_num=10)
    log.debug(summary)
    t = "\n".join([item.text for item in summary])
    log.debug(t)
