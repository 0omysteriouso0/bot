import discord
from discord.ext import commands
import pymongo
import random
import asyncio
import json
from dislash import slash_command, OptionChoice, Option, OptionType
import datetime
from core.core import Core

url='mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]
shopdb = cluster["RPG"]["shop"]

with open("item.json","r",encoding="utf-8") as data:
    itemdata=json.load(data)
with open("weapon.json","r",encoding="utf-8") as data:
    weapondata=json.load(data)
with open("shop.json","r",encoding="utf-8") as data:
    shopdata=json.load(data)

choice = []
for key in shopdata.keys():
  choice.append(OptionChoice(
                name = key,
                value = key)
              )

async def shopcode(self, ctx, shop, commodity = None, num = 1):
    playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
    if playerSet == "你還沒有登入過啦":
      channel = self.bot.get_channel(876055534757875724)
      await channel.send(f"gm-start {ctx.author.id}")
      await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
      return
  #check
    check = Core.check(self)
    if check!= None:
      if "打工" in self.state:
        pass
      elif type(check) == str:
        await ctx.reply(check)
        return
      else:
        await ctx.reply(embed = check)
        return
  #start 
    if shopdb.count_documents({"_id":ctx.guild.id})==0:
        shopdb.insert_one({"_id":ctx.guild.id,
                           "date":datetime.datetime.now()})
        for shopkey in shopdata.keys():
          if shopkey != "玩家交易所":
            shopdb.update_one({"_id":ctx.guild.id},
                              {"$set": {shopkey : shopdata[shopkey]}})
    if shopdb.find_one({"_id":ctx.guild.id})["date"].day != \
      datetime.datetime.now().day:
        
      for shopkey in shopdata.keys():
        if shopkey == "玩家交易所":
          continue
        shopdb.update_one({"_id":ctx.guild.id},
          {"$set": {shopkey : shopdata[shopkey],
                   "date" : datetime.datetime.now()}})
    if not shop:
      embed=discord.Embed(title = "商店清單\n"+"-"*20,color= 0xa94b23)
      for shops in shopdata.keys():
          embed.add_field(
            name=shops,
            value=f"\\",inline=False)
      await ctx.reply(embed=embed)
      return 
          
    elif not commodity:
      guildshop = shopdb.find_one({"_id":ctx.guild.id})[shop]
      embed=discord.Embed(title = shop+"\n"+"-"*20,color= 0xa94b23)
      # embed.set_thumbnail(url=pfp)
      for goods, price in guildshop.items():
        if type(price) == int:
          embed.add_field(
            name=goods,
            value=f"價格: {price} 元",inline=False)
          
        elif type(price) == list:
          if len(price) > 3:
            goods = goods+". "+price[-1]
          embed.add_field(
            name=goods,
            value=f"價格: {price[0]} 元"+" "*4+
            f"剩餘數量 {price[1]} 個",inline=False)
          
        elif type(price) == dict:
          itemPrice = ""
          for item, num in price.items():
            itemPrice += f"{item}: {num} 個\n"
          embed.add_field(
            name=goods,
            value=itemPrice
            ,inline=False)
  
      embed.timestamp = datetime.datetime.utcnow()
  
      await ctx.reply(embed=embed)
      return
      
    elif commodity:
      price = shopdb.find_one({"_id":ctx.guild.id})[shop].get(commodity)
      if price == None:
        await ctx.reply("我們店裡好像沒這個貨，請再確認看看吧")
        return 
        
      else:
        if type(price) == int:
          price *= num
          if self.money < price:
            await ctx.reply("錢不夠阿=v=")
            return
          rpg.update_one({"id":ctx.author.id},{"$inc":{"money": -price}})
          await ctx.reply("交易成功，你獲得了"+commodity)
          
        elif type(price) == list:
          price[0] *= num
          price[1] -= num
          if self.money < price[0]:
            await ctx.reply("錢不夠阿=v=")
            return
          elif price[1] < 0:
            await ctx.reply("沒貨啦OwO")
            return
          # 道具
          if len(price) == 4:
            rpg.update_one({"id": price[2]},{"$inc":{"money":price[0]}})
            rpg.update_one({"id":ctx.author.id},{"$inc":{"money": -price[0]}})
            nowshop = shopdb.find_one({"_id":ctx.guild.id})[shop]
            nowshop[commodity][1] -= num
            if nowshop[commodity][1] == 0:
              del nowshop[commodity]
            commodity = price[-1]
            shopdb.update_one({"_id":ctx.guild.id},{"$set":{shop: nowshop}})
            await ctx.reply("交易成功，你獲得了"+commodity)
            playauthor = rpg.find_one({"id": ctx.author.id})
            Core.getSomething(self, playauthor, commodity, num)
            return
          # 武器
          elif len(price) == 5:
            rpg.update_one({"id": price[2]},{"$inc":{"money":price[0]}})
            rpg.update_one({"id":ctx.author.id},{"$inc":{"money": -price[0]}})
            nowshop = shopdb.find_one({"_id":ctx.guild.id})[shop]
            nowshop[commodity][1] -= num
            if nowshop[commodity][1] == 0:
              del nowshop[commodity]
            commodity = price[-1]
            shopdb.update_one({"_id":ctx.guild.id},{"$set":{shop: nowshop}})
            await ctx.reply("交易成功，你獲得了"+commodity)
            weapon = { commodity : price[3] }
            playauthor = rpg.find_one({"id": ctx.author.id})
            Core.getSomething(self, playauthor, weapon, num)
            # rpg.update_one({"id":ctx.author.id},{"$set":{"背包."+commodity: price[3]}})
            return
          

          rpg.update_one({"id":ctx.author.id},{"$inc":{"money": -price[0] * num}})
          nowshop = shopdb.find_one({"_id":ctx.guild.id})[shop]
          nowshop[commodity][1] -= num
          if nowshop[commodity][1] == 0:
            del nowshop[commodity]
          shopdb.update_one({"_id":ctx.guild.id},{"$set":{shop: nowshop}})
          await ctx.reply("交易成功，你獲得了"+commodity)
          
        elif type(price) == dict:
          newbag = {key: self.bag.get(key, 0) - price.get(key, 0)*num
          for key in set(price)}
          print(newbag)
          if min(newbag.values()) < 0:
            await ctx.reply("素材不夠阿=v=")
            return
          for i in price.keys():
            if newbag[i] == 0 :
              del newbag[i]
              del self.bag[i]
          await ctx.reply("打造成功，你獲得了"+commodity)
          
          self.bag.update(newbag)
          
          rpg.update_one({"id":ctx.author.id},{"$set":{"背包": self.bag}})
        playauthor = rpg.find_one({"id": ctx.author.id})
        if commodity in weapondata:
          commodity = Core.weaponSet(self, weapondata[commodity])
        Core.getSomething(self, playauthor, commodity, num)
    return

