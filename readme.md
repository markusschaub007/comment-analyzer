# Commment Analyser for ecamm Live

### Vidoe Demo: [link will follow](https://youtube.com)

### Description

Here it comes

## Deciding the scope

MVP

## Some Titel

### Format of the .srt Files from ecamm Live

Live chat messages are stored in a SupRip file, with the ".srt" extension. The format is described in [Wikipedia](https://en.wikipedia.org/wiki/SubRip).

Specific to ecamm live:

- The start time is set to when ecamm got the chat message (relative to the start of the stream). The end time is always 5 seconds after the start time.

- The text is always on one line and is divided by a ":" into the chatter and the chat message:

    - chatter:

        The name of the person sending the chat. It may be prefixed with a "@", but this is not always the case.

    - message

        This contains the text, that was sent. **Caution:** there may be additional ":" in the message and the message can be empty.

- The file ends with two blank lines.

**Example:**

```
1
00:02:06,000 --> 00:02:11,000
@FishstickUSA: Hello Markus

2
00:02:22,000 --> 00:02:27,000
@eaglevp: Hi Phillip
````

### Parsing the .srt File

There are 4 types of line to parse:

- **blank line:** ingore
- **number:** check for an integer and save as "number".
- **time:** check the starting time (hh:mm:ss) and save as "time"
- **text:** split at the first ":" into chatter and message:
    - **chatter:** ignore the optinal "@" at the start and save as "chatter"
    - **message:** ignore the leading blank, accept empty message. Save as "message"

Iterating throug the lines, while ignoring blank lines means that the order is always: number, time, text.
