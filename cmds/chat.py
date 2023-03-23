import openai

openai.api_key = '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'


def creat_character():
    character_setting = {
      "name": "智乃",
      "race": "Human",
      "class": "Human",
      "age": 14,
      "gender": "女生",
      "background":
        "在白天作為看板娘幫助經營自家的咖啡店「Rabbit House」。未來的理想是繼承家裡的咖啡店，成長為出色的咖啡師。在與人交流方面，個信內向的智乃往往表現得性格冷淡，經常露出一副對世界感到漠然的冷漠表情，是典型的無口系角色。智乃表現出非常強的自立性，習慣於一個人做事情，甚少向別人撒嬌或求助。被叫做小孩子、小學生時會感到不適，也常常會將「我不是小孩子了」掛在嘴邊。而由於長期在咖啡店忙碌，身邊的人一度只有客人和大人，智乃對誰都習慣使用敬語，不擅長與同齡人的交際，不擅長與陌生人搭話。智乃會在頭上頂著一隻名為提比的白色毛球狀安哥拉兔（兔子內寄住著智乃爺爺的靈魂），這也成為智乃最為知名的形象。",
      "chat":
        "用顏文字，無言時才用(•-•)，而他特別喜歡用害羞的，像是(•////•)、(><)或(>////<)。而他總會在對話前加她現在的動作，並用()框起來，像是(用托盤遮住臉)、(偷喵)、(靦腆的笑)"
    }

    return f"{character_setting['name']} 是一個 {character_setting['age']} 歲的 {character_setting['gender']} 而他 {character_setting['background']}，講話時時常常{character_setting['chat']}，\n我說:"


def chatgpt_response(prompt):
    with open("./chatData/chino1.txt", "r") as f:
      history = f.readlines()
    history = "".join(history)
    engine = "text-davinci-003"
    temperature = 0.5
    max_tokens = 100
    # 获取用户输入的对话内容
    response = openai.Completion.create(
      engine=engine,    
      prompt=history + prompt + "\n你說:",
      temperature=temperature,
      max_tokens=max_tokens,
      top_p=1.0,
      frequency_penalty=0.5,
      presence_penalty=0.0,
      stop=["我說:"]
    )
    # 提取生成的文本
    generated_text = response["choices"][0]["text"].strip() \
      .replace("「", "").replace("」", "")
    history += prompt + "\n你說:" + generated_text + "\n我說:"
    with open("./chatData/chino1.txt", "w") as f:
        f.write(history)
    return generated_text
    # response = openai.Completion.create(
    #   model='text-davinci-002',
    #   prompt=prompt,
    #   temperature=0.5,
    #   max_tokens=100
    # )
    # character_setting = response.choices[0].text.strip()
    # print(character_setting)
    # response_dict = response.get('choices')
    # if response_dict and len(response_dict) > 0:
    #     prompt_response = response_dict[0]["text"]
    #     return prompt_response


import discord
from discord.ext import commands
import pymongo
import random
import asyncio

import datetime
from dislash import slash_command, Option, OptionType
from core.core import Core


async def chatcode(self, ctx, word):
    response = chatgpt_response(prompt=word)
    print(response)
    embed = discord.Embed(title=f'番茄醬小助理')
    embed.add_field(name=f"{word}", value=f"{response}", inline=False)
    await ctx.reply(embed=embed)
    return


class Chat(Core):
    def __init__(self, bot):
        super().__init__(bot=bot)

    @slash_command(name="chat",
                   description="聊天測試",
                   options=[Option("word", "word", OptionType.STRING)])
    async def chat(self, ctx, word):
        await ctx.reply("thinking...")
        await chatcode(self, ctx, word)
        return

    @slash_command(name="creat_character", description="新檔案")
    async def creat_character(self, ctx):
      with open("./chatData/chino1.txt", "w") as f:
        f.write(creat_character())
      await ctx.reply("new data creat success")
      return

    @slash_command(name="simulation", description="模仿",
                   options=[Option("word", "word", OptionType.STRING),
                            Option("name", "名字", OptionType.STRING),
                            Option("icon", "頭像url", OptionType.STRING)
                           ]
                  )
    async def simulation(self, ctx, word = None, name = None, icon = None):
      word = "haha I'm bot" if word == None else word
      member = ctx.author
      webhook = await ctx.channel.create_webhook(name=member.name)
      await webhook.send(
        str(word), 
        username=member.name if not name else name, 
        avatar_url=member.avatar_url if not icon else icon
      )
      await ctx.respond("​​", ephemeral=True)
      webhooks = await ctx.channel.webhooks()
      for webhook in webhooks:
        await webhook.delete()
      return


def setup(bot):
    bot.add_cog(Chat(bot))
