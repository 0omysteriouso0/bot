import discord
from discord.ext import commands
import pymongo
import random
import asyncio
import json
import datetime
from dislash import slash_command, SelectMenu, SelectOption, Option, OptionChoice, OptionType

from core.core import Core

url = 'mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]

with open("monster.json", "r", encoding="utf-8") as monjson:
    mondata = json.load(monjson)


#code
#start
async def startcode(self, inter):
    user = inter.author
    if rpg.count_documents({"id": user.id}) != 0:
        await inter.reply(f'{user.name}你已登入過')
        return
    print(inter)
    #Hp, Atk, Def, Agi, Luc, Sta
    basicValues = [
        random.randint(100, 125),
        random.randint(10, 15),
        random.randint(7, 10),
        random.randint(5, 7),
        random.randint(2, 5),
        random.randint(20, 40)
    ]
    post = {
        "_id": user.id,
        "id": user.id,
        "tag": user.mention.replace("!", ""),
        "name": user.name,
        "職位": "冒險者",
        "頭像": str(user.avatar_url),
        "等級": 1,
        "exp": 0,
        "maxHp": basicValues[0],
        "nowHp": basicValues[0],
        "Atk": basicValues[1],
        "Def": basicValues[2],
        "Agi": basicValues[3],
        "Luc": basicValues[4],
        "maxSta": basicValues[5],
        "nowSta": basicValues[5],
        "useSta": 0,
        "money": 200,
        "背包": {},
        "武器": self.basicWeapon,
        "裝備": None,
        '寵物': None,
        "技能": self.basicSkill,
        "狀態": [],
        "回合": 0,
        "地區": self.allArea[1],
        "副職": None,
        "成就": {},
        "稱號": None,
        "職位列表": [],
        "teamid": user.id,
        "teamName": None,
        "teamMember": [user.mention.replace("!", "")],
        "boss": False,
        "已狩獵boss": {},
        "已狩獵": {},
        "對戰對象": int(),
        "對戰": False,
        "死亡數": 0,
        "狩獵休息": [datetime.datetime.now(), 0],
        "探險休息": [datetime.datetime.now(), 0],
        "打工時間": 0,
        "技能點": 0,
        "每日登入": 0,
        "連續登入": 0,
        "每日爆裂": 0,
        'maxHp點': 0,
        "Atk點": 0,
        "Def點": 0,
        "Agi點": 0,
        "Luc點": 0,
        "maxSta點": 0
    }
    rpg.insert_one(post)
    await inter.reply('登入成功')
    return


#select
async def selectcode(self, ctx):
    msg = await ctx.reply("選擇一個想查詢的職位",
                          components=[
                              SelectMenu(custom_id="test",
                                         placeholder="Choose position",
                                         max_values=1,
                                         options=[
                                             SelectOption("劍士", 0),
                                             SelectOption("聖騎士", 1),
                                             SelectOption("遊俠", 2),
                                             SelectOption("法師", 3),
                                             SelectOption("牧師", 4)
                                         ])
                          ])

    def check(inter):
        # inter is instance of MessageInteraction
        # read more about it in "Objects and methods" section
        return inter.author == ctx.author
        # Wait for a menu click under the message you've just sent

    allembed = [
        discord.Embed(title=f"", color=0x16d070).add_field(
            name="劍士", value="可以一手揮舞著劍,一手施展一些小魔法,是個各方面都很平均的角色", inline=False),
        discord.Embed(title=f"", color=0x16d070).add_field(
            name="聖騎士", value="最擅長防禦的角色,擁有一滴點的神性,在敵人面前從不屈服", inline=False),
        discord.Embed(title=f"", color=0x16d070).add_field(
            name="遊俠",
            value="穿梭於叢林之間,藏身於暗夜之中,擅長使弓,並擁有敏銳的直覺與高速的敏捷",
            inline=False),
        discord.Embed(title=f"", color=0x16d070).add_field(
            name="法師", value="已大量的傷害給予遠處的敵人致命一擊,不過得小心近身戰呦(並沒有)", inline=False),
        discord.Embed(title=f"", color=0x16d070).add_field(
            name="牧師",
            value="神性極高的角色,給人們帶來希望與光明,幸運之神會眷顧著這些可愛的教徒",
            inline=False)
    ]
    while True:
        try:
            inter = await msg.wait_for_dropdown(check=check, timeout=40)
            # Tell which options you received
            labels = [
                int(option.value)
                for option in inter.select_menu.selected_options
            ]
            await msg.edit(embed=allembed[labels[0]],
                           components=[
                               SelectMenu(custom_id="test",
                                          placeholder="Choose position",
                                          max_values=1,
                                          options=[
                                              SelectOption("劍士", 0),
                                              SelectOption("聖騎士", 1),
                                              SelectOption("遊俠", 2),
                                              SelectOption("法師", 3),
                                              SelectOption("牧師", 4)
                                          ])
                           ])
        except asyncio.TimeoutError:
            await msg.delete()
            return


