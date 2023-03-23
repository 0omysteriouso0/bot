import discord
from discord.ext import commands
import pymongo
import random
import asyncio
from dislash import slash_command, SelectMenu, SelectOption, Option, OptionType
from dislash import InteractionClient, ActionRow, Button, ButtonStyle

from core.core import Core

url='mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]
bagdata = {}



class bagCog(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)
    
    @slash_command(name="bag",description="開啟背包")
    async def checkbag(self,ctx):
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
                
      embed = discord.Embed(title = f'{self.name}的背包\n'+"-"*20, color = 0x8a8a8a)
      embed.set_thumbnail(url = self.pfp)
      print(self.bag)
      if len(self.bag)==0:
          embed.add_field(name=f"你的背包空空如也",value="-"*20,inline=False)
          await ctx.reply(embed = embed)
          await asyncio.sleep(10)
          await ctx.delete()
          return
      elif len(self.bag) <= 7:
        for item, num in self.bag.items():
          if type(num)==dict:
            embed.add_field(name = f"{item}({num['type']})", value= "數量: 1")
          else:
            embed.add_field(name = f"{item}", value= f'數量: {num}')
        embed.add_field(name="-"*20, value = "​​",inline=False)
        await ctx.reply(embed = embed)
        await asyncio.sleep(30)
        await ctx.delete()
        return
      else:
        n=0
        newbag=[]
        pageBag={}
        page = 0
        embed = discord.Embed(title = f'{self.name}的背包\n第 {page+1} 頁\n'+"-"*20, color = 0x8a8a8a)
        embed.set_thumbnail(url = self.pfp)
        for item, num in self.bag.items():
          n+=1
          if n == 7:
              newbag.append(pageBag)
              pageBag={}
              n = 0
          if type(num)==dict:
              pageBag[f"{item}({num['type']})"] = 1
          else:
              pageBag[f"{item}"] = num
        else:
          if pageBag:
            newbag.append(pageBag)
        # with open("bag.json","r",encoding="utf-8") as file:
        #     date=json.loads(file.read())
        bagdata.update({str(ctx.id):{"own" : self.name, 
                                  "pfp" : self.pfp, 
                                  "bag" : newbag, 
                                  "page": page}})
        # with open("bag.json","w",encoding="utf-8") as file:
        #     json.dump(date,file)
        lastpage = Button(
              style=ButtonStyle.gray,
              emoji="⬅️",
              label="上一頁",
              custom_id="green"
              )
        nextpage = Button(
              style=ButtonStyle.gray,
              emoji="➡️",
              label="下一頁",
              custom_id="red"
              )
        page_button = ActionRow(nextpage)
        
      # Note that we assign a list of rows to components
        for item, num in newbag[page].items():
            embed.add_field(name=f"{item}",value=f"數量: {num}",inline=False)
        embed.add_field(name="-"*20,value = "​​",inline=False)
        msg = await ctx.reply(embed = embed, components=[page_button])
      # This is the check for button_click waiter
        def check(inter):
          return inter.author == ctx.author
      # Wait for a button click under the bot's message
        while True:
          try:
            # with open("bag.json","r",encoding="utf-8") as file:
            #     date=json.loads(file.read())
            date = bagdata
            ownbag = date[str(ctx.id)]["bag"]
            page = date[str(ctx.id)]["page"]
            name = date[str(ctx.id)]["own"]
            pfp = date[str(ctx.id)]["pfp"]
            inter = await msg.wait_for_button_click(check=check, timeout=40)
            # Respond to the interaction
            if inter.clicked_button.label=="下一頁": page += 1 
            else: page -= 1 
            print(date)
            date[str(ctx.id)]["page"] = page
            date.update(date)
            # with open("bag.json","w",encoding="utf-8") as file:
            #     json.dump(date,file)
            embed = discord.Embed(title = f'{name}的背包\n第 {page+1} 頁\n'+"-"*20, color = 0x8a8a8a)
            embed.set_thumbnail(url = pfp)
            for item, num in ownbag[page].items():
              embed.add_field(name=f"{item}",value=f"數量: {num}",inline=False)
            else:
              embed.add_field(name="-"*20, value = "​​",inline=False)
            page_button = []
            if page != 0: page_button.append(lastpage)
            if page != len(ownbag)-1: page_button.append(nextpage) 
            await inter.respond(content="", embed = embed, components=[ActionRow(*page_button)], type=7)
          except asyncio.TimeoutError:
            del date[str(ctx.id)]
            await msg.delete()
            return

    @slash_command(name="weapon",description="查看自己裝備的武器")
    async def weapon(self,ctx):
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

      plusLv = self.weapon.get("鍛造數", 0)
      plusLvText = f"+{plusLv}" if plusLv else ""

      weaponLvList = ["","Ⅰ","Ⅱ","Ⅲ","Ⅳ","Ⅴ","Ⅵ"]
      embed=discord.Embed(color = self.rareColor[self.weapon['品質']])
      embed.set_author(name = f'{weaponLvList[self.weapon["Lv"]]}. {self.weapon["名稱"] + plusLvText}({self.weapon["種類"]})\n熟練度 : {self.weapon["熟練度"]}')
      embed.set_thumbnail(url = self.weapon["頭像"])
      embed.add_field(name = "\n敘述:", value = self.weapon['敘述'], inline=False)
      embed.add_field(name = "耐久度", value = self.weapon['耐久度'], inline=False)
      embed.add_field(name = "攻擊力", value = self.weapon['攻擊力'], inline=False)
      embed.add_field(name = "防禦力", value = self.weapon['防禦力'], inline=False)
      embed.add_field(name = "敏捷度", value = self.weapon['敏捷度'], inline=False)
      embed.add_field(name = "運氣值", value = self.weapon['運氣值'], inline=False)
      await ctx.reply(embed = embed)
      await asyncio.sleep(30)
      await ctx.delete()
      return

    @slash_command(name="pet",description="查看自己的寵物")
    async def pet(self,ctx):
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
      elif self.pet != None:
        embed=discord.Embed(color = self.rareColor[self.pet['品質']])
        embed.set_author(name = f'{self.pet["名稱"]}({self.pet["種類"]})')
        embed.set_thumbnail(url = self.pet["頭像"])
        embed.add_field(name = "\n\n敘述:", value = self.pet['敘述'], inline=False)
        await ctx.reply(embed = embed)
        await asyncio.sleep(30)
        await ctx.delete()
        return
      else:
        await ctx.reply("你還沒有寵物啦")
        return
        
    @slash_command(name="artname",description="裝備稱號",options=[
        Option("achievement", 
               "填入你的成就變成稱號", 
               OptionType.STRING)])
    async def pet(self,ctx, achievement = None):
      playerSet = Core.playerSet(self, rpg.find_one({"id": ctx.author.id}))
      if playerSet == "你還沒有登入過啦":
          channel = self.bot.get_channel(876055534757875724)
          await channel.send(f"gm-start {ctx.author.id}")
          await ctx.reply(playerSet + "\n但我幫你添了一筆資料")
          return
      #check
      check = Core.check(self)
      if check != None:
          if type(check) == str:
              await ctx.reply(check)
          else:
              await ctx.reply(embed=check)
          return
      if achievement == None:
        await ctx.reply("你沒有告訴我你要的稱號...")
        if "《隱藏成就》佐佐木小次郎?" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得**隱藏**成就✨\n「佐佐木小次郎?」")
            return
          
      if achievement in [i.split("》")[1] for i in self.achievement.keys()]:
        rpg.update_one({"id":ctx.author.id}, {"$set":{"稱號":achievement}})
      else:
        await ctx.reply("你沒有這個稱號;O;")
        return
      
      await ctx.reply(f"《{achievement}》{self.name}，你的稱號更新啦！")
        
def setup(bot):
    bot.add_cog(bagCog(bot))
