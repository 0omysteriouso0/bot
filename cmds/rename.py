import discord
from discord.ext import commands
import pymongo
import random
import asyncio
import json
from dislash import slash_command, ActionRow, Button, ButtonStyle,SelectMenu, SelectOption, Option, OptionType,OptionChoice
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from core.core import Core

url='mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]



with open("monster.json","r",encoding="utf-8") as monjson:
    mondata=json.load(monjson)

#code
#rename
async def renamecode(self, ctx, name):
  playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
  if playerSet == "你還沒有登入過啦":
    channel = self.bot.get_channel(876055534757875724)
    await channel.send(f"gm-start {ctx.author.id}")
    await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
    return
  rpg.update_one({"_id":ctx.author.id}, {"$set":{"name":name}})
  await ctx.reply(f"你現在就叫做 {name} 了!")
  return
#petrename
async def petnamecode(self, ctx, name):
  playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
  if playerSet == "你還沒有登入過啦":
    channel = self.bot.get_channel(876055534757875724)
    await channel.send(f"gm-start {ctx.author.id}")
    await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
    return
  rpg.update_one({"_id":ctx.author.id}, {"$set":{"寵物.名稱":name}})
  await ctx.respond(f"成功替寵物取名為{name}~~")
  return
#weaponrename
async def weaponnamecode(self, ctx, name):
  playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
  if playerSet == "你還沒有登入過啦":
    channel = self.bot.get_channel(876055534757875724)
    await channel.send(f"gm-start {ctx.author.id}")
    await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
    return
  rpg.update_one({"_id":ctx.author.id}, {"$set":{"武器.名稱":name}})
  await ctx.respond(f"已把你的武器名改成{name}")
  return

def circle_corner(img, radii):  #把原图片变成圆角，这个函数是从网上找的，原址 https://www.pyget.cn/p/185266
    """
    圆角处理
    :param img: 源图象。
    :param radii: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """
    # 画圆（用于分离4个角）
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形
    # 原图
    img = img.convert("RGBA")
    w, h = img.size
    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
    # alpha.show()
    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    return img

class pfpCog(Core):
    def __init__(self, bot):
        super().__init__(bot = bot)
        self.bot = bot

    @commands.command(name="pfp",description="重設頭像")
    async def pfp(self, ctx, shapetype = None):
      msg = ctx.message
      print(msg.attachments)
      url = msg.attachments[0].url
      if msg.attachments[0].filename.endswith(".gif"):
        url = msg.attachments[0].url
      else:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        x, y = img.size
        smaller = min(x, y)
        # if min(img.size) < 628:
        #     multiple = int(628/smaller)+1
        #     img = img.resize((x*multiple, y*multiple))
        #     x, y = img.size
        #     smaller = min(x, y)
        smaller_half = smaller / 2
        newsize = smaller / 3
        half = newsize / 2

        direction = {"top_left": (0, 0, newsize, newsize),
                      "top": (x/2 -half, 0, x/2 +half, newsize),
                      "top_right": (x-newsize, 0, x, newsize),

                      "buttom_left": (0, y-newsize, newsize, y),
                      "buttom": (x/2 -half, y-newsize, x/2 +half, y),
                      "buttom_right": (x-newsize, y-newsize, x, y),

                      "left": (0, y/2 -half, newsize, y/2 +half),
                      "center": (x/2 -half, y/2 -half, x/2 +half, y/2 +half),
                      "right": (x-newsize, y/2 -half, x, y/2 +half)}
        shapetype = shapetype
        shapetype_None = (x/2 - smaller_half, y/2 - smaller_half, 
        x/2 + smaller_half, 
        y/2 + smaller_half)
        if shapetype == None: shape = shapetype_None
        else:
          shape = direction.get(shapetype, (0,0,x,y))
        
        print(shape)
        print(img.size)
        img = img.crop(shape) 
        img = circle_corner(img, radii=20)
        img = img.convert('RGB')
        img.save('./pfpImage/self_pfp.jpg')
        pic = discord.File('./pfpImage/self_pfp.jpg')
        author = self.bot.get_user(868464149145997313)
        print(author)
        message = await author.send(file = pic)
        url = message.attachments[0].url
        
      rpg.update_one({"id":ctx.author.id},{"$set": {"頭像": url} })


    @commands.command(name="rename", description="改名")
    async def renamecmd(self, ctx, name = None):
      if name == None:
        await ctx.reply("請輸入名字")
        return
      await renamecode(self, ctx, name)
      return

    @slash_command(name="rename", description="改名", options=[
        Option("name", "你的新名字", OptionType.STRING
        )])
    async def rename(self, ctx, name = None):
      if name == None:
        await ctx.reply("請輸入名字")
        return
      await renamecode(self, ctx, name)
      return
    
  
    @commands.command(name="petname", description="改寵物名")
    async def petnamecmd(self, ctx, name = None):
      if name == None:
        await ctx.reply("請輸入名字")
        return
      await petnamecode(self, ctx, name)
      return

    @slash_command(name="petname", description="改寵物名", options=[
        Option("name", "寵物的新名字", OptionType.STRING)])
    async def petrename(self, ctx, name = None):
      if name == None:
        await ctx.reply("請輸入名字")
        return
      await petnamecode(self, ctx, name)
      return


    @commands.command(name="weaponname", description="改武器名")
    async def weaponnamecmd(self, ctx, name = None):
      if name == None:
        await ctx.reply("請輸入名字")
        return
      await weaponnamecode(self, ctx, name)
      return
      
    @slash_command(name="weaponname", description="改武器名", 
    options=[Option("name", "武器的新名字", OptionType.STRING)])
    async def weaponname(self, ctx, name = None):
      if name == None:
        await ctx.reply("請輸入名字")
        return
      await weaponnamecode(self, ctx, name)
      return
    

def setup(bot):
    bot.add_cog(pfpCog(bot))