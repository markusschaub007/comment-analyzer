import re
from datetime import datetime
from typing import TypedDict


class ChatEntry(TypedDict):
    StreamName: str
    StreamTime: datetime
    Number: str
    Time: str
    Chatter: str
    Message: str


def parse_file(file_name: str, lines: list[str]) -> list[ChatEntry]:
    chats: list[ChatEntry] = []
    stream_name, stream_time = parse_filename(file_name)

    length = len(lines)
    if length % 4 != 0:
        raise ValueError(f"Can't parse file {file_name}, invalid number of lines")

    for i in range(0, length, 4):
        number = parse_number(lines[i].rstrip())
        time = parse_time(lines[i + 1].rstrip())
        chatter, message = parse_message(lines[i + 2].rstrip())
        if number and time and chatter:
            chats.append(
                {
                    "StreamName": stream_name,
                    "StreamTime": stream_time,
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

    return chats


def parse_filename(file_name: str) -> tuple[str, datetime]:
    pattern = r"^(.*?) on (\d{4}-\d{2}-\d{2}) at (\d{2}\.\d{2})\.srt$"
    if match := re.search(pattern, file_name):
        stream_name = match.group(1)
        date_time = match.group(2) + " " + match.group(3)
        streamtime = datetime.strptime(date_time, "%Y-%m-%d %H.%M")
        return stream_name, streamtime
    else:
        raise ValueError(f"Can't parse file name {file_name}")

# print(parse_filename("Live Stream on 2024-01-01 at 12.00.srt")[1].date())

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
