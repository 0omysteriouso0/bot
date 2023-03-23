import discord
from discord.ext import commands
import pymongo
import random
import asyncio
import json
from dislash import slash_command, ActionRow, Button, ButtonStyle
import datetime
from core.core import Core

url = 'mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]

with open("monster.json", "r", encoding="utf-8") as monjson:
    mondata = json.load(monjson)


async def huntcode(self, ctx):
    #get who & where
    print(f"{ctx.channel}: {ctx.author.id}:{ctx.author}: {ctx.author.name}")
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

    check = Core.fightcheck(self)
    if check["content"] != None:
        if check["type"] == "stop":
            await ctx.reply(check["content"])
            return

    Core.monsterSet(self, self.area)
    print(self.area, self.monName)
    #rest
    seconds = (datetime.datetime.now() - self.huntrest[0]).total_seconds()
    if seconds < self.huntrest[1]:
        await ctx.reply(f"筋疲力盡的{self.name}還想休息一下")
        return
#damage
# n is damageIncrease(1~2)
    n = (random.random() + 1) / 2
    damage = int(
        (self.monDef / (self.monDef + self.Atk) * (n + 0.5)) * self.monDef)
    nowHp = self.nowHp - damage

    getmoney = int(self.monMoney * (n + self.Luc / (self.monMoney + self.Luc)))
    money = self.money + getmoney
    #reward
    # a is expIncrease
    a = int(self.monExp / 10)
    increase = (random.randint(-a, a))
    self.exp = self.exp + self.monExp + increase

    #dead or win (*there is《成就》冷血殺手)
    if nowHp <= 0:
        text = Core.dead(self, self.monName)
        if type(text) == str: await ctx.reply(text)
        else: await ctx.reply(embed=text)
        if self.monName == "雷電棉花糖雲" and "《成就》冷血殺手" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「冷血殺手」")
            # Core.getAch(self, "冷血殺手", 0x8f1e1e)

            # Core.getAch(self, "冷血殺手", 0x8f1e1e)
    else:
        if self.monName == "雷電棉花糖雲" and "《成就》冷血殺手" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「冷血殺手」")
        elif self.monName == "莓果兔":
            Core.getSomething(self, rpg.find_one({"id": self.id}), "新鮮莓果兔肉")
            if "《隱藏成就》請問您今天要來點兔子嗎?" not in self.achievement:
                await ctx.channel.send(
                    f"✨{self.tag} 獲得**隱藏**成就✨\n「請問您今天要來點兔子嗎?」")

        embed = discord.Embed(title=f'你打倒了{self.monName}!',
                              color=self.areaColor[self.area])
        if type(self.monPfp) == list:
            self.monPfp = random.choice(self.monPfp)
        pfp = self.pfp if self.monPfp == None else self.monPfp
        embed.set_thumbnail(url=str(pfp))
        embed.add_field(name=f"損失了{damage}點生命值",
                        value=f"目前生命: {nowHp}",
                        inline=False)
        embed.add_field(name=f"獲得了{self.monExp+increase}點經驗值",
                        value=f"目前exp: {self.exp}",
                        inline=False)
        embed.add_field(name=f"獲得了{getmoney}元",
                        value=f"目前金錢: {money}",
                        inline=False)
        await ctx.reply(embed=embed)
        hunted = self.hunted.get(self.monName) + 1 if self.hunted.get(
            self.monName) != None else 1
        huntedata = rpg.find_one({"_id": ctx.author.id})["已狩獵"]
        huntedata[self.monName] = hunted
        rpg.update_one({"_id": ctx.author.id}, {"$set": {f"已狩獵": huntedata}})

        #Reproduction huntRest
        rpg.update_one({"id": ctx.author.id}, {
            "$set": {
                "money": money,
                "nowHp": nowHp,
                "exp": self.exp,
                "狩獵休息": (datetime.datetime.now(), 0)
            }
        })

        while self.exp >= self.lv * 20:
            content = Core.lvup(self, rpg.find({"id": ctx.author.id}))
            if type(content) == tuple:
                await ctx.channel.send(embed=content[0])
                await ctx.channel.send(content[1])
            else:
                await ctx.channel.send(embed=content)

        if check["content"] != None:
            await ctx.channel.send(check["content"])

        if self.lv >= 5 and "《成就》初心冒險者" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「初心冒險者」")
        elif self.lv >= 10 and "《成就》中級冒險者" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「中級冒險者」")
        elif self.lv >= 25 and "《成就》老練冒險者" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「老練冒險者」")
        elif self.lv >= 40 and "《成就》頂尖冒險者" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「頂尖冒險者」")
        elif self.lv >= 50 and "《成就》終極冒險者" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「終極冒險者」")
        elif self.lv >= 70 and "《成就》大師" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「大師」")
        elif self.lv >= 99 and "《成就》頂點的王者" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「頂點的王者」")
        elif self.lv >= 999 and "《特殊成就》Lv.Max" not in self.achievement:
            await ctx.channel.send(f"✨{self.tag} 獲得成就✨\n「Lv.Max」")


