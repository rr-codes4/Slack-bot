import os
import random
import time
import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

#Load environment variables from local for.env file
load_dotenv(Path(__file__).with_name("for.env"))

#Grabing API keys and tokens from the environment
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
NASA_API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")

#Initializing the Slack app using Socket Mode
app = App(token=SLACK_BOT_TOKEN)


#some basic commands for fun and engagement

@app.command("/space-fact")
def handle_space_fact_command(ack, respond):
    ack()
    #Random cosmic trivia to drop in chat
    facts = [
        "Neutron stars can spin at a rate of 600 rotations per second.",
        "A day on Venus is longer than a year on Venus.",
        "Jupiter's Great Red Spot is a giant storm that has been raging for at least 400 years.",
        "The largest volcano in the solar system is Olympus Mons on Mars.",
        "There are more stars in the universe than grains of sand on all the beaches on Earth.",
    ]
    respond(f" **Space Fact**: {random.choice(facts)}")


@app.command("/space-joke")
def handle_space_joke_command(ack, respond):
    ack()
    #Dad jokes but make them astronomical :|
    jokes = [
        "Why did the astronaut break up with his girlfriend? He needed space.",
        "Why did the sun go to school? To get a little brighter.",
        "Why did the alien go to school? To improve his 'space'ial skills.",
        "Why did the astronaut bring a broom to space? Because he wanted to sweep the galaxy.",
    ]
    respond(f"🚀 **Space Joke**: {random.choice(jokes)}")


# --- PHYSICS & UTILS --

@app.command("/orbit-force")
def handle_gravity_calc(ack, respond, command):
    ack()
    try:
        #Expecting inputs: mass1, mass2, distance
        args = command['text'].split()
        m1 = float(args[0])
        m2 = float(args[1])
        r = float(args[2])
        
        #Universal gravitational constant
        G = 6.67430e-11  
        force = G * (m1 * m2) / (r ** 2)
        
        respond(f"🌌 The gravitational force between the two masses is: {force:.2e} N")
    except Exception:
        respond("⚠️ Usage format: `/orbit-force <mass1> <mass2> <distance>` (mass in kg, distance in meters).")



#This one only if you want the link 
@app.command("/nasa-apod")  
def handle_nasa_apod(ack, respond):
    ack()
    data = None
    
    #Try up to 3 times in case NASA's API is acting sluggish
    for attempt in range(3):
        try:
            response = requests.get(
                "https://api.nasa.gov/planetary/apod",
                params={"api_key": NASA_API_KEY},
                timeout=(5, 20),
            )
            response.raise_for_status()
            data = response.json()
            break
        except requests.RequestException:
            if attempt < 2:
                time.sleep(attempt + 1)

    if data is None:
        respond("NASA's APOD service is taking too long to respond. Please try again shortly.")
        return

    if data.get("error"):
        respond(f"NASA could not return APOD: {data['error'].get('message', 'Unknown API error')}")
        return

    title = data.get('title', 'NASA Picture of the day')
    image_url = data.get('url', '')
    explanation = data.get('explanation', '')[:200]
    respond(f"**{title}**\n{image_url}\n\n_{explanation}_")


@app.command("/nasa-mars-rover")
def handle_nasa_mars_rover(ack, respond):
    ack()
    try:
        url = "https://images-api.nasa.gov/search"
        params = {
            "q": "mars rover curiosity",
            "media_type": "image"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        items = data.get("collection", {}).get("items", [])
        if not items:
            respond(" No Mars Rover photos found right now.")
            return
            
        first_item = items[0]
        item_data = first_item.get("data", [{}])[0]
        links = first_item.get("links", [{}])

        title = item_data.get("title", "Mars Rover Photo")
        description = item_data.get("description", "Mars Surface View")[:200] + "..."
        date_created = item_data.get("date_created", "")[:10]
        image_url = links[0].get("href", "") if links else ""

        #Building a nice rich Block Kit message for Slack
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🔴 Mars Rover: {title[:120]}"}
            },
            {
                "type": "image",
                "image_url": image_url,
                "alt_text": "Mars Rover Photo"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 *Date:* {date_created}\n\n{description}"
                }
            }
        ]
        
        respond(blocks=blocks)

    except Exception as e:
        respond(f" Could not fetch Mars Rover image: {e}")