#info
async def infocode(self, ctx, public=True, user=None):
    users = ctx.author.id if user == None else user.id
    if user != None:
        if rpg.count_documents({"_id": user.id}) == 0:
            await ctx.reply(f'{user.name}還沒登入過喔')
            return
    playerSet = Core.playerSet(self, rpg.find_one({"id": users}))
    if playerSet == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet + "\n但我幫你添了一筆資料")
        return
    '''
  #check
    check = Core.check(self)
    if check!= None:
      if type(check) == str:
        await ctx.reply(check)
      else:
        await ctx.reply(embed = check)
    '''
    title = f"職位: {self.position}\n等級: Lv.{self.lv}\nexp: {self.exp}/{self.lv*20}\n地區: {self.area}"
    name = f"{self.name}的數值"
    if self.pet != None:
        title = f"寵物: {self.pet['名稱']}\n等級: Lv.{self.lv}\nexp: {self.exp}/{self.lv*20}\n地區: {self.area}\n職位: {self.position}"

    if self.title != None:
        title = f"《{self.title}》\n{title}"

    embed = discord.Embed(title=title, color=self.areaColor[self.area])
    embed.set_author(name=name)
    embed.set_thumbnail(url=self.pfp)
    if self.pet != None:
        embed.set_author(name=name, icon_url=self.pfp)
        embed.set_thumbnail(url=self.pet["頭像"])
    embed.add_field(name="武器",
                    value=f"{self.weapon['名稱']}({self.weapon['種類']})",
                    inline=False)
    embed.add_field(name="生命值",
                    value=f"{self.nowHp} / {self.maxHp}",
                    inline=False)
    embed.add_field(name="體力",
                    value=f"{self.nowSta} / {self.maxSta}",
                    inline=False)
    embed.add_field(name="攻擊力",
                    value=f"{self.basicAtk} (+{self.weapon['攻擊力']})",
                    inline=False)
    embed.add_field(name="防禦力",
                    value=f"{self.basicDef} (+{self.weapon['防禦力']})",
                    inline=False)
    embed.add_field(name="敏捷度",
                    value=f"{self.basicAgi} (+{self.weapon['敏捷度']})",
                    inline=False)
    embed.add_field(name="運氣值",
                    value=f"{self.basicLuc} (+{self.weapon['運氣值']})",
                    inline=False)
    embed.add_field(name="金錢", value=self.money, inline=False)
    # embed.add_field(name="剩餘技能點", value=self.AP, inline=False)
    msg = await ctx.reply(embed=embed, ephemeral=public)
    if not public:
        await asyncio.sleep(30)
        await msg.delete()
    return


#reincarnation
async def reincarnacode(self, ctx):
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
    elif self.lv < 10:
        await ctx.reply("至少需要10等才能進行轉生喔")

    print(self.name, self.nowHp)
    allPosition = {
        "冒險者": [0, 0, 0, 0, 0],
    }
    basicValues = [
        random.randint(100, 150),
        random.randint(10, 15),
        random.randint(7, 10),
        random.randint(5, 7),
        random.randint(2, 5),
        random.randint(40, 60)
    ]
    value = allPosition["冒險者"]
    post = {
        "等級": 1,
        "exp": 0,
        "職位": "冒險者",
        "maxHp": basicValues[0] + value[0],
        "nowHp": basicValues[0] + value[0],
        "Atk": basicValues[1] + value[1],
        "Def": basicValues[2] + value[2],
        "Agi": basicValues[3] + value[3],
        "Luc": basicValues[4] + value[4],
        "maxSta": basicValues[5],
        "nowSta": basicValues[5],
        "money": 200,
        "技能": self.basicSkill,
        "狀態": [],
        "回合": 0,
        "地區": self.allArea[1],
        "teamid": ctx.author.id,
        "teamName": None,
        "teamMember": [ctx.author.mention.replace("!", "")],
        "boss": False,
        "已狩獵boss": {},
        "已狩獵": {},
        "對戰對象": int(),
        "對戰": False,
        "狩獵休息": [datetime.datetime.now(), 0],
        "探險休息": [datetime.datetime.now(), 0],
        "技能點": 0,
        "每日登入": 0,
        "每日爆裂": 0,
        'maxHp點': 0,
        "Atk點": 0,
        "Def點": 0,
        "Agi點": 0,
        "Luc點": 0,
        "maxSta點": 0
    }
    rpg.update_one({"id": ctx.author.id}, {"$set": post})
    rpg.update_one({"id": ctx.author.id}, {"$inc": {"死亡數": 1}})
    await ctx.reply('你再次以冒險者的身分回到這個世界啦~')
    return


