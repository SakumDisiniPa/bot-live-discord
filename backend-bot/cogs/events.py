"""Event handlers cog."""
import wavelink
import config
from discord.ext import commands


class Events(commands.Cog):
    """Bot event handlers."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when bot is ready."""
        print(f'✅ Bot logged in as {self.bot.user}')
        await self._setup_lavalink()
        print(f'📡 Bot is ready to stream music!')
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload):
        """Called when a Lavalink node is ready."""
        print(f'✅ Lavalink Node is ready!')
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        """Called when a track ends."""
        print(f'🎵 Track ended: {track.title}')
    
    async def _setup_lavalink(self):
        """Setup Lavalink connection."""
        node = wavelink.Node(
            uri=config.LAVALINK_URI,
            password=config.LAVALINK_PASSWORD
        )
        
        try:
            await wavelink.Pool.connect(nodes=[node], client=self.bot)
            print('✅ Connected to Lavalink!')
        except Exception as e:
            print(f'❌ Failed to connect to Lavalink: {e}')
            print('⚠️ Make sure Lavalink server is running on localhost:2333')

