"""Cogs loader."""
import asyncio


async def setup(bot):
    """Setup all cogs."""
    from . import music, events
    
    await bot.add_cog(music.Music(bot))
    await bot.add_cog(events.Events(bot))
    
    print('✅ All cogs loaded!')

