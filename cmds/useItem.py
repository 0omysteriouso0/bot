import discord
from discord.ext import commands
import pymongo
import random
import asyncio
import json
from dislash import slash_command, SelectMenu, SelectOption, Option, OptionType
from dislash import InteractionClient, ActionRow, Button, ButtonStyle

from core.core import Core

url='mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]

with open("food.json","r",encoding="utf-8") as data:
    fooddata = json.load(data)
with open("skill.json","r",encoding="utf-8") as data:
    skilldata = json.load(data)
  
async def learncode(self, ctx, skill = None):
        playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
        if playerSet == "你還沒有登入過啦":
          channel = self.bot.get_channel(876055534757875724)
          await channel.send(f"gm-start {ctx.author.id}")
          await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
          return
      #check
        check = Core.check(self)
        if check!= None:
          if type(check) == str:
            await ctx.respond(check)
          else:
            await ctx.respond(embed = check)
          return

        else:
          embed = '' 
          lvskill = set()
          lv = sorted((list(self.skill_list["lvskill"].keys())))
          for i in lv:
            if self.lv < i:
              break
            lvskill = lvskill | self.skill_list["lvskill"].get(i)
          
          UnllockSkill = ((self.skill_list.get("alllv") & self.skill_list.get("通用")) | (self.skill_list.get("alllv") & self.skill_list.get(self.position,self.skill_list["通用"])) | (lvskill & self.skill_list.get("通用"))) - (set(self.skill.keys())|self.skill_list["cannotlearn"])
          if skill == None:
            for i in UnllockSkill:
              embed += '\n'+ i
            await ctx.reply(f"{self.name}可學習的技能列表\n```"+embed+"\n```")

          elif type(self.bag.get("技能卷軸")) != int:
            await ctx.reply("並沒有=v=")
            return
            
          elif skill not in UnllockSkill:
            await ctx.reply(f"並沒有=v=")
            return
            
          else:
            self.skill[skill] = skilldata[skill]
            rpg.update_one({"id":self.id}, {"$set":{"技能":self.skill}})
            await ctx.reply(f"{self.name}習得了{skill}")
            Core.usedItem(self, "技能卷軸")
        return
  