#explore
async def explorecode(self, ctx):
    #get who & where
    print(f"{ctx.channel}: {ctx.author.id}:{ctx.author}: {ctx.author.name}")
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

    fightcheck = Core.fightcheck(self)
    if fightcheck["content"] != None:
        if fightcheck["type"] == "stop":
            await ctx.reply(fightcheck["content"])
            return

    Core.monsterSet(self, self.area)
    print(self.area)
    #rest
    seconds = (datetime.datetime.now() - self.advenrest[0]).total_seconds()
    if seconds < self.advenrest[1]:
        await ctx.reply(
            f"精疲力盡的{self.name}還想休息{int(self.advenrest[1] - seconds)}秒")
        return
#Treasure
#Money
    moneyBag = random.choice([{
        "名稱": '一小堆金幣',
        "金錢": random.randint(40, 100)
    }, {
        "名稱": '一袋錢',
        "金錢": random.randint(150, 300)
    }, {
        "名稱": '一小堆金幣',
        "金錢": random.randint(40, 100)
    }, {
        "名稱": '一袋錢',
        "金錢": random.randint(150, 300)
    }, {
        "名稱": "滿箱子的黃金",
        "金錢": random.randint(70, 100) * 10
    }])
    self.chestMoney = f"{moneyBag['名稱']} 共{moneyBag['金錢']}元"
    #寶石
    self.gemstone = random.choice(["紅", "黃", "綠", "藍", "紫", "七彩夢幻", "靈魂"
                                   ]) + "寶石"
    #武器
    self.getWeapon = Core.weaponSet(self, random.choice(self.fieldWeapon))
    #地區素材
    areaMaterial = random.choice(self.areaMaterial[self.area])

    #好壞道具
    badTreasure = [random.choice(mondata["chest"])] + [self.monster] * 3

    money_num = 2
    goodTreasure = [self.chestMoney] * money_num + [areaMaterial] * 2 + [
        self.getWeapon
    ] + ["技能卡包"] * 2 + [self.gemstone]

    treasure = [
        random.choice(goodTreasure),
        random.choice(goodTreasure),
        random.choice(badTreasure)
    ]
    #Increase
    #n is damageIncrease
    n = random.random() + 1
    #choice what Events
    Events = random.randint(0, 6)
    #AdvEvents
    notHappened = [
        "空手而歸......", "被抓去吃麻婆拉麵並昏倒了...", "探險到一半莫名其妙就變快樂遠足了~~",
        f"遇到了{self.monName}\n不過取得共識,彼此和平地打了個招呼"
      ]
    if self.area == self.active:
      notHappened = [
      "空手而歸......", 
      "找到了知識：原來python跟蟒蛇完全沒關係", 
      "找到了知識：C++只是一個玩笑，++C才能發生在運算之前", 
      "找到了知識：只要有「Chicken」、「 」、「\n」就能寫Chicken語言啦",
      "找到了知識：我沒開玩笑，真的有 Pig 語言！",
      "找到了知識：我沒開玩笑，真的有 Pig 語言！",
      f"遇到了{self.monName}\n覺得他又臭又長，就逃跑了"
    ]
    #notHappend
    if Events < 1:
        await ctx.reply(f"{random.choice(notHappened)}")
        rpg.update_one({"id": ctx.author.id},
                       {"$set": {
                           "探險休息": (datetime.datetime.now(), 25 * self.explore_bonus)
                       }})
