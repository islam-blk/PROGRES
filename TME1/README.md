# PROGRES - TME1

Python programs for exercises 1 and 2 (UDP ping, TCP time server).
Each exercise has its own folder with a `server.py` and a `client.py`.
Always start the server first, then the client.

## Exercise 1 - UDP ping

### What it does

- `server.py`: waits for UDP messages and answers each one with "pong". It can ignore a message at random, using a miss rate (0.5 means half of the messages get no answer).
- `client.py`: sends a number of "ping" messages, measures the time until each answer comes back (the RTT), and prints the average RTT. If no answer comes before the timeout, the ping is counted as failed and is not used in the average.

### How to run

Server:

```
python server.py
python server.py --serverPort 1234 --missRate 0.5
```

Client:

```
python client.py
python client.py --serverAddress 127.0.0.1 --serverPort 1234 --count 10 --timeOut 1.0
```

Options:

| Program | Option | Default | Meaning |
|---|---|---|---|
| server | `--serverPort` | 1234 | port to listen on |
| server | `--missRate` | 0.0 | probability of not answering |
| client | `--serverAddress` | 127.0.0.1 | server IP or name |
| client | `--serverPort` | 1234 | server port |
| client | `--count` | 4 | number of pings |
| client | `--timeOut` | 1.0 | seconds to wait for each answer |

To test several clients, open several terminals and run the client in each one (use a big `--count` so they overlap).
To test on two machines, run the server on one, and give its IP with `--serverAddress` on the other.

## Exercise 2 - TCP time server

### What it does

- `server.py`: TCP server. For each client that connects it starts a thread, so several clients can be served at the same time. For every request it receives, it sends back its current time. It stops serving a client when the client closes the connection.
- `client.py`: connects once, asks the server for the time `count` times, and computes the clock difference for each try with `server_time - (t1 + t2) / 2`, where `t1` is the time before sending and `t2` the time after receiving. It prints the offset of the try with the smallest RTT, since that one is the most precise.

### How to run

Server:

```
python server.py
python server.py --serverPort 2345
```

Client:

```
python client.py
python client.py --serverAddress 127.0.0.1 --serverPort 2345 --count 10
```

Options:

| Program | Option | Default | Meaning |
|---|---|---|---|
| server | `--serverPort` | 2345 | port to listen on |
| client | `--serverAddress` | 127.0.0.1 | server IP or name |
| client | `--serverPort` | 2345 | server port |
| client | `--count` | 4 | number of time requests |

On the same machine the offset should be close to 0. For different machines, use the server's IP and allow the port in the firewall.

The server runs until you stop it. On Windows, if Ctrl+C does not work while it waits for a client, use Ctrl+Break.

## Use of LLM

**Model used:** Claude Sonnet 5.5 (Anthropic).

**How I used it:**

1. To understand the main structure of each exercise (what to build, which concepts are involved, and the general approach), without asking for the code.
2. To help write this README.

I also asked it to review my code and explain error messages I got (for example WinError 10054 and an UnboundLocalError). I wrote the code myself.

**Prompts, understanding the structure of the exercises:**

- "here is this lab explain each exercice in details and what is the best approach without really solving them or giving the code"
- "what is the best coding structure to do for exercice one am thinking two files a client and a server then from the command line i do somthing"
- "lets move to the second exercice"
- "what does the server stamp mean and what is bind address"
- "the offset means the diffrence between the client clock and the server clock ?"
- "how to handle the multiple threads situation"

**Prompt, making the README:**

- "make a simple readme.md file dont make it look ai generated just simple english explanation of each program not much detail then explain how to run each code start with exercice 1 then 2 at the end add this part use of LLM model used(the current model) the use understanding the main structure of the exercice and provide the prompts i gave relevent to this making the readme.md file and provide this prompt"
