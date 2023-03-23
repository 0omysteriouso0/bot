import discord
from discord.ext import commands
import pymongo
import random
import asyncio
import json
import copy
from dislash import slash_command, Option, OptionType
from core.core import Core

url = 'mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]
fboss = cluster["RPG"]["fightboss"]
fight = cluster["RPG"]["fight"]
team = cluster["RPG"]["team"]
bossdata = cluster["RPG"]["boss"]

with open("monster.json", "r", encoding="utf-8") as monjson:
    mondata = json.load(monjson)
with open("skill.json", "r", encoding="utf-8") as data:
    skilldata = json.load(data)


class bossCog(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)

    @slash_command(name="fight",
                   description="打架(低機率死亡)",
                   options=[Option("user", "挑戰對象", OptionType.USER)])
    async def fight(self, ctx, user=None):
        playerSet1 = Core.playerSet(self, rpg.find_one({"id": ctx.author.id}))
        if playerSet1 == "你還沒有登入過啦":
            channel = self.bot.get_channel(876055534757875724)
            await channel.send(f"gm-start {ctx.author.id}")
            await ctx.reply(playerSet1 + "\n但我幫你添了一筆資料")
            return

    #check
        check = Core.check(self)
        if check != None:
            if type(check) == str:
                await ctx.respond(check)
            else:
                await ctx.respond(embed=check)
            return

        selfId = self.id
        enemyId = user.id

        player2Set = Core.playerSet(self, rpg.find_one({"id": user.id}))
        if player2Set == "你還沒有登入過啦":
            await ctx.reply("這裡好像沒有這個人ㄟ")
            return
        check = Core.check(self)

        if check != None:
            if type(check) == str:
                await ctx.respond(check)
            else:
                await ctx.respond(embed=check)
            return

        if fight.count_documents({"id": ctx.author.id}) == 0:
            Core.playerSet(self, rpg.find_one({"id": selfId}))
            fight.insert_one(self.result)
            fight.update_one({"id": selfId},
                             {"$set": {
                                 "狀態": {},
                                 "對戰對象": enemyId
                             }})

            Core.playerSet(self, rpg.find_one({"id": enemyId}))
            fight.insert_one(self.result)
            fight.update_one({"id": enemyId},
                             {"$set": {
                                 "狀態": {},
                                 "對戰對象": selfId
                             }})
        return

    @slash_command(name="team",
                   description="組隊",
                   options=[
                       Option("user", "隊友", OptionType.USER),
                       Option("name", "隊伍名", OptionType.STRING)
                   ])
    async def team(self, ctx, user=None, name=None):
        playerSet = Core.playerSet(self, rpg.find_one({"id": ctx.author.id}))
        if playerSet == "你還沒有登入過啦":
            channel = self.bot.get_channel(876055534757875724)
            await channel.send(f"gm-start {ctx.author.id}")
            await ctx.reply(playerSet + "\n但我幫你添了一筆資料")
            return

        check = Core.check(self)
        if check != None:
            if type(check) == str:
                await ctx.respond(check)
            else:
                await ctx.respond(embed=check)
            return
        user = user.mention.replace("!","")
        if team.count_documents({"teamid": self.teamid}) == 0:
            self.teamMember.append(user)
            data = {
                "teamid": self.teamid,
                "teamName": name,
                "teamMember": self.teamMember
            }
            team.insert_one(data)
        else:
            myTeam = team.find_one({"teamid": self.teamid})
            teamMember = myTeam["teamMember"].append(user)
            team.update_one({"teamid": self.teamid},
                            {"$set": {
                                "teamMember": teamMember
                            }})
        rpg.update_one({"tag": user}, {"$set": {"teamid": self.teamid}})
        await ctx.reply("組隊成功")
        return

    @slash_command(name="boss", description="召喚王(請準備萬全)")
    async def boss(self, ctx):
        playerSet = Core.playerSet(self, rpg.find_one({"id": ctx.author.id}))
        if playerSet == "你還沒有登入過啦":
            channel = self.bot.get_channel(876055534757875724)
            await channel.send(f"gm-start {ctx.author.id}")
            await ctx.reply(playerSet + "\n但我幫你添了一筆資料")
            return
        with open("boss.json", "r", encoding="utf-8") as i:
            bossdatas = json.load(i)

    #check
        check = Core.check(self)
        if check != None:
            if type(check) == str:
                await ctx.respond(check)
            else:
                await ctx.respond(embed=check)
            return

    #Bossdata
        bosspost = self.areaboss[self.area]["Boss"]
        if bosspost == None:
            await ctx.reply("此處還沒有王ㄟ，敬啟期待下個版本")
            return
        #BossLv
        try:
            bossLv = self.huntedBoss[self.areaboss[self.area]["Boss"]["名稱"]]
            print(bossLv)
        except:
            bossLv = 0
        #Bossdata setting
        for i in self.areaboss[self.area]:
            if i != "Boss":
                bosspost[i] = self.areaboss[self.area][i]
            else:
                for j in self.areaboss[self.area]["Boss"]:
                    if j in ["maxHp", "nowHp", "Atk", "Def", "Spd", "Luc"]:
                        bosspost[j] = int(bossdatas[bosspost['名稱']][j] *
                                          (bossLv + 1))

        #Bossdata insert
        bosspost["_id"] = f"{ctx.guild.id}{bosspost['id']}"
        bosspost["lv"] = bossLv
        if bossdata.count_documents({"_id": bosspost["_id"]}) == 0:
            bossdata.insert_one(bosspost)
        else:
            # bossdata.update_one({"_id":bosspost["_id"]},{"$set":bosspost})
            return

        #if not fighting boss則放入競技場
        if fboss.count_documents({"id": ctx.author.id}) == 0:
            for tag in self.teamMember:
                Core.playerSet(self, rpg.find_one({"tag": tag}))
                fboss.insert_one(self.result)
                print(tag)
                fboss.update_one({"tag": tag}, {"$set": {"狀態": {}}})

    #若已在競技場 return
        else:
            # fboss.update_one({"id":ctx.author.id},{"$set":self.result})
            return

        #send Boss embed
        embed = discord.Embed(title=f"地區: {self.area}", color=0xff0000)
        embed.set_author(name=f"**{bosspost['名稱']}**")
        if bossLv != 0:
            embed.set_author(name=f"**{bosspost['名稱']}**\n難度級別: {bossLv} 級")
        embed.add_field(name="血量", value=int(bosspost['maxHp']), inline=False)
        embed.add_field(name="攻擊力", value=int(bosspost['Atk']), inline=False)
        embed.add_field(name="防禦力", value=int(bosspost['Def']), inline=False)
        embed.add_field(name="敏捷度", value=int(bosspost['Spd']), inline=False)
        embed.add_field(name="運氣值", value=int(bosspost['Luc']), inline=False)
        embed.set_image(url=bosspost['大圖'])
        embed.set_footer(
            text="輸入 /skill 來發技打王喔\n(或者輸入 /flee 脫離戰鬥喔)\n備註:逃跑=個人離開並退出隊伍")
        await ctx.respond(embed=embed)
        return

    @slash_command(name="flee", description="逃跑")
    async def flee(self, ctx):
        playerSet = Core.playerSet(self, rpg.find_one({"id": ctx.author.id}))
        if playerSet == "你還沒有登入過啦":
            channel = self.bot.get_channel(876055534757875724)
            await channel.send(f"gm-start {ctx.author.id}")
            await ctx.reply(playerSet + "\n但我幫你添了一筆資料")
            return
        check = Core.check(self)
        if check != None:
            if type(check) == str:
                if "別在打王途中分心" not in check:
                    await ctx.respond(check)
                    return
            else:
                await ctx.respond(embed=check)
                return

