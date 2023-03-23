import discord
from discord.ext import commands
import pymongo
import random
import asyncio
import json
import copy
from dislash import slash_command, Option, OptionType
from core.core import Core

url='mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]
fight = cluster["RPG"]["fight"]
bossdata = cluster["RPG"]["boss"]


with open("monster.json","r",encoding="utf-8") as monjson:
    mondata = json.load(monjson)
with open("skill.json","r",encoding="utf-8") as data:
    skilldata = json.load(data)


class bossCog(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)

    @slash_command(
      name="fight",description="打架(低機率死亡)",options=[
      Option("user", "挑戰對象", OptionType.USER)]
    )
    async def fight(self, ctx, user = None):
      playerSet1 = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
      if playerSet1 == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet1+"\n但我幫你添了一筆資料")
        return
    
     #check
      check = Core.check(self)
      if check!= None:
        if type(check) == str:
          await ctx.respond(check)
        else:
          await ctx.respond(embed = check)
        return
      
      selfId = self.id
      enemyId = user.id
      self.enemy = enemyId
      player2Set = Core.playerSet(self,rpg.find_one({"id": user.id}))
      if player2Set == "你還沒有登入過啦":
        await ctx.reply("這裡好像沒有這個人ㄟ")
        rpg.find_one({"id": selfId}).enemy = 0
        return
      check = Core.check(self)
      
      if check!= None:
        if type(check) == str:
          await ctx.respond(check)
        else:
          await ctx.respond(embed = check)
          rpg.find_one({"id": selfId}).enemy = 0
        return
      self.enemy = selfId

      if fight.count_documents({"id":ctx.author.id})==0:
          Core.playerSet(self,rpg.find_one({"id":selfId}))
          fight.insert_one(self.result)
          fight.update_one({"id":selfId},{"$set":{"狀態":{}}})
        
          Core.playerSet(self,rpg.find_one({"id":enemyId}))
          fight.insert_one(self.result)
          fight.update_one({"id":enemyId},{"$set":{"狀態":{}}})
      return
        
    