#getSomething
    elif Events <= 5:
        getTreasure = random.choice(treasure)
        print(getTreasure)
        if self.area == self.active:
          questions = [
            "迴圈問題" ,
            "邏輯運算",
            "數學運算",
            "英文單字",
            "英文填空"
          ]
          question = random.choice(questions)
          # question = "英文填空"
          if question == "迴圈問題":
            timeout = 20
            _n = random.randint(5, 10)
            _m = _n + random.randint(0, 10); _m_str = "," + str(_m) if _m != 0 else ""
            _o = random.randint(0, 3); _o_str = "," + str(_o) if (_o != 0 and _m != "") else ""
            question = f"`for i in range({_n}{_m_str}{_o_str})` 會執行幾次？"
            
            _m = 2*_n if _m == 0 else _m
            _o = 1 if _o == 0 else _o
            options = [
               len(list(range(_n, _m+2, _o))), 
               len(list(range(_n, _m+1, _o))), 
               len(list(range(_n, _m-1, _o))),
               len(list(range(_n, _m-2, _o))), 
               len(list(range(_n, _m, _o+1))),
               len(list(range(_n, _m-1, _o+1))),
               len(list(range(_n, _m+1, _o+1)))
            ]
            options = options if len(options) < 5 else set(random.choice(options, k=4))
            options.append(len(list(range(_n, _m, _o)))) 
            options = list(set(options))

            print(options)
            random.shuffle(options)
            
            options_str = [f"({chr(ord('A') + index)}) {str(i)}" if i >= 0 else f"({chr(ord('A') + index)}) {str(48763)}" for index, i in list(enumerate(options))]
            options_str = "\n".join(options_str)

            ans = options.index(len(list(range(_n, _m, _o))))
            ans = chr(ord('A') + ans)
                      
          elif question == "邏輯運算":
            timeout = 30
            operator = ["OR", "AND", "XOR", "XOR"]
            num = ["1", "0"]
            times = random.randint(1, 4)
            command = random.choice(num)
            for i in range(times):
              command += " "
              command += random.choice(operator)
              command += " "
              command += random.choice(num)
              pass
            question = f"{command}"
            
            options = [
                "True",
                "False"
            ]
            options_str = [f"({chr(ord('A') + index)}) {str(i)}" for index, i in enumerate(options)]
            options_str = "\n".join(options_str)
            
            ans = options.index(str(bool(eval(command.lower().replace("xor", "^")))))
            ans = chr(ord('A') + ans)

          elif question == "數學運算":
            timeout = 20
            operator = ["+", "-", "*", "/", "%"]
            num = list(range(1, 100))
            times = random.randint(3, 5)
            command = str(random.choice(num))
            for i in range(times):
              command += " "
              command += random.choice(operator)
              if command[-1] == "/":
                # command = command[0:-3] + " " + random.choice(operator).replace("/", "+") + " int(" + command[-3:]
                command = command.replace("/", f"{random.choice(operator[:3])} int({random.choice(num)} / {random.choice(num)})")
                # command += " "
                # command += str(random.choice(num)) + ")"
                continue
              command += " "
              command += str(random.choice(num))

            question = f"{command}"
            print(command)
            options = [
               eval(command)+1, 
               eval(command)-1,
               eval(command)+int(eval(command)/10),
               eval(command)+int(eval(command)/10)+1, 
               eval(command)-int(eval(command)/10),
               eval(command)-int(eval(command)/10)-1
            ]
            options = random.choices(options,k=4)
            options.append(eval(command))
            options = list(set(options))

            print(options)
            random.shuffle(options)
            
            options_str = [f"({chr(ord('A') + index)}) {str(i)}" for index, i in list(enumerate(options))]
            options_str = "\n".join(options_str)

            ans = options.index(eval(command))
            ans = chr(ord('A') + ans)
            
          elif question == "英文單字":
            timeout = 20
            with open("English.json", "r", encoding="utf-8") as j:
              _data = json.load(j)

            text = random.choice(list(_data.items()))
            del _data[text[0]]

            question = f"{text[0]} 的意思是？"

            options = random.choices(list(_data.values()), k = 4)
            options.append(text[1])

            print(options)
            random.shuffle(options)
            
            options_str = [f"({chr(ord('A') + index)}) {str(i)}" for index, i in list(enumerate(options))]
            options_str = "\n".join(options_str)

            ans = options.index(text[1])
            ans = chr(ord('A') + ans)
          
          elif question == "英文填空":
            timeout = 20
            with open("English.json", "r", encoding="utf-8") as j:
              _data = json.load(j)

            text = random.choice(list(_data.items()))
            del _data[text[0]]

            emp_text = text[0][0] + "\_"*len(text[0][1:-1]) + text[0][-1]
            question = f"{emp_text}{text[1]} \n怎麼拼？"
            
            options_str = ""

            ans = text[0]
            
          topic_message = await ctx.reply(f"{question}\n{options_str}")
          def check(m):
            if m.reference is not None:
                if m.reference.message_id == topic_message.id:
                    return True
            return False
          try:
            input = await self.bot.wait_for("message", check=check, timeout=timeout)
          except asyncio.TimeoutError:
            await topic_message.reply("超時...")
            getTreasure = random.choice(badTreasure)

          else:
            _answer = input.content
            if _answer == ans:
              await input.reply("答對")
              getTreasure = random.choice(goodTreasure)
            else:
              await input.reply("答錯")
              getTreasure = random.choice(badTreasure)
            print(_answer)
          print(ans)
            
        #goodTreasure
        if getTreasure in goodTreasure:
            #Money
            if getTreasure in goodTreasure[:money_num]:
                money = self.money + moneyBag['金錢']
                rpg.update_one({"id": ctx.author.id},
                               {"$set": {
                                   "money": money
                               }})
            #else
            else:
                Core.getSomething(self, rpg.find({"id": ctx.author.id}),
                                  getTreasure)
            if type(getTreasure) == dict:
                getTreasure = getTreasure['名稱']
            await ctx.reply(f"{self.name} 找到了一個寶箱\n打開後裡面居然是 {getTreasure} !")
            await ctx.channel.send(f"你默默的把它收到背包裡OVO")
            rpg.update_one({"id": ctx.author.id},
                           {"$set": {
                               "探險休息": (datetime.datetime.now(), 45 * self.explore_bonus)
                           }})
    #badTreasure
        elif getTreasure in badTreasure:
            await ctx.reply(f"{self.name} 找到了一個寶箱\n打開後卻是 {getTreasure['名稱']} !"
                            )
            boxAtk = getTreasure["攻擊力"]
            boxMoney = getTreasure["金錢"] * n
            boxName = getTreasure["名稱"]
            boxDamage = int(boxAtk / (boxAtk + self.Def) * n * boxAtk)
            if getTreasure in mondata["chest"]:
                boxDamage = int(self.nowHp * (random.random() + 0.9) / 2)
                if getTreasure['名稱'] == "炸彈":
                    boxDamage = int(self.maxHp * (random.random() + 0.5) / 2)
            await ctx.channel.send(f"{boxName}害你遭受{boxDamage}點傷害...")
            nowHp = self.nowHp - boxDamage
            rpg.update_one({"id": ctx.author.id}, {"$set": {"nowHp": nowHp}})
            #dead
            if nowHp <= 0:
                text = Core.dead(self, boxName)
                if type(text) == str: await ctx.reply(text)
                else: await ctx.reply(embed=text)
                return
            #alive
            else:
                await ctx.channel.send(
                    f"但你還是從他身上得到了{int(boxMoney)}元\n目前生命{int(nowHp)}")
                money = self.money + int(boxMoney)
                rpg.update_one({"id": ctx.author.id}, {
                    "$set": {
                        "money": money,
                        "探險休息": (datetime.datetime.now(), 35 * self.explore_bonus)
                    }
                })