#|==============|沒打王|==============|
        if fboss.count_documents({"id": ctx.author.id}) == 0:
            await ctx.reply("沒4，你很安全")
            return

        else:
            bossid = f'{ctx.guild.id}{self.areaboss[self.area]["Boss"]["id"]}'
            bossdata.delete_one({"_id": bossid})
            fboss.delete_one({"_id": self.id})
            await ctx.reply("逃跑成功")
            return

    @slash_command(name="skill",
                   description="你的技能",
                   options=[
                       Option("useskill", "你的技能", OptionType.STRING),
                       Option("user", "若技能為輔助再填對象", OptionType.USER)
                   ])
    async def useskill(self, ctx, useskill=None, user=None):
        playerSet = Core.playerSet(self, rpg.find_one({"id": ctx.author.id}))
        if playerSet == "你還沒有登入過啦":
            channel = self.bot.get_channel(876055534757875724)
            await channel.send(f"gm-start {ctx.author.id}")
            await ctx.reply(playerSet + "\n但我幫你添了一筆資料")
            return
        check = Core.check(self)
        if check != None:
            if type(check) == str:
                if "別在打王途中分心" not in check:
                    await ctx.respond(check)
                    return
            else:
                await ctx.respond(embed=check)
                return

        CDkey = "nowCD"
        #|==============|沒打王|==============|
        if fboss.count_documents({
                "id": ctx.author.id
        }) == 0 and fight.count_documents({"id": ctx.author.id}) == 0:
            CDkey = "CD"

            player = rpg.find({"id": ctx.author.id})
            for i in player:
                player = i
            playerSkill = player["技能"]

            if useskill != None:
                skill = playerSkill[useskill]
                embed = discord.Embed(title=f'**{skill["名稱"]}**\n' + "-" * 20,
                                      color=0x8a8a8a)
                skilltype = skill["type"]
                skilltype = f"({skilltype})" if skilltype else ""

                embed.add_field(name=f"名稱: {skill['名稱']+skilltype}\n" +
                                f"等級: {skill['Lv']}/{skill['lvMax']}\n" +
                                f'威力: {int(skill["威力"]*(skill["Lv"] + 4)/5)}' +
                                " " * 4 + f'命中: {skill["命中"]}' + " " * 4 +
                                f'CD: {skilldata[useskill]["CD"]}\n',
                                value="​​")
                if skill.get("效果"):
                    for skillEffectName, skillEffect in skill.get(
                            "效果").items():
                        embed.add_field(
                            name=f'效果 - {skillEffect.get("name","-"*3)}',
                            value=f'效果強度: {skillEffect.get("lv","-"*3)}\n'
                            f'回合: {skillEffect.get("time","-"*3)}' + " " * 4 +
                            f'命中機率: {skillEffect.get("chance","-"*3)}')
                if skill.get("能力"):
                    for skillEffectName, skillEffect in skill.get(
                            "能力").items():
                        embed.add_field(name="提升能力 - " + skillEffectName,
                                        value=f'效果強度: {skillEffect}')

                await ctx.reply(embed=embed)
                return

        if useskill == None:
            if fboss.count_documents({"id": ctx.author.id}) != 0:
                player = fboss.find({"id": ctx.author.id})
                for i in player:
                    player = i
                playerSkill = player["技能"]

            embed = discord.Embed(title=f'{self.name}的技能列表\n' + "-" * 20,
                                  color=0x8a8a8a)
            for name, info in playerSkill.items():
                skilltype = info["type"]
                skilltype = f"({skilltype})" if skilltype else ""
                embed.add_field(
                    name=f"{name+skilltype}",
                    value=f'威力: {int(info["威力"]*(info["Lv"] + 4)/5)}' +
                    " " * 4 + f'命中: {info["命中"]}' + " " * 4 +
                    f'CD: {info[CDkey]}')
            await ctx.reply(embed=embed)
            return

        else:
            """
          if fight.count_documents({"id":ctx.author.id}) != 0:
            Core.playerSet(self, fight.find_one({"id":ctx.author.id}))
            Boss = fight.find_one({"_id":self.enemy})
            temp = fboss
            fboss = fight
          """
            if fboss.count_documents({"id": ctx.author.id}) != 0:
                Core.playerSet(self, fboss.find_one({"id": ctx.author.id}))
                bossid = f'{ctx.guild.id}{self.areaboss[self.area]["Boss"]["id"]}'
                Boss = bossdata.find_one({"_id": bossid})

                Core.bossSet(self, Boss)
            skill = self.skill.get(useskill)
            n = random.uniform(0, 0.7)

            skillType = self.skill[useskill]["type"]
            skillName = self.skill[useskill]["名稱"]
            skillLv = self.skill[useskill]["Lv"]
            skillPower = self.skill[useskill]["威力"]
            skillCD = self.skill[useskill]["nowCD"]

            #state
            statePower = self.state.get(
                "力量", {"lv": 0})["lv"] - self.state.get("虛弱", {"lv": 0})["lv"]
            stateDamage = self.bossState.get(
                "抗性", {"lv": 0})["lv"] - self.bossState.get("易傷",
                                                            {"lv": 0})["lv"]
            stateBossDodge = self.bossState.get(
                "迅捷", {"lv": 0})["lv"] - self.bossState.get("緩速",
                                                            {"lv": 0})["lv"]
            stateSpeed = self.state.get(
                "專注", {"lv": 0})["lv"] - self.state.get("恍神", {"lv": 0})["lv"]
            stateLuck = self.state.get("幸運", {"lv": 0})["lv"] - self.state.get(
                "詛咒", {"lv": 0})["lv"]

            if skillCD > 0:
                await ctx.reply("冷卻還沒好...\n你還要再等 " + str(skillCD) + " 回合")
                return

            else:
                #===============================玩家回合===============================
                skillreCD = self.skill[useskill]["CD"] + 1
                fboss.update_one(
                    {"id": self.id},
                    {"$set": {
                        "技能." + useskill + ".nowCD": skillreCD
                    }})
                #======================跳過======================
                stopstate = {"冰凍", "威嚇"}
                stopstate = stopstate & set(self.state.keys())
                if stopstate:
                    for i in stopstate:
                        await ctx.reply(
                            f"{self.name}因為{self.state[i]['name']}而無法動彈")
                    pass
    #======================輔助======================
                elif skillType == "輔助":
                    skillPower = n + (skillPower / 100) / 5 * (skillLv + 4)
                    skillPower = int(skillPower * self.Luc)
                    skillEffect = skill.get("能力")

                    # if skillEffect["chance"] < random.randint(0, 100):
                    #   return

                    #非全體輔助
                    if skill["Aim"] != "all" and skill["Aim"] != "enemies":
                        #設定目標
                        if skill["Aim"] == "other" and user != None:
                            skillAim = user.id
                        else:
                            skillAim = self.id
                        #能力提升
                        for effect in skillEffect.keys():
                            fboss.update_one({"id": skillAim},
                                             {"$inc": {
                                                 effect: skillPower
                                             }})

                        #給予狀態
                        skillStatu = skill.get("效果")
                        if skillStatu != None:
                            for i in skillStatu.keys():
                                name = i
                            state = skillStatu[name]
                            fboss.update_one({"_id": skillAim},
                                             {"$set": {
                                                 "狀態." + name: state
                                             }})

                    elif skill["Aim"] == "enemies":
                        #設定目標
                        if user != None:
                            skillAim = user.id
                        else:
                            skillAim = self.bossId
                            print(self.bossId)
                        # #能力提升
                        for effect in skillEffect.keys():
                            bossdata.update_one({"_id": self.bossId},
                                                {"$inc": {
                                                    effect: skillPower
                                                }})

                        #給予狀態
                        skillStatu = skill.get("效果")

                        if skillStatu != None:
                            if fboss.count_documents({"id": skillAim}) != 0:
                                # state = fboss.find_one({"id":skillAim})["狀態"]
                                # state.update(skillStatu)
                                for i in skillStatu.keys():
                                    name = i
                                    state = skillStatu[name]
                                    fboss.update_one(
                                        {"_id": skillAim},
                                        {"$set": {
                                            "狀態." + name: state
                                        }})

                            else:
                                # state = bossdata.find_one({"_id":skillAim})["狀態"]
                                # state.update(skillStatu)
                                for i in skillStatu.keys():
                                    name = i
                                    state = skillStatu[name]
                                    bossdata.update_one(
                                        {"_id": skillAim},
                                        {"$set": {
                                            "狀態." + name: state
                                        }})

                    #全體輔助
                    else:
                        #能力提升
                        for effect in skillEffect.keys():
                            fboss.update_one({"teamid": self.teamid},
                                             {"$inc": {
                                                 effect: skillPower
                                             }})
                        #給予狀態
                        skillStatu = skill.get("效果")
                        if skillStatu != None:
                            for i in skillStatu.keys():
                                name = i
                                state = skillStatu[name]
                                fboss.update_many(
                                    {"teamid": self.teamid},
                                    {"$set": {
                                        "狀態." + name: self.state
                                    }})
                    print(self.state)
                    await ctx.reply(self.name+"使用了"+skill["名稱"]+"\n" + \
                                    skill["敘述"])
                    return

    #=====================玩家攻擊=====================
                else:
                    #連擊設定
                    times = len(skill.get("hit", "1"))

                    for x in range(times):
                        if x != 0 and skill.get("hit"):
                            #連擊是否繼續
                            if random.randint(0,
                                              100) > skill["hit"][x]["chance"]:
                                break
                            else:
                                skillPower = skill["hit"][x]["威力"]

                        #攻擊威力: 0~0.7 + 技能威力 X 技能等級(每等加20%) X 力量狀態加成(每等加10%)
                        skillPower = n + (skillPower *
                                          (skillLv + 4) / 5 / 100) * (
                                              (statePower * 10) + 100) / 100

                        if type(skill["命中"]) == int:
                            skillHit = skill["命中"] * (stateSpeed + 1)
                            a = random.random() / 5
                            #迴避率: ((王敏捷度X2 - 自身敏捷度 / 王敏捷度) + 0 ~ 0.2) X 5*迴避狀態(每等加10%)
                            dodge = (
                                ((self.bossAgi * 2 - self.Agi) / self.bossAgi +
                                 a * 10) * 5) + stateBossDodge * 10
                            a = random.randint(0, skillHit)
                        #必中技能
                        else:
                            a, dodge = 1, 0

                        # 幸運不好事件: (王運氣 / 運氣) * 運氣狀態(從 10 每等降 1)
                        LucEventChance = self.bossLuc / self.Luc * (10 -
                                                                    stateLuck)
                        b = random.randint(0, 150)

                        hitTime = f"第 {x+1} 擊，" if times != 1 else " "

                        #dodge
                        if self.bossName == self.active.Boss.name:
                          dodge *= 5
                        if a <= dodge:
                          if hitTime: hitTime += "被"
                          text = f"{hitTime}{self.bossName}輕巧地躲過了你的攻擊" 
                          await ctx.reply(text)

                    #BossDamage
                        else:
                            會心一擊 = "會心一擊！" if n >= 0.5 else " "
                            #傷害: (攻擊**2 / 王防禦+攻擊) X 2*技能威力 X 抗性狀態(每等降10%傷害)
                            damage = int(self.Atk / (self.bossDef + self.Atk) *
                                         2 * skillPower * self.Atk)
                            if skillType == "破防":
                                damage = int(self.Atk * skillPower)

                            damage *= (100 - stateDamage * 10) / 100
                            # print(self.Atk/(self.bossDef+self.Atk))
                            # print(skillPower)
                            # print((100 - stateDamage*10)/100)

                            #傷害永不小於0
                            if damage < 0: damage = 0

                            self.bossNowHp = self.bossNowHp - damage

                            await ctx.reply(
                                f"{hitTime}{self.name}使出 {skillName}**{會心一擊}**對{self.bossName}造成{damage}點傷害\n{self.bossName}剩餘血量:{self.bossNowHp}"
                            )

                            if skill.get('效果') != None:
                                for key in skill["效果"].keys():
                                    if skill["效果"][key][
                                            "chance"] >= random.randint(
                                                0, 100):
                                        if skill["效果"][key]["Aim"] == "self":
                                            self.state[key] = skill["效果"][key]
                                            fboss.update_one(
                                                {"tag": self.tag},
                                                {"$set": {
                                                    "狀態": self.state
                                                }})
                                        elif skill["效果"][key][
                                                "Aim"] == "enemies":
                                            self.bossState[key] = skill["效果"][
                                                key]
                                            bossdata.update_one(
                                                {"_id": self.bossId}, {
                                                    "$set": {
                                                        "狀態": self.bossState
                                                    }
                                                })

                    else:
                        if x != 0:
                            x += 1

                    if x != 0:
                        await ctx.reply(f"共使出 {x} 連擊")

                    bossdata.update_one({"_id": self.bossId},
                                        {"$set": {
                                            "nowHp": self.bossNowHp
                                        }})
                    #=====================玩家攻擊結束=====================
                    #=====================玩家壞運氣=====================
                    #LucEvent
                    if LucEventChance > b:
                        LucEvents = [("被天外飛來的番茄砸到了", 3), ("跌了一跤", 5),
                                     ("因為昨晚吃的麻婆拉麵肚子突然痛了起來", 10),
                                     ("被不知道哪來的爆裂餘波波及到了", 20),
                                     ("踩到別人亂丟的樂O積木", 100)]
                        LucEvent, LucEventDamage = random.choice(LucEvents)
                        #幸運傷害: 事件威力/10 X 王運氣 X 0.2~1.2
                        LucEventDamage = int(LucEventDamage / 10 *
                                             self.bossLuc *
                                             (random.random() + 0.1))

                        await ctx.reply(self.name + LucEvent +
                                        f"\n受到{LucEventDamage}點傷害")

                        self.nowHp -= LucEventDamage

    #=====================玩家狀態=====================
    #===========回復===========
                    heal = {"回復"}
                    heal = heal & set(self.state.keys())
                    if heal:
                        for i in heal:
                            stateHeal = int(self.Luc *
                                            (random.random() + 0.5) *
                                            self.state["回復"]["lv"])

                            await ctx.reply(f"{self.name}回復了{stateHeal}點血量")

                            self.nowHp += stateHeal

            #===========傷害===========
                    burn = {"燃燒", "流血"}
                    burn = burn & set(self.state.keys())
                    if burn:
                        for i in burn:
                            stateDamage = int(self.bossLuc *
                                              (random.random() + 0.2) *
                                              self.state[i]["lv"] / 2)

                            await ctx.reply(
                                f'{self.name}因為{self.state[i]["name"]}效果，損失了{stateDamage}點血量'
                            )

                            self.nowHp -= stateDamage

                    poison = {"中毒", "立即傷害"}
                    poison = poison & set(self.state.keys())
                    if poison:
                        for i in poison:
                            stateDamage = int(
                                self.nowHp *
                                ((random.random() + 0.2) +
                                 (self.state[i]["lv"] * 10) / 100))

                            await ctx.reply(
                                f'{self.name}因為{self.state[i]["name"]}效果，損失了{stateDamage}點血量'
                            )

                        self.nowHp -= stateDamage

    #=====================玩家血量設置=====================
                    fboss.update_one({"id": ctx.author.id},
                                     {"$set": {
                                         "nowHp": self.nowHp
                                     }})


