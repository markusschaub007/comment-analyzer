# Commment Analyser for Ecamm Live

### Vidoe Demo: [link will follow](https://youtube.com)

### Description

Ecamm Live is a mac software for live streaming. During a live stream people can put messages in the chat. The messages get stored in a SubRip File. With the Comment Analyser for Ecamm Live you can collect and analyse this chats.

### Deciding the scope

This is my final project for the Harward course: "CS50's Introduction to Programming with Python". My goals for the project were:

- Fullfilling the course requierements
- Applying and practicing what I've learned
- Challenging myself
- Finishing in a resonable time
- Build something that is useful to me and potentially others

These goals guided the scope of the project. It can't be too big in order to complete it in a resonable time. It still needs to be complete enough to be useful.

I decided the scope with the **Minimal Viable Product** (MVP) strategy. It is described in [Wikipedia](https://en.wikipedia.org/wiki/Minimum_viable_product).

#### MVP Features:

- Reading the SubRip files from the programms subfolder `/srt/`.
- Parsing the files and extracting:
    - the date and time from the file name
    - the time, chatter and message from the file content
- Writing the results in a `csv` file in the programms subfolder `/out/`.
- Creating a wordcloud from the messages in a `png` file in the programms subfolder `/out/`.
- Create a list of the top 10 chatters with the number of their chats and `print` it to the `terminal`.

### Features for future releases:

- Saving the imported data in a database
- Letting the user choose the directory for the import, and the directory and filename for the output.
- More statistics, that can be chosen and configured by the user.
- Interactivity with:
    - command line arguments
    - a TUI
    - a GUI
    - a web interface

## Some Titel

### Format of the .srt Files from Ecamm Live

#### Filename


#### Content

Live chat messages are stored in a SubRip file, with the `.srt` extension. The format is described in [Wikipedia](https://en.wikipedia.org/wiki/SubRip).

Specific to Ecamm live:

- The start time is set to when Ecamm Live got the chat message (relative to the start of the stream). The end time is always 5 seconds after the start time.

- The text is always on one line and is divided by a `:` into the chatter and the chat message:

    - chatter:

        The name of the person sending the chat. It may be prefixed with a `@`, but this is not always the case.

    - message

        This contains the text, that was sent. **Caution:** there may be additional `:` in the message and the message can be empty.

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

### Parsing the `.srt` File

There are 4 types of lines to parse:

- **blank line:** ingore
- **number:** check for an integer and save as `number`.
- **time:** check the starting time (hh:mm:ss) and save as `time`
- **text:** split at the first ":" into chatter and message:
    - **chatter:** ignore the optinal `@` at the start and save as `chatter`
    - **message:** ignore the leading blank, accept empty message. Save as `message`

Iterating throug the lines, while ignoring `blank lines` means that the order is always: `number`, `time`, `text`.
