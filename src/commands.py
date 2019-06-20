import discord
from discord.ext import commands
import datetime
import configloader as cfload
import praw, random
import subprocess

cfload.read("..\\config.ini")
print(cfload.configSectionMap("Owner Credentials")['owner_id'], "is the owner. Only he can use /shutdown.")

class Commands(commands.Cog):
    prune_cutoff = 25

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong! ({} ms)".format(round(self.bot.latency, 2)))

    @commands.command(aliases = ["clean", "purge"])
    async def prune(self, ctx, n = 1):
        '''Deletes n messages.'''
        n = abs(n)
        if n > Commands.prune_cutoff:
            await ctx.channel.send("You can only delete up to 25 messages at a time.")
            return
        print(f"Purging {n + 1} message(s)...") #accounts for command invoke
        await ctx.message.remove_reaction("\U000023F3", ctx.me) #hourglass not done
        await ctx.channel.purge(limit=n + 1)
        title = f'{ctx.message.author} deleted {n} message'
        title += 's!' if n > 1 else '!'
        embed = discord.Embed(title=title, colour=discord.Colour(0xe7d066))
        await ctx.send(embed=embed)

    @commands.command(aliases=['sd'])
    async def shutdown(self, ctx):
        '''Shuts down the bot.'''
        if ctx.author.id == int(cfload.configSectionMap("Owner Credentials")["owner_id"]):
            await ctx.message.add_reaction("\U0001F50C") #power plug emoji
            await self.bot.logout()
        else:
            await ctx.message.add_reaction('\U0000274C') #Cross mark
            await ctx.send("You can't shut me down.", delete_after=15)

    @commands.command()
    async def update(self, ctx):
        """Shuts down the bot, updates the repo, and restarts using start.sh."""
        if ctx.author.id == int(cfload.configSectionMap("Owner Credentials")["owner_id"]):
            await ctx.message.add_reaction("\U0001F50C") #power plug emoji
            await self.bot.logout()
            subprocess.call(['../update_git.sh'])
        else:
            await ctx.message.add_reaction('\U0000274C') #Cross mark

    @commands.command()
    async def meme(self, ctx, subreddit='dankmemes'):
        """Gets a random meme from reddit and posts it.
        Specify a subreddit to get a post from (actually works with any sub). Default is r/dankmemes."""
        #Load the reddit login and bot credentials from config.ini
        credentials = cfload.configSectionMap("Reddit API")

        await ctx.message.add_reaction("\U0000231B")  # hourglass done (not actually done)

        r = praw.Reddit(client_id=credentials['client_id'],
                           client_secret=credentials['client_secret'],
                           user_agent=credentials['user_agent'],
                           username=credentials['username'],
                           password=credentials['password'])
        try:
            sub = r.subreddit(subreddit)
            if sub.over18:
                return await ctx.message.add_reaction("\U0001F6AB") #Prohibited
            posts = sub.hot(limit=100)
            rand = random.randint(0, 100)
            for i, post in enumerate(posts):
                if i == rand:
                    await ctx.send(post.url)
        except Exception:
            await ctx.message.add_reaction("\U0000274C") #Cross mark
        finally:
            await ctx.message.remove_reaction('\U0000231B', ctx.me)


def setup(bot):
    bot.add_cog(Commands(bot))