#===============================王回合===============================
                if self.bossNowHp > 0 and self.nowHp > 0:
                    player = random.choice(self.teamMember)

                    Core.playerSet(self, fboss.find_one({"tag": player}))
                    n = random.uniform(0, 0.7)

                    skill = random.choice(self.bossSkill)
                    if bossdata.find_one({"_id": self.bossId
                                          })["回合"] % bossdata.find_one(
                                              {"_id": self.bossId})["蓄力"] == 0:
                        skill = self.bossSpecial
                    skillType = skill["type"]
                    skillName = skill["名稱"]
                    skillPower = skill["威力"]

                    #state
                    statePower = self.bossState.get(
                        "力量", {"lv": 0})["lv"] - self.bossState.get(
                            "虛弱", {"lv": 0})["lv"]
                    stateDamage = self.state.get(
                        "抗性", {"lv": 0})["lv"] - self.state.get(
                            "易傷", {"lv": 0})["lv"]
                    stateBossDodge = self.state.get(
                        "迅捷", {"lv": 0})["lv"] - self.state.get(
                            "緩速", {"lv": 0})["lv"]
                    stateSpeed = self.bossState.get(
                        "專注", {"lv": 0})["lv"] - self.bossState.get(
                            "恍神", {"lv": 0})["lv"]
                    stateLuck = self.bossState.get(
                        "幸運", {"lv": 0})["lv"] - self.bossState.get(
                            "詛咒", {"lv": 0})["lv"]
                    #======================跳過======================
                    stopstate = {"冰凍", "威嚇"}
                    stopstate = stopstate & set(self.bossState.keys())
                    if stopstate:
                        for i in stopstate:

                            await ctx.reply(
                                f"{self.bossName}因為{self.bossState[i]['name']}而無法動彈"
                            )
    #======================輔助======================
                    else:
                        while skillType == "輔助":
                            if skill["chance"] < random.randint(0, 100):
                                continue
                            skillPower = n + (skillPower /
                                              100) / 5 * (skillLv + 4)
                            skillPower = int(skillPower * self.Luc)
                            skillEffect = skill.get("效果")

                            #非全體輔助
                            if skill["Aim"] != "all":
                                #設定目標
                                if skill["Aim"] == "other" and user != None:
                                    skillAim = user.id
                                else:
                                    skillAim = self.id
                                #能力提升
                                for effect in skillEffect:
                                    rpg.update_one(
                                        {"_id": skillAim},
                                        {"$inc": {
                                            effect: skillPower
                                        }})
                                #給予狀態
                                skillStatu = skill.get("效果")
                                if skillStatu != None:
                                    fboss.update_one(
                                        {"_id": skillAim},
                                        {"$push": {
                                            "狀態": skillStatu
                                        }})

                            #全體輔助
                            else:
                                #能力提升
                                for effect in skillEffect:
                                    fboss.update_many(
                                        {"teamid": self.teamid},
                                        {"$inc": {
                                            effect: skillPower
                                        }})
                                #給予狀態
                                skillStatu = skill.get("效果")
                                if skillStatu != None:
                                    fboss.update_many(
                                        {"teamid": self.teamid},
                                        {"$push": {
                                            "狀態": skillStatu
                                        }})
                            print(self.state)
                            skill = random.choice(self.bossSkill)

    #======================王攻擊======================
                        else:
                            times = len(skill.get("hit", "1"))
                            for x in range(times):
                                if x != 0:
                                    if skill.get("hit"):
                                        if random.randint(
                                                0, 100
                                        ) > skill["hit"][x]["chance"]:
                                            break
                                        else:
                                            skillPower = skill["hit"][x]["威力"]
                                if type(skill["命中"]) == int:
                                    skillHit = int(skill["命中"] *
                                                   (stateSpeed * 0.1 + 1))
                                    skillPower = n + (
                                        skillPower *
                                        (skillLv + 4) / 5 / 100) * (
                                            (statePower * 10) + 100) / 100
                                    a = random.random() / 5
                                    dodge = ((self.Agi * 2 - self.bossAgi) /
                                             self.Agi +
                                             a) * 5 * (stateBossDodge * 10 +
                                                       100) / 100
                                    print(dodge)
                                    print(skillHit)
                                    a = random.randint(0, skillHit)
                                else:
                                    a, dodge = 1, 0

                                LucEventChance = self.Luc / self.bossLuc * (
                                    10 - stateLuck)
                                b = random.randint(0, 150)

                                if a <= dodge:
                                    dodgeMessage = random.choice(
                                        ["輕巧地閃過了攻擊", "驚險的避過了攻擊"])
                                    await ctx.reply(self.name + dodgeMessage)

                                else:
                                    會心一擊 = "會心一擊！" if n >= 0.5 else " "
                                    hitTime = f"第 {x+1} 擊，" if times != 1 else " "

                                    damage = int(self.bossAtk /
                                                 (self.Def + self.bossAtk) *
                                                 2 * skillPower * self.bossAtk)
                                    if skillType == "破防":
                                        damage = int(self.bossAtk * skillPower)

                                    damage *= (100 - stateDamage * 10) / 100

                                    self.nowHp = self.nowHp - damage

                                    await ctx.reply(
                                        f"{hitTime}{self.bossName}使出{skillName}**{會心一擊}**對{self.name}造成{damage}點傷害\n{self.name}剩餘血量:{self.nowHp}"
                                    )

                                    if skill.get('效果') != None:
                                        if list(skill["效果"].values(
                                        ))[0]["chance"] >= random.randint(
                                                0, 100):
                                            await ctx.reply(
                                                f"並對{self.name}造成{skill['效果'][list(skill['效果'].keys())[0]]['name']}的效果"
                                            )
                                            self.state.update(skill["效果"])
                                            fboss.update_one(
                                                {"tag": self.tag},
                                                {"$set": {
                                                    "狀態": self.state
                                                }})
                            else:
                                if x != 0:
                                    x += 1
                            if x != 0:
                                await ctx.reply(f"共使出 {x} 連擊")

                            fboss.update_one({"_id": self.id},
                                             {"$set": {
                                                 "nowHp": self.nowHp
                                             }})

                            if LucEventChance > b:
                                LucEvents = [("被天外飛來的番茄砸到了", 10), ("跌了一跤", 5),
                                             ("因為昨晚吃的麻婆拉麵肚子突然痛了起來", 20),
                                             ("被不知道哪來的爆裂餘波波及到了", 30),
                                             ("踩到別人亂丟的樂O積木", 100)]
                                LucEvent, LucEventDamage = random.choice(
                                    LucEvents)
                                LucEventDamage = int(LucEventDamage / 10 *
                                                     self.Luc)
                                self.bossNowHp -= LucEventDamage
                                await ctx.reply(self.bossName + LucEvent +
                                                f"\n受到{LucEventDamage}點傷害")
                                bossdata.update_one(
                                    {"_id": self.bossId},
                                    {"$inc": {
                                        "nowHp": -LucEventDamage
                                    }})

                    #===========回復===========
                            heal = {"回復"}
                            heal = heal & set(self.bossState.keys())
                            if heal:
                                for i in heal:
                                    stateHeal = int(self.Luc *
                                                    (random.random() + 0.5) *
                                                    self.bossState[i]["lv"])

                                    await ctx.reply(
                                        f"{self.bossName}回復了{stateHeal}點血量")

                                    self.bossNowHp += stateHeal

                    #===========傷害===========
                            burn = {"燃燒", "流血"}
                            burn = burn & set(self.bossState.keys())
                            if burn:
                                for i in burn:
                                    stateDamage = int(self.bossLuc *
                                                      (random.random() + 0.2) *
                                                      self.bossState[i]["lv"] /
                                                      2)

                                    await ctx.reply(
                                        f'{self.bossName}因為{self.bossState[i]["name"]}效果，損失了{stateDamage}點血量'
                                    )

                                    self.bossNowHp -= stateDamage

                            poision = {"中毒", "立即傷害"}
                            poision = poision & set(self.bossState.keys())
                            if poision:
                                for i in poision:
                                    stateDamage = int(
                                        self.bossNowHp *
                                        (random.random() + 0.2) *
                                        (self.bossState[i]["lv"] * 10) / 100)

                                    await ctx.reply(
                                        f'{self.bossName}因為{self.bossState[i]["name"]}效果，損失了{stateDamage}點血量'
                                    )

                                    self.bossNowHp -= stateDamage

    #=====================玩家血量設置=====================
                            bossdata.update_one(
                                {"_id": self.bossId},
                                {"$set": {
                                    "nowHp": self.bossNowHp
                                }})

                if self.nowHp < 0:
                    resurrect = {"毅力"}
                    resurrect = resurrect & set(self.state.keys())
                    if resurrect:
                        for i in resurrect:
                            if random.randint(
                                    0, 100) < (self.state[i]["lv"] * 10):
                                fboss.update_one({"id": self.id},
                                                 {"$set": {
                                                     "nowHp": 1
                                                 }})
                                fboss.update_one(
                                    {"id": self.id},
                                    {"$inc": {
                                        "狀態." + i + ".lv": -1
                                    }})
                                self.nowHp = 1
                                await ctx.reply(
                                    f'{self.name} 因為{self.state[i]["name"]}，而勉強活下來了'
                                )
                                break

                if self.bossNowHp < 0:
                    resurrect = {"毅力"}
                    resurrect = resurrect & set(self.bossState.keys())
                    if resurrect:
                        for i in resurrect:
                            if random.randint(
                                    0, 100) < (self.bossState[i]["lv"] * 10):
                                bossdata.update_one({"_id": self.bossId},
                                                    {"$set": {
                                                        "nowHp": 1
                                                    }})
                                bossdata.update_one(
                                    {"id": self.bossId},
                                    {"$inc": {
                                        "狀態." + i + ".lv": -1
                                    }})
                                self.bossNowHp = 1
                                await ctx.reply(
                                    f'{self.bossName} 因為{self.bossState[i]["name"]}，而勉強活下來了'
                                )
                                break

            #死王
                if self.bossNowHp <= 0 and self.nowHp > 0:
                    self.huntedBoss[self.bossName] = self.bossLv + 1
                    rpg.update_one({"id": self.id},
                                   {"$set": {
                                       "已狩獵boss": self.huntedBoss
                                   }})
                    if self.bossLv <= 0:
                        #擊殺獎勵
                        Core.getSomething(self, rpg.find_one({"id": self.id}),
                                          self.bossWeapon)
                        #通關(大獎)
                        member = random.choice(self.teamMember)
                        Core.getSomething(self, rpg.find({"tag": member}),
                                          self.bossPet[0])

                    for tag in self.teamMember:
                        if fboss.count_documents({"tag": tag}) == 0:
                            continue
                        if self.bossLv <= 0:
                            for items in self.bossPet[1:]:
                                Core.getSomething(self,
                                                  rpg.find_one({"tag": tag}),
                                                  items)

                        for items in self.bossItem:
                            Core.getSomething(self, rpg.find_one({"tag": tag}),
                                              items)

                        Core.playerSet(self, rpg.find_one({"tag": tag}))
                        self.exp += self.bossExp
                        rpg.update_one({"tag": tag},
                                       {"$set": {
                                           "exp": self.exp
                                       }})
                        self.money += int(self.bossMoney /
                                          len(self.teamMember))
                        rpg.update_one({"tag": tag},
                                       {"$set": {
                                           "money": self.money
                                       }})

                        lv = self.lv
                        while self.exp >= self.lv * 20:
                            rpgplayer = rpg.find_one({"tag": tag})
                            content = Core.lvup(self, rpgplayer)
                            if type(content) == tuple:
                                await ctx.channel.send(rpgplayer["name"] +
                                                       content[1])
                        else:
                            if lv != self.lv:
                                nowInfo = fboss.find_one({"id": self.id})
                                newInfo = rpg.find_one({"id": self.id})
                                embed = discord.Embed(
                                    title=
                                    f"{self.name}你已升級成等級: Lv.{lv} → {self.lv}",
                                    color=0x16d070)
                                embed.set_thumbnail(url=self.pfp)
                                embed.add_field(
                                    name="生命值",
                                    value=
                                    f'+{int(newInfo["maxHp"] - nowInfo["maxHp"])}',
                                    inline=False)
                                embed.add_field(
                                    name="攻擊力",
                                    value=
                                    f'+{int(newInfo["Atk"] - nowInfo["Atk"])}',
                                    inline=False)
                                embed.add_field(
                                    name="防禦力",
                                    value=
                                    f'+{int(newInfo["Def"] - nowInfo["Def"])}',
                                    inline=False)
                                embed.add_field(
                                    name="敏捷度",
                                    value=
                                    f'+{int(newInfo["Agi"] - nowInfo["Agi"])}',
                                    inline=False)
                                embed.add_field(
                                    name="運氣值",
                                    value=
                                    f'+{int(newInfo["Luc"] - nowInfo["Luc"])}',
                                    inline=False)
                                await ctx.send(embed=embed)

                            fboss.delete_one({"id": self.id})

                    bossdata.delete_one({"_id": self.bossId})

                    return

                elif self.bossNowHp <= 0 and self.nowHp <= 0:
                    embed = discord.Embed(title=f'兩敗俱傷，握手言和回家囉=v=',
                                          color=0x8a8a8a)
                    embed.set_thumbnail(url=self.bossPfp)
                    await ctx.reply(embed=embed)
                    bossdata.delete_one({"_id": self.bossId})
                    fboss.delete_one({"_id": self.id})
                    return
            #死人
                elif self.nowHp <= 0:
                    text = Core.dead(self, self.bossName, self.bossPfp)
                    if type(text) == str: await ctx.reply(text)
                    else: await ctx.reply(embed=text)
                    fboss.delete_one({"_id": self.id})
                    if len(self.teamMember) > 1:
                        if fboss.count_documents({"teamid": self.teamid}) == 0:
                            embed = discord.Embed(
                                title=f'{self.teamName}全軍覆沒...',
                                color=0x8a8a8a)
                            embed.set_thumbnail(url=self.bossPfp)
                            await ctx.reply(embed=embed)
                            bossdata.delete_one({"_id": self.bossId})
                            fboss.delete_one({"_id": self.id})
                            return
                    else:
                        bossdata.delete_one({"_id": self.bossId})
                        fboss.delete_one({"_id": self.id})
                        return

            #CD減少、重製CD
                else:
                    statelist = [
                        "不屈", "回復", "冰凍", "威嚇", "燃燒", "流血", "中毒", "立即傷害", "加速",
                        "緩速", "抗性", "易傷", "力量", "虛弱", "專注", "恍神", "祝福", "詛咒"
                    ]
                    statelen = len(statelist)
                    for i in range(len(statelist)):
                        if i >= statelen - i - 1:
                            break
                        fboss.update_many(
                            {
                                "teamid": self.teamid,
                                "狀態." + statelist[i]: {
                                    "$exists": True
                                }
                            }, {"$inc": {
                                "狀態." + statelist[i] + ".time": -1
                            }})
                        players = fboss.find_one({
                            "teamid": self.teamid,
                            "狀態." + statelist[i] + ".time": {
                                "$lte": 0
                            }
                        })
                        if players:
                            # print(players)
                            # for j in players:
                            await ctx.reply(self.state[statelist[i]]['name'] +
                                            "效果已消失")
                        fboss.update_many(
                            {
                                "teamid": self.teamid,
                                "狀態." + statelist[i] + ".time": {
                                    "$lte": 0
                                }
                            }, {"$unset": {
                                "狀態." + statelist[i]: 1
                            }})
                        players = fboss.find_one({
                            "teamid": self.teamid,
                            "狀態." + statelist[statelen - i - 1] + ".time": {
                                "$lte": 0
                            }
                        })
                        if players:
                            # for j in players:
                            await ctx.reply(statelist[statelen - i - 1] +
                                            "效果已消失")
                        fboss.update_many(
                            {
                                "teamid": self.teamid,
                                "狀態." + statelist[statelen - i - 1] + ".time":
                                {
                                    "$lte": 0
                                }
                            }, {
                                "$unset": {
                                    "狀態." + statelist[statelen - i - 1]: 1
                                }
                            })

                        fboss.update_many(
                            {
                                "teamid": self.teamid,
                                "狀態." + statelist[statelen - i - 1]: {
                                    "$exists": True
                                }
                            }, {
                                "$inc": {
                                    "狀態." + statelist[statelen - i - 1] + ".time":
                                    -1
                                }
                            })

                        bossdata.update_one(
                            {
                                "_id": self.bossId,
                                "狀態." + statelist[i]: {
                                    "$exists": True
                                }
                            }, {"$inc": {
                                "狀態." + statelist[i] + ".time": -1
                            }})
                        players = bossdata.find_one({
                            "teamid": self.bossId,
                            "狀態." + statelist[i] + ".time": {
                                "$lte": 0
                            }
                        })
                        if players:
                            # for j in players:
                            await ctx.reply(self.bossName + "的" +
                                            statelist[i] + "效果已消失")
                        players = bossdata.find_one({
                            "teamid": self.bossId,
                            "狀態." + statelist[statelen - i - 1] + ".time": {
                                "$lte": 0
                            }
                        })
                        if players:
                            # for j in players:
                            await ctx.reply(self.bossName + "的" +
                                            statelist[statelen - i - 1] +
                                            "效果已消失")
                        bossdata.update_one(
                            {
                                "_id": self.bossId,
                                "狀態" + statelist[statelen - i - 1] + ".time": {
                                    "$lte": 0
                                }
                            }, {
                                "$unset": {
                                    "狀態" + statelist[statelen - i - 1]: 1
                                }
                            })
                        bossdata.update_one(
                            {
                                "_id": self.bossId,
                                "狀態" + statelist[i] + ".time": {
                                    "$lte": 0
                                }
                            }, {"$unset": {
                                "狀態" + statelist[i]: 1
                            }})

                        bossdata.update_one(
                            {
                                "_id": self.bossId,
                                "狀態." + statelist[statelen - i - 1]: {
                                    "$exists": True
                                }
                            }, {
                                "$inc": {
                                    "狀態." + statelist[statelen - i - 1] + ".time":
                                    -1
                                }
                            })

                    for user in self.teamMember:
                        userskills = fboss.find_one({"tag": user})["技能"]
                        for skills in userskills.keys():
                            if userskills[skills]["nowCD"] == 0:
                                continue
                            userskills[skills]["nowCD"] -= 1
                        fboss.update_one({"tag": user},
                                         {"$set": {
                                             "技能": userskills
                                         }})

                    bossdata.update_one({"_id": self.bossId},
                                        {"$inc": {
                                            "回合": 1
                                        }})
                    await ctx.reply("-" * 20)
                    return


def setup(bot):
    bot.add_cog(bossCog(bot))
