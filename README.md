## SPACE BOT
A Python powered Slack bot built with 'SLACK_BOLT' that delivers space exploration imagery and exploration data directly on slack channels using official NASA API and Block kit.It also provides a real-time ISS location as per longitudes and latitudes.

[Download the demo video for reference](./Demo_vid.mp4)

## Quick Start
Try using these commands first:
1. /nasa-stream 
2. /nasa-mars-rover
3. /iss-location
4. /space-fact
5. /space-jokes


## Features
* **Socket Mode Integration:** Runs continuously using WebSockets without requiring public webhooks.
* **NASA API Integration:** Connects with official NASA media search to get high resolution "PICTURE OF THE DAY".

### Prerequisites
* Python 3.10+
* Slack App configured with Socket Mode and Slash Commands

## Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/rr-codes4/Slack-bot.git](https://github.com/rr-codes4/Slack-bot.git)
   cd Slack-bot
