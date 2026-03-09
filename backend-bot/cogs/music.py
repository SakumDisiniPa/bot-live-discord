"""Music commands cog."""
import discord
import wavelink
from discord.ext import commands


class Music(commands.Cog):
    """Music playback commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    # ==================== HELPERS ====================
    
    async def _get_player(self, ctx):
        """Get or create player for guild."""
        voice_channel = ctx.author.voice.channel
        
        player = voice_channel.guild.voice_client
        if player is None:
            player = await voice_channel.connect(cls=wavelink.Player, self_deaf=True)
            await player.set_volume(100)
        elif player.channel != voice_channel:
            await player.move_to(voice_channel)
        
        return player
    
    async def _check_voice(self, ctx):
        """Check if user is in voice channel."""
        if not ctx.author.voice:
            await ctx.send('❌ You must be in a voice channel first!')
            return False
        return True
    
    async def _check_player(self, ctx):
        """Check if bot is in voice channel."""
        player = ctx.guild.voice_client
        if player is None:
            await ctx.send('❌ Bot is not in a voice channel!')
            return None
        return player
    
    # ==================== COMMANDS ====================
    
    @commands.command(name='p', help='Play music from YouTube or Spotify')
    async def play(self, ctx, *, query: str):
        """Play audio from YouTube, Spotify, or other sources."""
        if not await self._check_voice(ctx):
            return
        
        try:
            player = await self._get_player(ctx)
        except Exception as e:
            await ctx.send(f'❌ Error connecting to voice channel: {str(e)}')
            return
        
        await ctx.send(f'🔍 Searching for: `{query}`')
        
        try:
            tracks = await wavelink.Playable.search(query)
            
            if not tracks:
                await ctx.send('❌ No tracks found!')
                return
            
            track = tracks[0]
            await player.queue.put_wait(track)
            
            if not player.playing:
                track_to_play = await player.queue.get_wait()
                await player.play(track_to_play)
                await ctx.send(f'▶️ Now playing: **{track_to_play.title}** by `{track_to_play.author}`')
            else:
                await ctx.send(f'✅ Added to queue: **{track.title}** by `{track.author}`')
        
        except Exception as e:
            await ctx.send(f'❌ Error: {str(e)}')
            print(f'Error: {e}')
    
    @commands.command(name='stop', help='Stop music and disconnect')
    async def stop(self, ctx):
        """Stop the music and disconnect from voice."""
        player = await self._check_player(ctx)
        if not player:
            return
        
        await player.stop()
        await player.disconnect()
        await ctx.send('⏹️ Music stopped and disconnected!')
    
    @commands.command(name='pause', help='Pause the current song')
    async def pause(self, ctx):
        """Pause the current song."""
        player = await self._check_player(ctx)
        if not player:
            return
        
        if player.playing:
            await player.pause(True)
            await ctx.send('⏸️ Music paused!')
        else:
            await ctx.send('❌ Nothing is playing!')
    
    @commands.command(name='resume', help='Resume the paused song')
    async def resume(self, ctx):
        """Resume the paused song."""
        player = await self._check_player(ctx)
        if not player:
            return
        
        if player.paused:
            await player.pause(False)
            await ctx.send('▶️ Music resumed!')
        else:
            await ctx.send('❌ No paused music to resume!')
    
    @commands.command(name='skip', help='Skip to next song')
    async def skip(self, ctx):
        """Skip the current song."""
        player = await self._check_player(ctx)
        if not player:
            return
        
        if player.queue.is_empty:
            await player.stop()
            await ctx.send('⏭️ No more songs in queue!')
        else:
            await player.skip()
            await ctx.send('⏭️ Skipped to next song!')
    
    @commands.command(name='join', help='Join your voice channel')
    async def join(self, ctx):
        """Join the user's voice channel."""
        if not await self._check_voice(ctx):
            return
        
        try:
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
            await player.set_volume(100)
            await ctx.send(f'✅ Joined {ctx.author.voice.channel.name}!')
        except Exception as e:
            await ctx.send(f'❌ Error: {str(e)}')
    
    @commands.command(name='leave', help='Leave the voice channel')
    async def leave(self, ctx):
        """Leave the voice channel."""
        player = await self._check_player(ctx)
        if not player:
            return
        
        await player.disconnect()
        await ctx.send('👋 Left the voice channel!')
    
    @commands.command(name='queue', help='Show current queue')
    async def queue_cmd(self, ctx):
        """Show the current queue."""
        player = await self._check_player(ctx)
        if not player:
            return
        
        if player.queue.is_empty and not player.playing:
            await ctx.send('📭 Queue is empty!')
            return
        
        embed = discord.Embed(title='🎵 Music Queue', color=discord.Color.blue())
        
        if player.playing:
            embed.add_field(
                name='Currently Playing',
                value=f'**{player.current.title}** by `{player.current.author}`',
                inline=False
            )
        
        if not player.queue.is_empty:
            queue_list = '\n'.join([
                f'{i+1}. **{track.title}** by `{track.author}`'
                for i, track in enumerate(list(player.queue)[:10])
            ])
            embed.add_field(
                name=f'Up Next ({len(player.queue)} songs)',
                value=queue_list,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='now', help='Show current playing song')
    async def now(self, ctx):
        """Show current playing song."""
        player = await self._check_player(ctx)
        if not player:
            return
        
        if not player.playing:
            await ctx.send('❌ Nothing is playing!')
            return
        
        track = player.current
        embed = discord.Embed(title='🎵 Now Playing', color=discord.Color.green())
        embed.add_field(name='Title', value=track.title, inline=False)
        embed.add_field(name='Author', value=track.author, inline=False)
        
        duration = f'{int(track.length / 1000 / 60)}:{int((track.length / 1000) % 60):02d}'
        embed.add_field(name='Duration', value=duration, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='commands', help='Show all commands')
    async def commands_list(self, ctx):
        """Show all available commands."""
        embed = discord.Embed(title='🎵 Music Bot Commands', color=discord.Color.blue())
        
        commands_info = [
            ('s!p <query>', 'Play music from YouTube/Spotify'),
            ('s!pause', 'Pause the current song'),
            ('s!resume', 'Resume the paused song'),
            ('s!skip', 'Skip to next song'),
            ('s!stop', 'Stop music and disconnect'),
            ('s!join', 'Join your voice channel'),
            ('s!leave', 'Leave the voice channel'),
            ('s!queue', 'Show current queue'),
            ('s!now', 'Show current playing song'),
        ]
        
        for name, value in commands_info:
            embed.add_field(name=name, value=value, inline=False)
        
        embed.set_footer(text='Enjoy your music! 🎶')
        await ctx.send(embed=embed)

