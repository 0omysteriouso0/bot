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

class mapCog(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)

    @slash_command(name="map",description="地圖")
    async def map(self,ctx):
      playerSet = Core.playerSet(self,rpg.find_one({"id": ctx.author.id}))
      if playerSet == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet+"\n但我幫你添了一筆資料")
        return
      msg = await ctx.reply(
        "選擇一個地區",
        components=[
          SelectMenu(
            custom_id="test",
            placeholder="Choose area",
            max_values=1,
            options=[
              SelectOption("休憩小鎮", 0),
              SelectOption("啟程草原", 1),
              SelectOption("礦石洞窟", 2),
              SelectOption("迷霧森林", 3),
              SelectOption("荒涼之地", 4),
              SelectOption("赤炎山谷", 5),
              SelectOption("寒霜高原", 6),
            ]
          )
        ]
      )
      def check(inter):
        # inter is instance of MessageInteraction
        # read more about it in "Objects and methods" section
        return inter.author == ctx.author
        # Wait for a menu click under the message you've just sent
      allembed=[
        discord.Embed(title=f"",color=self.areaColor["休憩小鎮"]).add_field(name="休憩小鎮", value="一個適合休息的和平小鎮(沒什麼實質用途，胡亂狩獵或許會打擾他們和樂的氣氛...\n(推薦Lv:無，不要破壞和平氣氛)", inline=False),
        discord.Embed(title=f"",color=self.areaColor["啟程草原"]).add_field(name="啟程草原", value="一切的啟源，屬於你的冒險故事，在此揭開序幕\n(推薦Lv:0+)", inline=False),
        discord.Embed(title=f"",color=self.areaColor["礦石洞窟"]).add_field(name="礦石洞窟", value="許多人都不敢接近漆黑的礦洞，謠傳這裡有兇殘的怪物出沒，記得先提升一點等級再來喔\n(推薦Lv:10+)", inline=False),
        discord.Embed(title=f"",color=self.areaColor["迷霧森林"]).add_field(name="迷霧森林", value="充滿迷霧、伸手不見五指的地方，小心別迷失在裏頭，傳聞許多冒險者進去之後就杳無音訊......\n(推薦Lv:20+)", inline=False),
        discord.Embed(title=f"",color=self.areaColor["荒涼之地"]).add_field(name="荒涼之地", value="龜裂地表放遠望去只剩幾棵枯木，原先清澈的池塘如今成了充滿毒氣的泥濘，兇殘怪物佔據後，寥無生氣使這更加荒涼\n(推薦Lv:35+)", inline=False),
        discord.Embed(title=f"",color=self.areaColor["赤炎山谷"]).add_field(name="赤炎山谷", value="天氣終年異常炎熱，尤其是谷地正中央的火山。岩漿如同水漥一般常見，亂竄的火舌使生物燃燒，也有無法適應的燃燒殆盡化成了灰......\n(推薦Lv:50+)", inline=False),
        discord.Embed(title=f"",color=self.areaColor["寒霜高原"]).add_field(name="寒霜高原", value="天氣終年異常寒冷，高原上空的急疾風與爬升的暖濕氣流交會，使暴風雪頻繁襲來。如通冷凍庫的氣溫，令死亡的生物不易腐化\n(推薦Lv:50+)", inline=False)
      ]
      while True:
        try:
          inter = await msg.wait_for_dropdown(check = check, timeout=40)
          # Tell which options you received
          labels = [int(option.value) for option in inter.select_menu.selected_options]
          await msg.edit(embed=allembed[labels[0]],
                            components=[
                            SelectMenu(
                            custom_id="test",
                            placeholder="Choose area",
                            max_values=1,
                            options=[
                            SelectOption("休憩小鎮", 0),
                            SelectOption("啟程草原", 1),
                            SelectOption("礦石洞窟", 2),
                            SelectOption("迷霧森林", 3),
                            SelectOption("荒涼之地", 4),
                            SelectOption("赤炎山谷", 5),
                            SelectOption("寒霜高原", 6)
                            ]
                            )
                            ]
                            )
        except asyncio.TimeoutError:
          await ctx.delete()
          return
      
    @slash_command(name="teleport", description="傳送", options=[
        Option("area", "選擇想抵達的地點", OptionType.STRING)])
    async def teleport(self, ctx, area = None):
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
        if area == None:
          await ctx.reply("此指令無效，請輸入地區",ephemeral = True)
          return
        if area not in self.allArea:
          await ctx.reply(f"地圖上沒有{area},抑或尚未開放\n可以輸入 /map 來查看欲抵達位置喔")
          return
        # elif 寵物["名稱"]=="豆餡" and tmp[1]=="甘兔庵":
        #     await msg.channel.send(f"已成功將你傳送到{tmp[1]}")
        else:
          rpg.update_one({"_id":ctx.author.id}, {"$set":{"地區":area}})
          await ctx.reply(f"已成功將你傳送到{area}")
          return

def setup(bot):
    bot.add_cog(mapCog(bot))