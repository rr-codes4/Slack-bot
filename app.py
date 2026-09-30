import os
from dotenv import load_dotenv
load_dotenv()
import random
import requests
import json
import time
import urllib.request
from slack_bolt import App  
from slack_bolt.adapter.socket_mode import SocketModeHandler 
NASA_API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")
params = {"api_key": NASA_API_KEY}

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
NASA_API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")


app = App(token=SLACK_BOT_TOKEN)

@app.command("/space-fact")
def handle_space_fact_command(ack,respond):
    ack()
    facts = [
        "Neutron stars can spin at a rate of 600 rotations per second.",
        "A day on Venus is longer than a year on Venus.",
        "JUpiter's Great Red Spot is a giant storm that has been raging for at least 400 years.",
        "The largest volcano in the solar system is Olympus Mons on Mars.",
        "There are more stars in the universe than grains of sand on all the beaches on Earth.",
    ]
    respond(f"🌃**Space Fact**: {random.choice(facts)}")
@app.command("/space-joke")
def handle_space_joke_command(ack, respond):
    ack()
    jokes = [
        "Why did the astronaut break up with his girlfriend? He needed space.",
        "Why did the sun go to school? To get a little brighter.",
        "Why did the alien go to school? To improve his 'space'ial skills.",
        "Why did the astronaut bring a broom to space? Because he wanted to sweep the galaxy.",
    ]
    respond(f"🚀**Space Joke**: {random.choice(jokes)}")

@app.command("/orbit-force")
def handle_gravity_calc(ack,respond, command):
    ack()
    try:
        args = command['text'].split()
        m1 = float(args[0])
        m2 = float(args[1])
        r = float(args[2])
        G = 6.67430e-11  # Gravitational constant
        force = G * (m1 * m2) / (r ** 2)
        respond(f"🌌 The gravitational force between the two masses is: {force:.2e} N")
    except Exception:
        respond("Please use format: '/orbit-force <mass1> <mass2> <distance>' where mass is in kg and distance is in meters.")




import urllib.request
import json
@app.command("/nasa-apod")  
def handle_nasa_apod(ack, respond):
    ack()
    try:
        url = "https://api.nasa.gov/planetary/apod"
        req = urllib.request.urlopen(f"{url}?api_key={NASA_API_KEY}")
        data = json.loads(req.read().decode('utf-8'))

        title = data.get('title', 'NASA Picture of the day')
        image_url = data.get('url' , '')
        explanation = data.get('explanation', '')[:200]

        respond(f"**{title}**\n{image_url}\n\n_{explanation}_")
    except Exception as e:
        respond(f"Error fetching NASA APOD: {str(e)}")

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
            respond("🔴 No Mars Rover photos found right now.")
            return
        first_item = items[0]
        item_data = first_item.get("data", [{}])[0]
        links = first_item.get("links", [{}])

        title = item_data.get("title", "Mars Rover Photo")
        description = item_data.get("description", "Mars Surface View")[:200] + "..."
        date_created = item_data.get("date_created", "")[:10]
        image_url = links[0].get("href", "") if links else ""

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
        respond(f"⚠️ Could not fetch Mars Rover image: {e}")




@app.command("/iss-location")
def handle_iss_location(ack, respond):
    ack()
    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=5)
        data = response.json()

        lat = data['iss_position']['latitude']
        lon = data['iss_position']['longitude']

        respond(f"The current location of the ISS is:\nLatitude: {lat}\nLongitude: {lon}")
    except Exception as e:
        respond(f"Error fetching ISS location: {str(e)}")

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
def handle_help(ack,respond):
    ack()
    respond(f"*Space Bot Commands Guide:*\n\n")
    help_text = (
        "**AstroBot Commands Guide**\n\n"
        "1. '/space-calc [type] [args]' - Calculate Physics Formulas (escape,force)\n"
        "2. '/nasa-stream' - Get NASA's Astronomy Picture of the Day\n" \
        "3. '/nasa-mars-rover' - Get a random photo from NASA's Mars Rover\n" \
        "4. '/iss-location' - Get the current location of the International Space Station\n" \
        "5. '/space-fact' - Get a random space fact\n" \
        "6. '/space-joke' - Get a random space joke\n" \
        "7. '/astro-quiz' - Take a random astronomy quiz\n" \
        "8. '/astro-help' - Show this help message\n" \
        
    )

@app.command("/nasa-stream")
def handle_nasa_stream(ack, respond):
    ack()
    
    data = None
    last_error = None

    #Retry up to 3 times to handle NASA API slowness/timeouts
    for attempt in range(3):
        try:
            response = requests.get(
                "https://api.nasa.gov/planetary/apod",
                params={"api_key": NASA_API_KEY},
                timeout=25,  # Increased timeout from 10s to 25s
            )
            response.raise_for_status()
            data = response.json()
            break  # Success! Exit loop
        except requests.RequestException as err:
            last_error = err
            time.sleep(1)  # Wait 1s before retrying

    #Fallback if NASA completely fails after 3 retries
    if not data:
        respond(
            "🚀 NASA's servers are taking a bit longer than usual to respond. "
            "Please try running `/nasa-stream` again in a few seconds!"
        )
        return

    try:
        if data.get("error"):
            raise RuntimeError(data["error"].get("message", "NASA returned an error"))

        title = data.get('title', 'NASA Picture of the Day')
        image_url = data.get('url', '')
        explanation = data.get('explanation', '')[:300]
        media_type = data.get('media_type')

        if not image_url or media_type not in {"image", "video"}:
            raise ValueError("NASA returned an incomplete APOD response")

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

    except (ValueError, RuntimeError) as error:
        respond("⚠️ Could not parse NASA APOD data right now. Please try again in a moment!")
   

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start() 