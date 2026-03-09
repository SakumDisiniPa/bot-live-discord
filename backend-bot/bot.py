import discord
from discord.ext import commands
import wavelink
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='s!', intents=intents)

# Global variable to store player
players = {}

def get_player(guild_id):
    return players.get(guild_id)

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    await setup_lavalink()
    print(f'📡 Bot is ready to stream music!')

async def setup_lavalink():
    """Setup Lavalink connection"""
    lavalink_password = os.getenv('LAVALINK_PASSWORD', 'Padaherang') # Pastikan password sama dengan application.yml
    lavalink_uri = os.getenv('LAVALINK_URI', 'http://127.0.0.1:2333') # Pakai IP langsung
    
    # Tambahkan parameter heartbeat untuk mencegah disconnect code 1006
    node = wavelink.Node(
        uri=lavalink_uri,
        password=lavalink_password,
        heartbeat=30 
    )
    
    try:
        # Di Wavelink v3, gunakan connect dengan list nodes
        await wavelink.Pool.connect(nodes=[node], client=bot, cache_capacity=100)
        print('✅ Connected to Lavalink!')
    except Exception as e:
        print(f'❌ Failed to connect to Lavalink: {e}')

@bot.event
async def on_wavelink_node_ready(payload) -> None:
    """Called when a node is ready"""
    print(f'✅ Lavalink Node is ready!')

@bot.event
async def on_wavelink_node_error(payload):
    print(f"❌ Wavelink Node Error: {payload.node.identifier} | {payload.error}")

@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Playable, reason: str) -> None:
    """Called when a track ends"""
    print(f'🎵 Track ended: {track.title}')

@bot.event
async def on_wavelink_track_exception(payload):
    print(f"❌ Track Exception: {payload.exception}")

@bot.command(name='p', help='Play music from YouTube or Spotify')
async def play(ctx, *, query: str):
    """Play audio from YouTube, Spotify, or other sources"""
    
    # Check if user is in voice channel
    if not ctx.author.voice:
        await ctx.send('❌ You must be in a voice channel first!')
        return
    
    voice_channel = ctx.author.voice.channel
    
    # Get or create player
    try:
        player: wavelink.Player = voice_channel.guild.voice_client
        if player is None:
            player = await voice_channel.connect(cls=wavelink.Player, self_deaf=True)
            # Set default volume to 100%
            await player.set_volume(100)
        elif player.channel != voice_channel:
            await player.move_to(voice_channel)
    except Exception as e:
        await ctx.send(f'❌ Error connecting to voice channel: {str(e)}')
        return
    
    await ctx.send(f'🔍 Searching for: `{query}`')
    
    try:
        # Search for track
        tracks = await wavelink.Playable.search(query)
        
        if not tracks:
            await ctx.send('❌ No tracks found!')
            return
        
        track = tracks[0]
        await player.queue.put_wait(track)
        
        # Jika player belum main, ambil lagu dari queue dan putar
        if not player.playing:
            track = await player.queue.get_wait()
            await player.play(track)
            await ctx.send(f'▶️ Now playing: **{track.title}** by `{track.author}`')
        else:
            await ctx.send(f'✅ Added to queue: **{track.title}** by `{track.author}`')
        
    except Exception as e:
        await ctx.send(f'❌ Error: {str(e)}')
        print(f'Error: {e}')

@bot.command(name='stop', help='Stop music and disconnect')
async def stop(ctx):
    """Stop the music and disconnect from voice"""
    player = ctx.guild.voice_client
    
    if player is None:
        await ctx.send('❌ Bot is not in a voice channel!')
        return
    
    await player.stop()
    await player.disconnect()
    await ctx.send('⏹️ Music stopped and disconnected!')

@bot.command(name='pause', help='Pause the current song')
async def pause(ctx):
    """Pause the current song"""
    player = ctx.guild.voice_client
    
    if player is None:
        await ctx.send('❌ Bot is not in a voice channel!')
        return
    
    if player.playing:
        await player.pause(True)
        await ctx.send('⏸️ Music paused!')
    else:
        await ctx.send('❌ Nothing is playing!')