class itemCog(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)
    @slash_command(name="learn",description="學習技能",options=[
        Option("skill", 
               "你想學習的技能", 
               OptionType.STRING)])
    async def learn(self, ctx, skill = None):
      await learncode(self, ctx, skill)
      return
      
    @slash_command(name="skillup",description="隨機強化技能")
    async def skillupgrad(self,ctx):
        playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
        if playerSet == "你還沒有登入過啦":
          channel = self.bot.get_channel(876055534757875724)
          await channel.send(f"gm-start {ctx.author.id}")
          await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
          return
      #check
        check = Core.check(self)
        if check!= None:
          if type(check) == str:
            await ctx.respond(check)
          else:
            await ctx.respond(embed = check)
          return
        elif type(self.bag.get("技能卡包")) != int:
          await ctx.reply("並沒有OnO")
          return

        if "技能卡包" in self.bag.keys():
          #幾抽
          upgrad_num = random.randint(1,3)

          for i in range(upgrad_num):
            skill = random.choice(list(self.skill.values()))      
            j=0
            while skill['Lv'] >= skill['lvMax'] and j<len(self.skill.values()):
                print(self.skill.values())
                j+=1
                skill = list(self.skill.values()).pop(random.randint(0, len(self.skill.values())-1))
            else:
              if j==len(self.skill.values()):
                await ctx.reply(f"{self.name}技能等級都升滿啦")
                if i != 0 :
                  Core.usedItem(self, "技能卡包")
                return
            self.skill[skill['名稱']]['Lv'] += 1
            rpg.update_one({"_id":ctx.author.id}, {"$set":{"技能":self.skill}})
            await ctx.reply(f"{skill['名稱']}升了一等")
          await ctx.channel.send(f"共升了{upgrad_num}等OUO")
          Core.usedItem(self, "技能卡包")
          rpg.update_one({"_id":ctx.author.id}, {"$set":{"背包":self.bag}})
          return
        else:
          await ctx.reply(f"並沒有OnO")
          return

    @slash_command(name="eat",description="吃東西",options=[
        Option("food", "拿出背包中的點心品嘗吧(可回復體力)", OptionType.STRING)])
    async def eat(self, ctx, food = None):
      playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
      if playerSet == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
        return
    #check
      check = Core.check(self)
      if check!= None:
        if type(check) == str:
          await ctx.respond(check)
        else:
          await ctx.respond(embed = check)
        return
      elif self.bag.get(food) == None:
        await ctx.reply("並沒有O3O")
        return
      elif self.nowSta >= self.maxSta:
        await ctx.reply(f"{self.name}吃得太撐啦")
        return
        
      Core.usedItem(self, food)
      if food in fooddata.keys():
        goodfood = ['猶如美食界的藏寶盒','很好吃！','還不錯','已經臭酸了']
        content = random.choice(goodfood)
        await ctx.respond(f"{food}吃起來{content}")
        if goodfood.index(content) == 0:
          rpg.update_one({"_id":ctx.author.id}, {"$inc":{"nowSta":fooddata[food]["體力"]}})

        rpg.update_one({"id":ctx.author.id},{"$inc":{"nowSta":fooddata[food]["體力"]}})
        # if rpg.find_one({"_id":ctx.author.id})["nowSta"] >= self.maxSta:
        #   rpg.update_one({"id":ctx.author.id},
        #       {"$set":{"nowSta" :self.maxSta}})
        return

      else:
          notfood = ['噎到差點嗆死剩1hp','太髒了導致染病損失100hp','雖然勉強但還是吞下去了','發現雖然很有實驗精神但仍然很蠢']
          content = random.choice(notfood)
          await ctx.respond(content)

          if notfood.index(content)==0:
            rpg.update_one({"_id":ctx.author.id}, {"$set":{"nowHp":1}})

          elif notfood.index(content)==1:
            rpg.update_one({"_id":ctx.author.id}, {"$inc":{"nowHp":-100}})
            Hp = rpg.find_one({"_id":ctx.author.id})["nowHp"]
            if Hp <= 0:
                embed = discord.Embed(title=f'{self.name}因為吃了不該吃的東西而死掉了...',color=0x8a8a8a)
                embed.set_thumbnail(url=self.pfp)
                embed.set_footer(text="輸入 /resurrect 來復活喔")
                
                dead = Core.dead(self, food)
                if type(dead) != str:
                  await ctx.channel.send(embed = embed)
          return
          
    @slash_command(name="equip",description="裝備武器",options=[
        Option("weapon", "選擇你想裝備的武器", OptionType.STRING)])
    async def equip(self, ctx, weapon = None):
      playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
      if playerSet == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
        return
    #check
      check = Core.check(self)
      if check!= None:
        if type(check) == str:
          await ctx.respond(check)
        else:
          await ctx.respond(embed = check)
        return

      elif self.bag.get(weapon) == None:
        await ctx.reply(f"你並沒有{weapon}=ㄙ=")
        return

      elif self.bag[weapon].get("type") != "裝備":
        await ctx.reply(f"{weapon}並不是裝備=ㄙ=")
        return

      equipWeapon = self.bag[weapon]

      if self.weapon["種類"] != '空手' :
        self.bag[self.weapon["名稱"]] = self.weapon

      del self.bag[weapon]

      rpg.update_one({"_id":ctx.author.id}, {"$set":{"武器":equipWeapon}})
      rpg.update_one({"_id":ctx.author.id}, {"$set":{"背包":self.bag}})
      await ctx.reply(f"{self.name}裝備了 {weapon}")
      return
    
    @slash_command(name="summon",description="召喚寵物",options=[
        Option("pet", "選擇你要召喚的寵物", OptionType.STRING)])
    async def summon(self, ctx, pet):
      playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
      if playerSet == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
        return
    #check
      check = Core.check(self)
      if check!= None:
        if type(check) == str:
          await ctx.respond(check)
        else:
          await ctx.respond(embed = check)
        return
      elif self.bag.get(pet) == None:
        await ctx.reply(f"並沒有=A=")
        return
      elif self.bag[pet].get("type") != "寵物":
        await ctx.reply(f"並沒有=A=")
        return
        
      summonPet = self.bag[pet]

      if self.pet != None:
        self.bag[self.pet["名稱"]] = self.pet

      del self.bag[pet]

      rpg.update_one({"_id":ctx.author.id}, {"$set":{"寵物":summonPet}})
      rpg.update_one({"_id":ctx.author.id}, {"$set":{"背包":self.bag}})
      await ctx.reply(f"{pet} 開始跟隨 {self.name}一起冒險")

            
def setup(bot):
    bot.add_cog(itemCog(bot))