async def resurrectcode(self, ctx):
    playerSet = Core.playerSet(self, rpg.find_one({"id": ctx.author.id}))
    if playerSet == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet + "\n但我幫你添了一筆資料")
        return
    print(self.name, self.nowHp)
    if '死亡' not in self.state:
        print(self.state)
        await ctx.reply('你還沒死啦=厶=')
        return
    allPosition = {
        "冒險者": [0, 0, 0, 0, 0],
        "劍士": [10, 7, 7, 0, 0],
        "遊俠": [0, 3, 0, 15, 1],
        "法師": [0, 15, 0, 1, 2],
        "聖騎士": [20, 0, 15, 0, 5],
        "狂戰士": [20, 25, -10, 0, 0],
        "魔劍士": [20, 10, 10, 0, 0],
        "刺客": [0, 15, 0, 15, 0],
        "盜賊": [0, 0, 0, 15, 15],
        "幻影遊俠": [0, 0, 0, 30, 0],
        "牧師": [15, 0, 7, 0, 15],
        "召喚師": [10, 15, 0, 0, 10],
        "爆裂法師": [0, 50, 0, 0, 0]
    }
    basicValues = [
        random.randint(90, 150),
        random.randint(10, 15),
        random.randint(7, 10),
        random.randint(5, 10),
        random.randint(2, 5),
        random.randint(40, 60)
    ]
    value = allPosition[self.position]
    post = {
        "nowHp": int(self.maxHp * 0.3),
        "nowSta": int(self.maxSta * 0.3),
        "exp": self.exp * 0.2,
        "狀態": [],
        "回合": 0,
        "地區": self.allArea[1],
        "teamid": ctx.author.id,
        "teamName": None,
        "teamMember": [ctx.author.mention.replace("!", "")],
        "boss": False,
        "對戰對象": int(),
        "對戰": False,
        "狩獵休息": [datetime.datetime.now(), 0],
        "探險休息": [datetime.datetime.now(), 0]
    }
    # post = {
    #           "等級":1, "exp":0,
    #           "maxHp":basicValues[0]+value[0], "nowHp":basicValues[0]+value[0],
    #           "Atk":basicValues[1]+value[1], "Def":basicValues[2]+value[2],
    #           "Agi":basicValues[3]+value[3], "Luc":basicValues[4]+value[4],
    #           "maxSta":basicValues[5], "nowSta":basicValues[5],
    #           "money":200, "背包":{},
    #           "武器":self.basicWeapon, "裝備":None,'寵物':None,
    #           "技能":self.basicSkill, "狀態":[],"回合":0,
    #           "地區":self.allArea[1], "副職":None,
    #           "teamid":ctx.author.id,"teamName":None,"teamMember":[ctx.author.mention.replace("!","")],
    #           "boss":False, "已狩獵boss":{}, "已狩獵":{},
    #           "對戰對象":int(), "對戰":False,
    #           "狩獵休息":[datetime.datetime.now(), 0],
    #           "探險休息":[datetime.datetime.now(), 0],
    #           "技能點":0, "每日登入":0, "每日爆裂":0,
    #           'maxHp點':0, "Atk點":0, "Def點":0, "Agi點":0, "Luc點":0, "maxSta點":0
    #           }
    rpg.update_one({"id": ctx.author.id}, {"$set": post})
    rpg.update_one({"id": ctx.author.id}, {"$inc": {"死亡數": 1}})
    await ctx.reply('你再次回到這個世界了~')
    return


async def dailycode(self, ctx):
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

    myDaily = rpg.find_one({"id": ctx.author.id})["每日登入"]
    print(myDaily)

    today = datetime.datetime.today() + datetime.timedelta(hours=8)
    if type(myDaily) == int:
        myDaily = today

    elif myDaily.day == today.day:
        await ctx.reply(f"你今天已經登入過了啦 > <")
        return

    if (myDaily + datetime.timedelta(days=1)).day == today.day:
        rpg.update_one({"id": ctx.author.id}, {"$inc": {"連續登入": 1}})
    else:
        rpg.update_one({"id": ctx.author.id}, {"$set": {"連續登入": 1}})

    rpg.update_one({"id": ctx.author.id}, {"$inc": {"累積簽到": 1}})

    accumulationDays = rpg.find_one({'id': ctx.author.id})['累積簽到']
    continuousDays = rpg.find_one({'id': ctx.author.id})['連續登入']

    await ctx.reply(f"這是你第 {accumulationDays} 天登入遊戲")
    await ctx.reply(f"連續 {continuousDays} 天簽到囉 (・o・)")

    if accumulationDays == 1:
        await ctx.reply("恭喜獲得超稀有道具 - 重生水晶\n小心不要死掉囉")
        Core.getSomething(self, rpg.find_one({'id': ctx.author.id}), "重生水晶")

    elif accumulationDays % 30 == 0:
        await ctx.reply("恭喜獲得超稀有道具 - 重生水晶")
        Core.getSomething(self, rpg.find_one({'id': ctx.author.id}), "重生水晶")

    elif accumulationDays % 20 == 0:
        await ctx.reply("恭喜獲得稀有道具 - 靈魂寶石")
        Core.getSomething(self, rpg.find_one({'id': ctx.author.id}), "靈魂寶石")

    elif accumulationDays % 10 == 0:
        await ctx.reply("獲得道具 - 技能卡包")
        Core.getSomething(self, rpg.find_one({'id': ctx.author.id}), "技能卡包")

    else:
        await ctx.reply("獲得 300 金幣")
        rpg.update_one({"id": ctx.author.id}, {"$inc": {"money": 300}})
    await ctx.reply(f"並獲得連續登入的額外獎勵{continuousDays*10}枚金幣")
    rpg.update_one({"id": ctx.author.id},
                   {"$inc": {
                       "money": continuousDays * 10
                   }})
    rpg.update_one({"id": ctx.author.id}, {"$set": {"每日登入": today}})