#Raid
    elif Events <= 6:
        await ctx.reply(f"你遭到{self.monName}的突襲")
        nowHp = self.nowHp - int(self.monAtk /
                                 (self.monAtk + self.Def) * n * self.monAtk)
        rpg.update_one({"id": ctx.author.id}, {"$set": {"nowHp": nowHp}})
        #dead
        if nowHp <= 0:
            text = Core.dead(self, self.monName)
            if type(text) == str: await ctx.reply(text)
            else: await ctx.reply(embed=text)
            return
        #alive
        else:
            await ctx.channel.send(
                f"損失了{int(self.monAtk/(self.monAtk+self.Def)*n*self.monAtk)}點生命值\n目前生命{int(nowHp)}"
            )
        rpg.update_one({"id": ctx.author.id},
                       {"$set": {
                           "探險休息": (datetime.datetime.now(), 30 * self.explore_bonus)
                       }})

        if fightcheck["content"] != None:
            await ctx.channel.send(fightcheck["content"])


async def healcode(self, ctx):
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

    if self.nowHp == self.maxHp:
        print(self.name)
        await ctx.reply('你的血量是滿的=n=')
        return
    healMoney = int(
        (self.maxHp - self.nowHp) * 1.5 * (0.7 + self.nowHp / self.maxHp))
    rpg.update_one({"id": ctx.author.id}, {"$inc": {"money": -healMoney}})
    rpg.update_one({"id": ctx.author.id}, {"$set": {"nowHp": self.maxHp}})
    await ctx.reply(
        f"{self.name}你花了{int(healMoney)}元回滿了血量\n(maxHp: {self.maxHp})")
    return