async def sellcode(self, ctx, item, cost, num = 2):
    playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
    if playerSet == "你還沒有登入過啦":
      channel = self.bot.get_channel(876055534757875724)
      await channel.send(f"gm-start {ctx.author.id}")
      await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
      return
  #check
    check = Core.check(self)
    if check!= None:
      if "打工" in self.state:
        pass
      elif type(check) == str:
        await ctx.reply(check)
        return
      else:
        await ctx.reply(embed = check)
        return
        
    newShop = shopdb.find_one({"_id":ctx.guild.id})
  
    if item not in self.bag:
      await ctx.reply("你沒有這個道具啦=厶=")
      return
    elif num <= 0:
      await ctx.reply("格式錯誤，數量必須為正整數")
      return
    elif cost <= 0:
      await ctx.reply("大放送? 價格必須為正整數啦")
      return
      
    elif type(self.bag[item]) == int:
      if self.bag[item] < num:
        await ctx.reply("道具不足0n0")
        return
      else:
        n = 1
        while str(n) in newShop["玩家交易所"]:
          n += 1
        newShop["玩家交易所"].update({str(n): [cost, num, self.id, item]})
        
    elif type(self.bag[item]) == dict:
      if num != 1:
        await ctx.reply("道具不足0n0")
        return
      else:
        n = 1
        while str(n) in newShop["玩家交易所"]:
          n += 1
        newShop["玩家交易所"].update({str(n): [cost, num, self.id, self.bag[item], item]})
        
    await ctx.reply(f"你成功把 {item} 賣掉啦，為 {n} 號商品")
    for i in range(num):
      Core.usedItem(self, item)
    shopdb.update_one({"_id":ctx.guild.id},{"$set":newShop})
    
    
  
class Shop(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)
    @commands.command(name="shop", description="商店")
    async def shopcmd(self, ctx, shop, goods=None):
      await shopcode(self, ctx, shop, goods)
      return

    @slash_command(name="shop",description="商店", 
        options=[
            Option("shop", "商店", choices = choice),
            Option("goods", "商品", OptionType.STRING)
            ]
            )
    async def shop(self, ctx, shop = None, goods=None):
      await shopcode(self, ctx, shop, goods)
      return

    @commands.command(name="sell", description="販賣")
    async def sellcmd(self, ctx, item, cost=None, num = 1):
      await sellcode(self, ctx, item, cost, num = num)
      return

    @slash_command(name="sell",description="販賣", 
        options=[
            Option("item", "商品", OptionType.STRING),
            Option("cost", "價格", OptionType.INTEGER),
            Option("num", "數量", OptionType.INTEGER)
            ]
            )
    async def sell(self, ctx, item = None, cost=None, num = 1):
      await sellcode(self, ctx, item, cost, num = num)
      return


      
def setup(bot):
    bot.add_cog(Shop(bot))