from collections import Counter
import csv
import os
import re
import sys
from tabulate import tabulate
from typing import Dict, List, KeysView, Set, Tuple
import wordcloud


def main() -> None:
    srt_directory: str = get_directory("srt")
    print()
    print(f"Input directory for the .srt files: {srt_directory}")

    out_directory: str = get_directory("out")
    print(f"Output directory: {out_directory}")

    srt_paths: List[str] = get_paths(srt_directory)
    print()
    print(f"Parsing {len(srt_paths)} files...")

    chats: List[Dict] = read_files(srt_paths)

    if not chats:
        sys.exit("All files were skipped")

    print()
    print("Top words:")
    print()

    words_ranked: List[Tuple[str, int]] = get_rank(chats, "Word", 10)
    words_formated: List[Dict] = format_rank(words_ranked, column2="Word")
    print(tabulate(words_formated, headers="keys"))

    print()
    print("Top chatters:")
    print()

    chatters_ranked: List[Tuple[str, int]] = get_rank(chats, "Chatter", 10)
    chatters_formated: List[Dict] = format_rank(
        chatters_ranked, column2="Chatter", column3="Chats"
    )
    print(tabulate(chatters_formated, headers="keys"))

    print()
    print("Top streams")
    print()

    streams_ranked: List[Tuple[str, int]] = get_rank(chats, "Stream", 10)
    streams_formated: List[Dict] = format_rank(
        streams_ranked, column2="Stream", column3="Chats"
    )
    print(tabulate(streams_formated, headers="keys"))

    file_name: str = "chats.csv"
    print()
    print(f"Writing chats to {out_directory+file_name} ...")
    write_csv(out_directory, file_name, chats)

    file_name: str = "wordcloud.png"
    print(f"Writing wordcloud to {out_directory+file_name} ...")
    words_ranked: List[Tuple[str, int]] = get_rank(chats, "Word", 2000)
    write_wordcloud(out_directory, file_name, words_ranked)

    print("done!")
    print()


def get_directory(type: str = "srt") -> str:
    if type == "srt":
        # The directoy is hardcoded for now. Todo: get directory from argv or user prompt
        directory: str = "./srt/"
    elif type == "out":
        # The directoy is hardcoded for now. Todo: get directory from argv or user prompt
        directory: str = "./out/"
    else:
        raise ValueError(f"Type '{type}' is not valid")

    if os.path.isdir(directory):
        return directory
    else:
        sys.exit(f"Can't find {type}-directory: {directory}")


def get_paths(directory: str) -> List[str]:
    paths: List[str] = []
    for path in os.scandir(directory):
        if path.is_file():
            if os.path.splitext(path.name)[1] == ".srt":
                paths.append(path.path)
    return paths


def read_files(paths: List[str]) -> List[Dict]:
    chats: List[Dict] = []

    for path in paths:

        file_name: str = os.path.basename(path)

        with open(path) as file:
            lines: List[str] = file.readlines()

        try:
            file_chats = parse_file(file_name, lines)
            chats.extend(file_chats)
        except ValueError as e:
            print(e)

    return chats


def parse_file(file_name: str, lines: List[str]) -> List[Dict]:
    file_chats: List[Dict] = []
    stream: str = file_name.removesuffix(".srt")

    length: int = len(lines)
    if length % 4 != 0:
        raise ValueError(f"Can't parse file {file_name}, invalid number of lines")

    for i in range(0, length, 4):
        number: str = parse_number(lines[i].rstrip())
        time: str = parse_time(lines[i + 1].rstrip())
        chatter, message = parse_message(lines[i + 2].rstrip())
        chatter: str
        message: str
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

            error_message: str = (
                f"Can't parse file {file_name}, first error: line {i+error_line}"
            )
            raise ValueError(error_message)

    return file_chats


def parse_number(line: str) -> str:
    pattern: str = r"^\d+$"
    if match := re.search(pattern, line):
        return match.group(0)


def parse_time(line: str) -> str:
    pattern_time: str = r"(\d{2}(?::[0-5][0-9]){2}),\d{3}"
    pattern: str = r"^" + pattern_time + r" --> " + pattern_time + r"$"
    if match := re.search(pattern, line):
        return match.group(1)


def parse_message(line: str) -> List[str]:
    pattern: str = r"^@?(.+?): ?(.*)$"
    if match := re.search(pattern, line):
        chatter = match.group(1)
        message = match.group(2)
        return [chatter, message]
    else:
        return ["", ""]


def get_rank(chats: List[Dict], field: str, top_n: int = None) -> List[Tuple[str, int]]:
    fields: List[str] = []

    if field == "Word":
        for chat in chats:
            pattern: str = r"\w{3,}"
            message_words: List[str] = re.findall(pattern, chat["Message"])
            stopwords: Set[str] = set(wordcloud.STOPWORDS)
            stopwords.add("hey")
            for word in message_words:
                if word.casefold() not in stopwords:
                    fields.append(word)
    else:
        for chat in chats:
            fields.append(chat[field])

    return Counter(fields).most_common(top_n)


def format_rank(
    ranks: List[Tuple[str, int]],
    column1: str = "Rank",
    column2: str = "Value",
    column3: str = "#",
) -> List[Dict]:
    ranked: List[Dict] = []
    for index, rank in enumerate(ranks):
        ranked.append({column1: index + 1, column2: rank[0], column3: rank[1]})

    return ranked


def write_csv(dir: str, file_name: str, chats: List[Dict]) -> None:
    path: str = dir + file_name
    fieldnames: KeysView = chats[0].keys()

    with open(path, "w") as file:
        writer: csv.DictWriter = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for chat in chats:
            writer.writerow(chat)


def write_wordcloud(dir: str, file_name: str, words: List[Tuple[str, int]]) -> None:
    path: str = dir + file_name
    word_frequency: Dict = dict(words)
    wc: wordcloud.WordCloud = wordcloud.WordCloud(
        width=1920, height=1080, max_words=1000
    )
    wc.generate_from_frequencies(word_frequency)
    wc.to_file(path)


if __name__ == "__main__":
    main()