async def workcode(self, ctx):
    playerSet = Core.playerSet(self, rpg.find_one({"id": ctx.author.id}))
    if playerSet == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet + "\n但我幫你添了一筆資料")
        return


#check
    check = Core.check(self)
    playerData = rpg.find_one({"id": ctx.author.id})
    if check != None and check != f"{self.name}負債累累啊...\n用/work賺錢吧":
        if type(check) == str:
            await ctx.reply(check)
        else:
            await ctx.reply(embed=check)
        return
    elif playerData["地區"] != "休憩小鎮":
        await ctx.reply("你只能在休憩小鎮打工啦><")
        return
    elif playerData["nowSta"] <= 0:
        await ctx.reply(f"{self.name}因打工而累倒了")
        return

    rpg.update_one({"id": ctx.author.id}, {
        "$push": {
            "狀態": '打工'
        },
        "$set": {
            "useSta": 0,
            "打工時間": datetime.datetime.now()
        }
    })
    await ctx.reply("打工吧少年")
    await ctx.reply(f"{self.name}開始工作\n(海星之聲: 結束打工請使用/rest)")
    return


async def restcode(self, ctx):
    playerSet = Core.playerSet(self, rpg.find_one({"id": ctx.author.id}))
    if playerSet == "你還沒有登入過啦":
        channel = self.bot.get_channel(876055534757875724)
        await channel.send(f"gm-start {ctx.author.id}")
        await ctx.reply(playerSet + "\n但我幫你添了一筆資料")
        return


#check
    check = Core.check(self)
    if check != None:
        if "打工" in self.state:
            pass
        elif type(check) == str:
            await ctx.reply(check)
            return
        else:
            await ctx.reply(embed=check)
            return

    if '打工' in rpg.find_one({"id": ctx.author.id})["狀態"]:
        rpg.update_one({"id": ctx.author.id}, {"$pull": {"狀態": '打工'}})
        getmoney = int(self.useSta * 10)
        await ctx.reply(
            f"{self.name}取消打工\n共賺了{getmoney}元,消耗了{self.useSta}點體力\n目前體力: {self.nowSta}"
        )
    return


class Action(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)

    @commands.command(name="hunt", description="狩獵")
    async def huntcmd(self, ctx):
        await huntcode(self, ctx)
        return

    @slash_command(name="hunt", description="狩獵")
    async def hunt(self, ctx):
        await huntcode(self, ctx)
        return

    @commands.command(name="explore", description="探險")
    async def explorecmd(self, ctx):
        await explorecode(self, ctx)
        return

    @slash_command(name="explore", description="探險")
    async def explore(self, ctx):
        await explorecode(self, ctx)
        return

    @commands.command(name="heal", description="回復血量")
    async def healcmd(self, ctx):
        await healcode(self, ctx)
        return

    @slash_command(name="heal", description="回復血量\n(補越多寫愈划算)")
    async def heal(self, ctx):
        await healcode(self, ctx)
        return

    @commands.command(name="work", description="打工花體力賺錢\n(30秒消耗1體力)")
    async def workcmd(self, ctx):
        await workcode(self, ctx)
        return

    @slash_command(name="work", description="打工花體力賺錢\n(30秒消耗1體力)")
    async def workcode(self, ctx):
        await workcode(self, ctx)
        return

    @commands.command(name="rest", description="休息回復體力\n(90秒 -> 1 體力)")
    async def restcmd(self, ctx):
        await restcode(self, ctx)
        return

    @slash_command(name="rest", description="休息回復體力\n(90秒 -> 1 體力)")
    async def rest(self, ctx):
        await restcode(self, ctx)
        return


def setup(bot):
    bot.add_cog(Action(bot))