async def rolechangecode(self, ctx):
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

    try:
        author = ctx.author
        guild = ctx.guild
        for name, color in self.achievement.items():
            if discord.utils.get(guild.roles, name=name) == None:
                await guild.create_role(name=name, color=color)
            role = discord.utils.get(guild.roles, name=name)
            await author.add_roles(role)
        await ctx.reply("已將你所有成就轉換成身分組啦0ㄩ0")
    except:
        await ctx.reply("糟糕!發生錯誤,或許我沒權限管理您的身分組 0m0")


class BasicSet(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)

    @commands.command(name="start", description="創建帳號")
    async def startcmd(self, ctx):
        await startcode(self, ctx)
        return

    @slash_command(name="start", description="創建帳號")
    async def start(self, inter):
        await startcode(self, inter)
        return

    @commands.command(name="daily", description="每日登入")
    async def dailycmd(self, ctx):
        await dailycode(self, ctx)
        return

    @slash_command(name="daily", description="每日登入")
    async def daily(self, inter):
        await dailycode(self, inter)
        return

    @commands.command(name="rolechange", description="成就轉換身分組")
    async def rolechangecmd(self, ctx):
        await rolechangecode(self, ctx)
        return

    @slash_command(name="rolechange", description="成就轉換身分組")
    async def rolechange(self, ctx):
        await rolechangecode(self, ctx)
        return

    @commands.command(name="position", description="職位表")
    async def selectcmd(self, ctx):
        await selectcode(self, ctx)
        msg = ctx.message
        await msg.delete()
        return

    @slash_command(name="position", description="職位表")
    async def select(self, ctx):
        await selectcode(self, ctx)
        return

    @commands.command(name="info", description="查看屬性")
    async def infocmd(self, ctx, public=True):
        await infocode(self, ctx, public=public)
        msg = ctx.message
        await msg.delete()
        return

    @slash_command(name="info",
                   description="查看屬性",
                   options=[
                       Option("public",
                              "是否公開數值",
                              choices=[
                                  OptionChoice(name="Yes", value=0),
                                  OptionChoice(name="No", value=1)
                              ])
                   ])
    async def info(self, ctx, public=True):
        await infocode(self, ctx, public=public)
        return

    '''
    @slash_command(name="info",description="查看屬性",options=[
        Option("user", "你想看誰的數據", OptionType.USER)])
    async def info(self, ctx, user=None):
        await infocode(self, ctx, user=user)
        return
    '''

    @commands.command(name="resurrect", description="重生")
    async def resurrectcmd(self, ctx):
        await resurrectcode(self, ctx)
        return

    @slash_command(name="resurrect", description="重生")
    async def resurrect(self, ctx):
        await resurrectcode(self, ctx)
        return

    @commands.command(name="restart", description="轉生(職位、技能、等級將重製，請做好心理準備)")
    async def reincarnacmd(self, ctx):
        await reincarnacode(self, ctx)
        return

    @slash_command(name="reborn", description="轉生(職位、技能、等級將重製，請做好心理準備)")
    async def reincarna(self, ctx):
        await reincarnacode(self, ctx)
        return

    @commands.command(name="fix", description="修理用", hidden=True)
    async def fixcmd(self, ctx):
        for all in rpg.find():
            rpg.update_many({},
                            {"$set": {
                                "狩獵休息": (datetime.datetime.now(), 0)
                            }})
            rpg.update_many({},
                            {"$set": {
                                "探險休息": (datetime.datetime.now(), 0)
                            }})
            rpg.update_many({}, {"$set": {"累積簽到": 0}})

        await ctx.send("fix done")


def setup(bot):
    bot.add_cog(BasicSet(bot))
