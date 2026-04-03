from collections import Counter
import csv
import os
import re
import sys
from tabulate import tabulate
import wordcloud


def main():
    srt_directory = get_directory("srt")
    out_directory = get_directory("out")
    srt_paths = get_paths(srt_directory)
    chats = read_files(srt_paths)

    write_csv(out_directory, chats)

    write_wordcloud(out_directory, chats)

    words_ranked = get_word_rank(chats, 10)
    print(tabulate(words_ranked, headers="keys"))

    print()

    chatters_ranked = get_rank(chats, "Chatter", 10)
    print(tabulate(chatters_ranked, headers="keys"))

    print()

    files_ranked = get_rank(chats, "Stream", 10)
    print(tabulate(files_ranked, headers="keys"))


def get_directory(type="srt"):
    if type == "srt":
        # The directoy is hardcoded for now. Todo: get directory from argv or user prompt
        directory = "/workspaces/262424203/project/srt/"
    elif type == "out":
        # The directoy is hardcoded for now. Todo: get directory from argv or user prompt
        directory = "/workspaces/262424203/project/out/"

    if os.path.isdir(directory):
        return directory
    else:
        sys.exit(f"Can't find {type}-directory: {directory}")


def get_paths(directory):
    paths = []
    for path in os.scandir(directory):
        if path.is_file():
            if os.path.splitext(path.name)[1] == ".srt":
                paths.append(path.path)
    return paths


def read_files(paths):
    chats = []

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


def parse_file(file_name, lines):
    file_chats = []
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


def parse_number(line):
    pattern = r"^\d+$"
    if match := re.search(pattern, line):
        return match.group(0)


def parse_time(line):
    pattern_time = r"(\d{2}(?::[0-5][0-9]){2}),\d{3}"
    pattern = r"^" + pattern_time + r" --> " + pattern_time + r"$"
    if match := re.search(pattern, line):
        return match.group(1)


def parse_message(line):
    pattern = r"^@?(.+?): ?(.*)$"
    if match := re.search(pattern, line):
        chatter = match.group(1)
        message = match.group(2)
        return [chatter, message]
    else:
        return [None, None]

def write_csv(dir, chats):
    path = dir + "chats.csv"
    fieldnames = chats[0].keys()

    with open(path, "w") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for chat in chats:
            writer.writerow(chat)

def write_wordcloud(dir, chats):
    path = dir + "wordcloud.png"

def get_word_rank(chats, top_n=None):
    words = []

    for chat in chats:
        pattern = r"\w{3,}"
        message_words = re.findall(pattern, chat["Message"])
        stopwords = set(wordcloud.STOPWORDS)
        stopwords.add("markus")
        stopwords.add("hey")
        for word in message_words:
            if word.casefold() not in stopwords:
                words.append(word)

    ranks = Counter(words).most_common(top_n)

    words_ranked = []
    for index, rank in enumerate(ranks):
        words_ranked.append({"Rank": index + 1, "Word": rank[0], "#": rank[1]})

    return words_ranked


def get_rank(chats, field=None, top_n=None):
    fields = []
    for chat in chats:
        fields.append(chat[field])

    ranks = Counter(fields).most_common(top_n)

    fields_ranked = []
    for index, rank in enumerate(ranks):
        fields_ranked.append({"Rank": index + 1, field: rank[0], "Chats": rank[1]})

    return fields_ranked


if __name__ == "__main__":
    main()
