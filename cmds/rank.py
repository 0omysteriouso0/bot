import discord
from discord.ext import commands
import pymongo
import random
import asyncio
from dislash import slash_command, SelectMenu, SelectOption, OptionChoice, Option, OptionType
from dislash import InteractionClient, ActionRow, Button, ButtonStyle

from core.core import Core

url='mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]
bagdata = {}

class rankCog(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)
    @slash_command(name="rank",description="排名", 
                  options=[
                    Option
                    ("value", "想查看的排名", choices = 
                        [ OptionChoice(name = "等級", value = "等級"),
                          OptionChoice(name = "金錢", value = "money"),
                          OptionChoice(name = "生命", value = "maxHp"),
                          OptionChoice(name = "攻擊", value = "Atk"),
                          OptionChoice(name = "防禦", value = "Def"),
                          OptionChoice(name = "敏捷", value = "Agi"),
                          OptionChoice(name = "運氣", value = "Luc"),
                          OptionChoice(name = "死亡數", value = "死亡數")]
                    )
                  ]
                  )
    async def checkbag(self, ctx, value):
      playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
      if playerSet == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
        return
      valuedict = {"等級":"等級",
                   "money":"金錢",
                   "maxHp":"生命",
                   "Atk":"攻擊",
                   "Def":"防禦",
                   "Agi":"敏捷",
                   "Luc":"運氣",
                   "死亡數":"死亡數"
                  }
      rankdict = {}
      for i in rpg.find():
        rankvalue = i[value] + i.get(value+"點",0)
        username = i['name']
        rankdict.update({username:rankvalue})
      scoreboard = sorted(rankdict.items(), key=lambda i : i[1], reverse=True)
      print(scoreboard)
      namelist = [i[0] for i in scoreboard]
      selfrank = namelist.index(self.name) + 1
      embed=discord.Embed(title=f"{valuedict[value]}排行榜",color=0x00d652)
      try:
        embed.set_author(name=f"**第一名:{scoreboard[0][0]}**")
        embed.add_field(name="1st.", value=f"{scoreboard[0][0]}{valuedict[value]}: {scoreboard[0][1]}", inline=False)
        embed.add_field(name="2nd.", value=f"{scoreboard[1][0]}{valuedict[value]}: {scoreboard[1][1]}", inline=False)
        embed.add_field(name="3rd.", value=f"{scoreboard[2][0]}{valuedict[value]}: {scoreboard[2][1]}", inline=False)
        embed.add_field(name="4th.", value=f"{scoreboard[3][0]}{valuedict[value]}: {scoreboard[3][1]}", inline=False)
        embed.add_field(name="5th.", value=f"{scoreboard[4][0]}{valuedict[value]}: {scoreboard[4][1]}", inline=False)
      finally:
        embed.add_field(name=f"-----------------------------\n你是第{selfrank}名", value=f"{scoreboard[selfrank-1][0]}{valuedict[value]}: {scoreboard[selfrank-1][1]}", inline=False)
        await ctx.reply(embed=embed)
      return

def setup(bot):
    bot.add_cog(rankCog(bot))