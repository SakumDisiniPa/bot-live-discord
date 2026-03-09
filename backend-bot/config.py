"""Bot configuration and constants."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
PREFIX = 's!'
TOKEN = os.getenv('DISCORD_TOKEN')

# Lavalink configuration
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD', 'youshallnotpass')
LAVALINK_URI = os.getenv('LAVALINK_URI', 'http://localhost:2333')

# Intents
INTENTS = {
    'message_content': True,
    'voice_states': True
}

