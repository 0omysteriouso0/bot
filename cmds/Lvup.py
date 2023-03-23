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

with open("item.json","r",encoding="utf-8") as data:
    itemdata=json.load(data)
with open("weapon.json","r",encoding="utf-8") as data:
    weapondata=json.load(data)
with open("skill.json","r",encoding="utf-8") as data:
    skilldata=json.load(data)


async def transfercode(self, ctx, position):
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

    allPosition={
        "冒險者" : {
            "lvLimit" : 10,
            "劍士": [10, 7, 7, 0, 0],
            "遊俠": [0, 3, 0, 15, 1],
            "法師": [0, 15, 0, 1, 2],
        },
        
        "劍士":{
            "lvLimit" : 30,
            "聖騎士":  [20, 0, 15, 0, 5],
            "狂戰士":  [20, 25, -10, 0, 0],
            "魔劍士":  [20, 10, 10, 0, 0],
        },   

        "遊俠":{
            "lvLimit" : 30,
            "刺客":    [0, 15, 0, 15, 0],
            "盜賊":    [0, 0, 0, 15, 15],
            "幻影遊俠":[0, 0, 0, 30, 0],
        },
        
        "法師":{
            "lvLimit" : 30,
            "牧師":    [15, 0, 7, 0, 15],
            "祭司":  [10, 15, 0, 0, 10],
            "魔導師":  [10, 15, 0, 0, 10],
        }
        }
        #Hp, Atk, Def, Agi, Luc
    
    if position not in allPosition[self.position].keys() and True:
      await ctx.reply("並沒有=o=")
      return

    elif self.lv < allPosition[self.position]["lvLimit"]:
      await ctx.reply(f"等級必須達到{allPosition[self.position]['lvLimit']}，繼續加油吧")
      return

    value = allPosition[self.position][position]
    post={
      "maxHp": value[0], "nowHp": value[0],
      "Atk": value[1], "Def": value[2],
      "Agi": value[3], "Luc": value[4]
    }
    rpg.update_one({"id":ctx.author.id}, {"$inc":post})
    rpg.update_one({"id":ctx.author.id}, {"$set":{"職位":position}})
    await ctx.reply(f'{self.name}成功進階為{position},力量大幅提升了')
    return

async def weaponupcode(self, ctx, item):
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

    elif not item:
      await ctx.reply("請放上你的武器與素材")
      return
      
    elif self.money < 200:
      await ctx.reply("鍛造你的武器至少需要 200 元喔")
      return

    elif item not in self.bag:
      await ctx.reply("你的背包裡並沒有"+item+"啦=H=")
      return

    elif self.weapon["種類"] == "空手":
      await ctx.reply("敖,好痛,手不能拿來鍛造啦")
      return
      
    else:
      if item not in itemdata and self.bag[item]["種類"] not in weapondata:
        await ctx.reply(f"目前版本{item}還無法拿來鍛造,請期待版本更新")
        return
        
      if self.weapon.get("鍛造數", 0) == None:
        await ctx.reply(f"此武器無法鍛造喔")
        return
      elif self.weapon.get("鍛造數", 0) >= 15:   
        await ctx.reply(f"此武器已達到強化上限啦")
        return
        
      rpg.update_one({"id":ctx.author.id},{"$inc":{"money":-200}}) 
      if random.randint(1,25) <= self.weapon.get("鍛造數", 0):
        await ctx.reply(f"鍛造失敗")
        return

      self.weapon["鍛造數"] = self.weapon.get("鍛造數", 0)+1
      if item in itemdata:
        itemval = itemdata[item]
      else:
        itemval = self.bag[item]
        
      powervalues = ["攻擊力","防禦力",
                    "敏捷度","運氣值",
                    "耐久度"] 
      powervalues_lens = len(powervalues)
      n = random.uniform(0.5, 1.6)
      n = 2 if n > 1.5 else n
      
      isWeapon = 0.2 if type(self.bag[item]) == dict else 1
      n *= isWeapon
      if isWeapon == 0.2:
        if self.bag[item]["種類"] == self.weapon["種類"] and self.weapon["Lv"] < 5:
          n *= self.weapon["Lv"]
          self.weapon["Lv"] += 1
      
      report = {}
      for i in range(powervalues_lens):
        tail = powervalues_lens-1-i
        if i > tail:
          break
        i, tail = powervalues[i], powervalues[tail]
        
        if type(self.weapon[i]) == str:
          report[i] = "已達上限"
          continue
          
        report[i] = int(itemval[i] * n)
        self.weapon[i] += int(itemval[i] * n)
        if i != tail:
          
          if type(self.weapon[tail]) == str:
            report[tail] = "已達上限"
            continue
            
          report[tail] = int(itemval[tail] * n)
          self.weapon[tail] += int(itemval[tail] * n)

      if n >= 2:
        await ctx.reply("超級大成功!")
      elif n >= 1.3:
        await ctx.reply("大成功!")
      else:
        await ctx.reply("成功!")
      embed = discord.Embed(title = "數值提升",
                            color = 0xd60000)
      embed.set_thumbnail(url=str(self.weapon["頭像"]))
      embed.add_field(name = "耐久度", 
                      value = "+"+str(report['耐久度']), 
                      inline=False)
      embed.add_field(name = "攻擊力", 
                      value = "+"+str(report['攻擊力']), 
                      inline=False)
      embed.add_field(name = "防禦力", 
                      value = "+"+str(report['防禦力']), 
                      inline=False)
      embed.add_field(name = "敏捷度", 
                      value = "+"+str(report['敏捷度']), 
                      inline=False)
      embed.add_field(name = "運氣值", 
                      value = "+"+str(report['運氣值']), 
                      inline=False)
      msg = await ctx.reply(embed = embed)
      Core.usedItem(self, item)
      rpg.update_one({"id":ctx.author.id},{"$set":{"武器":self.weapon}})
      await asyncio.sleep(30)
      await msg.delete()
      return