@bot.command(name='resume', help='Resume the paused song')
async def resume(ctx):
    """Resume the paused song"""
    player = ctx.guild.voice_client
    
    if player is None:
        await ctx.send('❌ Bot is not in a voice channel!')
        return
    
    if player.paused:
        await player.pause(False)
        await ctx.send('▶️ Music resumed!')
    else:
        await ctx.send('❌ No paused music to resume!')

@bot.command(name='skip', help='Skip to next song')
async def skip(ctx):
    """Skip the current song"""
    player = ctx.guild.voice_client
    
    if player is None:
        await ctx.send('❌ Bot is not in a voice channel!')
        return
    
    if player.queue.is_empty:
        await player.stop()
        await ctx.send('⏭️ No more songs in queue!')
    else:
        await player.skip()
        await ctx.send('⏭️ Skipped to next song!')

@bot.command(name='join', help='Join your voice channel')
async def join(ctx):
    """Join the user's voice channel"""
    if not ctx.author.voice:
        await ctx.send('❌ You must be in a voice channel!')
        return
    
    voice_channel = ctx.author.voice.channel
    
    try:
        player = await voice_channel.connect(cls=wavelink.Player, self_deaf=True)
        await player.set_volume(100)
        await ctx.send(f'✅ Joined {voice_channel.name}!')
    except Exception as e:
        await ctx.send(f'❌ Error: {str(e)}')

@bot.command(name='leave', help='Leave the voice channel')
async def leave(ctx):
    """Leave the voice channel"""
    player = ctx.guild.voice_client
    
    if player is None:
        await ctx.send('❌ Bot is not in a voice channel!')
        return
    
    await player.disconnect()
    await ctx.send('👋 Left the voice channel!')

@bot.command(name='queue', help='Show current queue')
async def queue_cmd(ctx):
    """Show the current queue"""
    player = ctx.guild.voice_client
    
    if player is None:
        await ctx.send('❌ Bot is not in a voice channel!')
        return
    
    if player.queue.is_empty and not player.playing:
        await ctx.send('📭 Queue is empty!')
        return
    
    embed = discord.Embed(title='🎵 Music Queue', color=discord.Color.blue())
    
    if player.playing:
        embed.add_field(name='Currently Playing', value=f'**{player.current.title}** by `{player.current.author}`', inline=False)
    
    if not player.queue.is_empty:
        queue_list = '\n'.join([f'{i+1}. **{track.title}** by `{track.author}`' for i, track in enumerate(list(player.queue)[:10])])
        embed.add_field(name=f'Up Next ({len(player.queue)} songs)', value=queue_list, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='now', help='Show current playing song')
async def now(ctx):
    """Show current playing song"""
    player = ctx.guild.voice_client
    
    if player is None:
        await ctx.send('❌ Bot is not in a voice channel!')
        return
    
    if not player.playing:
        await ctx.send('❌ Nothing is playing!')
        return
    
    track = player.current
    embed = discord.Embed(title='🎵 Now Playing', color=discord.Color.green())
    embed.add_field(name='Title', value=track.title, inline=False)
    embed.add_field(name='Author', value=track.author, inline=False)
    embed.add_field(name='Duration', value=f'{int(track.length / 1000 / 60)}:{int((track.length / 1000) % 60):02d}', inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='commands', help='Show all commands')
async def commands_list(ctx):
    """Show all available commands"""
    embed = discord.Embed(title='🎵 Music Bot Commands', color=discord.Color.blue())
    embed.add_field(name='s!p <query>', value='Play music from YouTube/Spotify', inline=False)
    embed.add_field(name='s!pause', value='Pause the current song', inline=False)
    embed.add_field(name='s!resume', value='Resume the paused song', inline=False)
    embed.add_field(name='s!skip', value='Skip to next song', inline=False)
    embed.add_field(name='s!stop', value='Stop music and disconnect', inline=False)
    embed.add_field(name='s!join', value='Join your voice channel', inline=False)
    embed.add_field(name='s!leave', value='Leave the voice channel', inline=False)
    embed.add_field(name='s!queue', value='Show current queue', inline=False)
    embed.add_field(name='s!now', value='Show current playing song', inline=False)
    embed.set_footer(text='Enjoy your music! 🎶')
    
    await ctx.send(embed=embed)

# Run the bot
if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print('❌ Error: DISCORD_TOKEN not found in .env file!')
        print('Please create .env file with DISCORD_TOKEN=your_token')
        exit(1)
    bot.run(TOKEN)