@app.command("/iss-location")
def handle_iss_location(ack, respond):
    ack()
    try:
        #Quick lookup for where the ISS is floating right now
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=5)
        data = response.json()

        lat = data['iss_position']['latitude']
        lon = data['iss_position']['longitude']

        respond(f"The current location of the ISS is:\nLatitude: {lat}\nLongitude: {lon}")
    except Exception as e:
        respond(f"Error fetching ISS location: {str(e)}")

#Time for some stream 
@app.command("/nasa-stream")
def handle_nasa_stream(ack, respond):
    ack()
    data = None

    #Give NASA a few retries because the APOD endpoint can be moody
    for attempt in range(3):
        try:
            response = requests.get(
                "https://api.nasa.gov/planetary/apod",
                params={"api_key": NASA_API_KEY},
                timeout=25,
            )
            response.raise_for_status()
            data = response.json()
            break 
        except requests.RequestException:
            time.sleep(1)

    if not data:
        respond("🚀 NASA's servers are taking a bit longer than usual. Try `/nasa-stream` again in a second!")
        return

    try:
        if data.get("error"):
            raise RuntimeError(data["error"].get("message", "NASA returned an error"))

        title = data.get('title', 'NASA Picture of the Day')
        image_url = data.get('url', '')
        explanation = data.get('explanation', '')[:300]
        media_type = data.get('media_type')

        if not image_url or media_type not in {"image", "video"}:
            raise ValueError("Incomplete APOD response")

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"NASA Daily View: {title}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": explanation or "No explanation available."}
            }
        ]

        if media_type == "image":
            blocks.insert(1, {
                "type": "image",
                "image_url": image_url,
                "alt_text": title,
            })
        else:
            blocks.insert(1, {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"<{image_url}|Watch today's NASA feature>"},
            })

        respond(blocks=blocks)

    except (ValueError, RuntimeError):
        respond("⚠️ Could not parse NASA APOD data right now. Give it a moment!")


# --- QUIZ & HELP ---

@app.command("/astro-quiz")
def handle_astro_quiz(ack, respond):
    ack()
    questions = [
        {
            "question": "What is the largest planet in our solar system?",
            "options": ["Earth", "Jupiter", "Saturn", "Mars"],
            "answer": "Jupiter"
        },
        {
            "question": "What is the closest star to Earth?",
            "options": ["Proxima Centauri", "Sirius", "Alpha Centauri A", "The Sun"],
            "answer": "The Sun"
        },
        {
            "question": "What is the name of the galaxy that contains our Solar System?",
            "options": ["Andromeda Galaxy", "Milky Way Galaxy", "Triangulum Galaxy", "Whirlpool Galaxy"],
            "answer": "Milky Way Galaxy"
        }
    ]
    quiz = random.choice(questions)
    options_text = "\n".join([f"{i+1}. {option}" for i, option in enumerate(quiz["options"])])
    respond(f"**Quiz Time!**\n{quiz['question']}\n{options_text}\n\nReply with the number of your answer.")


@app.command("/astro-help")
def handle_help(ack, respond):
    ack()
    help_text = (
        "*AstroBot Commands Guide*\n\n"
        "1. `/orbit-force <m1> <m2> <dist>` - Calculate gravitational force\n"
        "2. `/nasa-stream` - Get NASA's Astronomy Picture of the Day\n"
        "3. `/nasa-mars-rover` - Get a random photo from the Mars Rover\n"
        "4. `/iss-location` - Check where the ISS is floating right now\n"
        "5. `/space-fact` - Drop a random space fact\n"
        "6. `/space-joke` - Tell a terrible space dad-joke\n"
        "7. `/astro-quiz` - Test your astronomy knowledge\n"
        "8. `/astro-help` - Show this help menu"
    )
    respond(help_text)


#fire up the app using Socket Mode
if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()