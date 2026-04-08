from collections import Counter
import csv
import os
import re
import sys
from tabulate import tabulate
from typing import Literal, TypedDict
import wordcloud


class ChatEntry(TypedDict):
    Stream: str
    Number: str
    Time: str
    Chatter: str
    Message: str


def main() -> None:
    srt_directory = get_directory("srt")
    print()
    print(f"Input directory for the .srt files: {srt_directory}")

    out_directory = get_directory("out")
    print(f"Output directory: {out_directory}")

    srt_paths = get_paths(srt_directory)
    print()
    print(f"Parsing {len(srt_paths)} files...")

    chats = read_files(srt_paths)

    if not chats:
        sys.exit("All files were skipped")

    print()
    print("Top words:")
    print()

    words_ranked = get_word_rank(chats, 10)
    words_formated = format_rank(words_ranked, column2="Word")
    print(tabulate(words_formated, headers="keys"))

    print()
    print("Top chatters:")
    print()

    chatters_ranked = get_rank(chats, "Chatter", 10)
    chatters_formated = format_rank(chatters_ranked, column2="Chatter", column3="Chats")
    print(tabulate(chatters_formated, headers="keys"))

    print()
    print("Top streams")
    print()

    streams_ranked = get_rank(chats, "Stream", 10)
    streams_formated = format_rank(streams_ranked, column2="Stream", column3="Chats")
    print(tabulate(streams_formated, headers="keys"))

    file_name = "chats.csv"
    print()
    print(f"Writing chats to {out_directory+file_name} ...")
    write_csv(out_directory, file_name, chats)

    file_name = "wordcloud.png"
    print(f"Writing wordcloud to {out_directory+file_name} ...")
    words_ranked = get_word_rank(chats, 2000)
    write_wordcloud(out_directory, file_name, words_ranked)

    print("done!")
    print()


def get_directory(directory_type: str = "srt") -> str:
    if directory_type == "srt":
        # The directoy is hardcoded for now. Todo: get directory from argv or user prompt
        directory = "./srt/"
    elif directory_type == "out":
        # The directoy is hardcoded for now. Todo: get directory from argv or user prompt
        directory = "./out/"
    else:
        raise ValueError(f"Type '{directory_type}' is not valid")

    if os.path.isdir(directory):
        return directory
    else:
        sys.exit(f"Can't find {directory_type}-directory: {directory}")


def get_paths(directory: str) -> list[str]:
    paths: list[str] = []
    for path in os.scandir(directory):
        if path.is_file():
            if os.path.splitext(path.name)[1] == ".srt":
                paths.append(path.path)
    return paths


def read_files(paths: list[str]) -> list[ChatEntry]:
    chats: list[ChatEntry] = []

    for path in paths:

        file_name = os.path.basename(path)

        with open(path) as file:
            lines = file.readlines()

        try:
            file_chats = parse_file(file_name, lines)
            chats.extend(file_chats)
        except ValueError as e:
            print(e)

    return chats


def parse_uploaded_files(
    uploaded_files: list[tuple[str, str]],
) -> tuple[list[ChatEntry], list[str]]:
    """
    Parse uploaded file contents.

    Args:
        uploaded_files: List of tuples containing (file_name, file_content)

    Returns:
        Tuple of (chats, errors) where chats is the parsed data and errors are parsing errors
    """
    chats: list[ChatEntry] = []
    errors: list[str] = []

    for file_name, file_content in uploaded_files:
        lines = file_content.splitlines(keepends=True)

        try:
            file_chats = parse_file(file_name, lines)
            chats.extend(file_chats)
        except ValueError as e:
            errors.append(str(e))

    return chats, errors


def parse_file(file_name: str, lines: list[str]) -> list[ChatEntry]:
    file_chats: list[ChatEntry] = []
    stream = file_name.removesuffix(".srt")

    length = len(lines)
    if length % 4 != 0:
        raise ValueError(f"Can't parse file {file_name}, invalid number of lines")

    for i in range(0, length, 4):
        number = parse_number(lines[i].rstrip())
        time = parse_time(lines[i + 1].rstrip())
        chatter, message = parse_message(lines[i + 2].rstrip())
        if number and time and chatter:
            file_chats.append(
                {
                    "Stream": stream,
                    "Number": number,
                    "Time": time,
                    "Chatter": chatter,
                    "Message": message,
                }
            )
        else:
            if not number:
                error_line = 1
            elif not time:
                error_line = 2
            else:
                error_line = 3

            error_message = (
                f"Can't parse file {file_name}, first error: line {i+error_line}"
            )
            raise ValueError(error_message)

    return file_chats


def parse_number(line: str) -> str:
    pattern = r"^\d+$"
    if match := re.search(pattern, line):
        return match.group(0)
    else:
        return ""


def parse_time(line: str) -> str:
    pattern_time = r"(\d{2}(?::[0-5][0-9]){2}),\d{3}"
    pattern = r"^" + pattern_time + r" --> " + pattern_time + r"$"
    if match := re.search(pattern, line):
        return match.group(1)
    else:
        return ""


def parse_message(line: str) -> tuple[str, str]:
    pattern = r"^@?(.+?): ?(.*)$"
    if match := re.search(pattern, line):
        chatter = match.group(1)
        message = match.group(2)
        return (chatter, message)
    else:
        return ("", "")


def get_word_rank(
    chats: list[ChatEntry], top_n: int | None = None
) -> list[tuple[str, int]]:
    stopwords = set(wordcloud.STOPWORDS)
    stopwords.add("hey")

    word_totals = Counter()
    word_variants = {}

    pattern = r"\w{3,}"
    for chat in chats:
        message_words = re.findall(pattern, chat["Message"])

        for word in message_words:
            normalized = word.casefold()

            if normalized in stopwords:
                continue

            word_totals[normalized] += 1

            if normalized not in word_variants:
                word_variants[normalized] = Counter()

            word_variants[normalized][word] += 1

    words_ranked: list[tuple[str, int]] = []
    for normalized, total_count in word_totals.most_common(top_n):
        variants_for_word = word_variants[normalized]
        display_word = variants_for_word.most_common(1)[0][0]

        words_ranked.append((display_word, total_count))

    return words_ranked


def get_rank(
    chats: list[ChatEntry],
    field: Literal["Chatter", "Stream"],
    top_n: int | None = None,
) -> list[tuple[str, int]]:
    return Counter(chat[field] for chat in chats).most_common(top_n)


def format_rank(
    ranks: list[tuple[str, int]],
    column1: str = "Rank",
    column2: str = "Value",
    column3: str = "#",
) -> list[dict[str, int | str]]:
    ranked = []
    for index, rank in enumerate(ranks):
        ranked.append({column1: index + 1, column2: rank[0], column3: rank[1]})

    return ranked


def write_csv(directory: str, file_name: str, chats: list[ChatEntry]) -> None:
    path = directory + file_name
    fieldnames = chats[0].keys()

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for chat in chats:
            writer.writerow(chat)


def write_wordcloud(
    directory: str, file_name: str, words: list[tuple[str, int]]
) -> None:
    path = directory + file_name
    word_frequency = dict(words)
    wc = wordcloud.WordCloud(width=1920, height=1080, max_words=1000)
    wc.generate_from_frequencies(word_frequency)
    wc.to_file(path)


if __name__ == "__main__":
    main()
