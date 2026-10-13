import os #Seriously VVIP!!!!!!
import random 
import time #to handle retries for NASA API calls
import json #Meeting json you know
from pathlib import Path #to handle the .env file path

import requests #to handle API calls
from dotenv import load_dotenv #to load environment variables from .env filesss
from slack_bolt import App #we need it
from slack_bolt.adapter.socket_mode import SocketModeHandler

#Loading environment variables from local for.env file
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
    """Dad jokes but make them astronomical :|"""
    jokes = [
        "Why did the astronaut break up with his girlfriend? He needed space.",
        "Why did the sun go to school? To get a little brighter.",
        "Why did the alien go to school? To improve his 'space'ial skills.",
        "Why did the astronaut bring a broom to space? Because he wanted to sweep the galaxy.",
    ]
    respond(f" **Space Joke**: {random.choice(jokes)}")


#PHYSICS & UTILS 

@app.command("/orbit-force")
def handle_gravity_calc(ack, respond, command):
    ack()
    try:
        #Expecting inputs: mass1, mass2, distance
        args = command['text'].split()
        m1 = float(args[0])
        m2 = float(args[1])
        r = float(args[2])
        
        #Universal gravitational constant aaaaaaaaaaa
        G = 6.67430e-11  
        force = G * (m1 * m2) / (r ** 2)
        
        respond(f" The gravitational force between the two masses is: {force:.2e} N")
    except Exception:
        respond(" Usage format: `/orbit-force <mass1> <mass2> <distance>` (mass in kg, distance in meters).")



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

#This one always works,it shows pictures of curiosity roves 
@app.command("/nasa-mars-rover")
def handle_nasa_mars_rover(ack, respond):
    ack()
    try:
        url = "https://images-api.nasa.gov/search"
        params = {
            "q": "mars rover curiosity",
            "media_type": "image"
        }
        
        response = requests.get(url, params=params, timeout=10) #timeout to avoid hanging
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
        respond(f" I am facing issues fetching the data,please try again later: {e}")

import requests
#Iss loc as per latitude and longitude
@app.command("/iss-location")
def handle_iss_location(ack, respond):
    ack()

    try:
        response = requests.get(
            "https://api.open-notify.org/iss-now.json",
            timeout=(5, 10),
        )
        response.raise_for_status()

        data = response.json()
        position = data["iss_position"]

        lat = float(position["latitude"])
        lon = float(position["longitude"])

        respond(
            "*🛰️ International Space Station Location*\n" #it helps
            f"• Latitude: `{lat:.4f}`\n"
            f"• Longitude: `{lon:.4f}`\n"
            f"<https://www.google.com/maps?q={lat},{lon}|"
            "View location on map>"
        )

    except (requests.RequestException, ValueError, KeyError, TypeError):
        respond(
            "🛰️ I couldn't retrieve the ISS location right now. "
            "Please try again shortly."
        )

#Fetches APOD and posts it to Slack.In the format that is devised 
@app.command("/nasa-stream")
def handle_nasa_stream(ack, respond):
    ack()

    data = None

    for attempt in range(2):
        try:
            response = requests.get(
                "https://api.nasa.gov/planetary/apod",
                params={"api_key": NASA_API_KEY},#
                timeout=(3, 10),
            )
            response.raise_for_status()
            data = response.json()
            break

        except (requests.RequestException, ValueError):
            if attempt == 0:
                time.sleep(1)

    if data is None:
        respond(
            " NASA's service could not be reached. "
            "Please try `/nasa-stream` again shortly."
        )
        return

    if data.get("error"): 
        error = data["error"]
        message = (
            error.get("message", "NASA returned an API error.")
            if isinstance(error, dict)
            else str(error)
        )
        respond(f"NASA API error: {message[:300]}")
        return

    title = str(data.get("title") or "NASA Picture of the Day")
    explanation = str(
        data.get("explanation") or "No explanation available."
    )[:2500]
    image_url = data.get("url")
    media_type = data.get("media_type")

    if not image_url or media_type not in ("image", "video"):
        respond("NASA returned incomplete or unsupported APOD data.")
        return

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"NASA Daily View: {title}"[:150],
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": explanation,
            },
        },
    ]

    if media_type == "image":
        blocks.insert(1, {
            "type": "image",
            "image_url": image_url,
            "alt_text": title[:2000] or "NASA astronomy image",
        }) #scrapping through pixels !
    else:
        blocks.insert(1, {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<{image_url}|Watch today's NASA feature>",
            },
        })

    try:
        respond(blocks=blocks)
    except Exception:
        #Logging the actual error in the server logs
        app.logger.exception("Failed to send NASA stream response")



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




#firing up the app using Socket Mode
if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()