async def skillcapcode(self, ctx, skill):
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

    elif not skill:
      await ctx.reply("請選擇你要突破上限的技能")
      return
      
    elif self.money < 1000:
      await ctx.reply("突破你的技能至少需要 1000 元喔")
      return

    elif skill not in self.skill.keys():
      await ctx.reply("你並不會"+skill+"啦=H=")
      return
      
    elif "靈魂寶石" not in self.bag:
      await ctx.reply("需要道具 *靈魂寶石* ")
    else:
      if self.skill[skill]["lvMax"] == 0:
        await ctx.reply(f"{skill}技能沒有等級之分啦")
        return
        
      self.money -= 1000
      self.skill[skill]["lvMax"] += skilldata[skill]["lvMax"]
      await ctx.reply(f"成功!{self.name}的{skill}上限提升了\n{skilldata[skill]['lvMax']}等 -> {self.skill[skill]['lvMax']}等")
      rpg.update_one({"id":ctx.author.id}, {"$set":{"技能":self.skill}})
      rpg.update_one({"id":ctx.author.id}, {"$set":{"money":self.money}})
      
class limitCog(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)
    
    @slash_command(name="transfer", description="職位升階", options=[
        Option("position", "選擇你想要的職位", OptionType.STRING)])
    async def transfer(self, ctx, position = None):
        await transfercode(self, ctx, position)
        return
    
    @commands.command(name="transfer", description="職位升階")
    async def transfercmd(self, ctx, position = None):
        await transfercode(self, ctx, position)
        return

    @slash_command(name="weaponup", description="武器鍛造", options=[
        Option("item", "選擇拿來強化的素材", OptionType.STRING)])
    async def weaponupcode(self, ctx, item = None):
        await weaponupcode(self, ctx, item)
        return
    
    @commands.command(name="weaponup", description="武器鍛造")
    async def weaponup(self, ctx, item = None):
        await weaponupcode(self, ctx, item)
        return

    @slash_command(name="skillcap", description="突破技能上限", options=[
        Option("skill", "選擇你想突破上限的技能", OptionType.STRING)])
    async def skillcap(self, ctx, skill = None):
        await skillcapcode(self, ctx, skill)
        return
    
    @commands.command(name="skillcap", description="突破技能上限")
    async def skillcapcmd(self, ctx, skill = None):
        await skillcapcode(self, ctx, skill)
        return

def setup(bot):
    bot.add_cog(limitCog(bot))