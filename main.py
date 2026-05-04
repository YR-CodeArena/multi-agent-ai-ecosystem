import discord
import os
from openai import AsyncOpenAI
import aiohttp
import asyncio
from bots_bios import tanjiro_bio, nezuko_bio, zenitsu_bio, akaza_bio, muzan_bio
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

ai_client = AsyncOpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=os.environ.get("GEMINI_KEY")
            )

class Engine(discord.Client):
    def __init__(self, prefix, bio, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix
        self.bio = bio
        self.bot_name = name
        self.chat_history = []
    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    async def on_message(self, message):
        if message.author == self.user:
            return
        

        anime_command = self.prefix + "anime"
        link_context = ""
        if message.content.startswith(anime_command):
            async with message.channel.typing():
                user_text = message.content[len(anime_command):].strip()
                message_payload = [{"role":"system", "content":f"You are {self.bot_name}. Act exactly like this: {self.bio}"}]
                message_payload.extend(self.chat_history[-10:])
                message_payload.append({"role":"user", "content": f"User Message: {user_text}"})
                response = await ai_client.chat.completions.create(
                        model="gemini-3.1-flash-lite-preview",
                        messages=message_payload,
                        temperature=0.8
                    )
                ai_reply = response.choices[0].message.content

                embed = discord.Embed(title=f"Anime: {user_text}", description=ai_reply, color=discord.Colour.random())
                embed.set_author(name=self.bot_name)

                formatted_query = user_text.replace(' ', '+')
                api_url = f"https://api.jikan.moe/v4/anime?q={formatted_query}&limit=1"
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                        
                            if len(data['data']) > 0:
                                image_url = data['data'][0]['images']['jpg']['large_image_url']
                                embed.set_image(url=image_url)
                

                await message.channel.send(embed=embed)

        elif self.prefix in message.content:
            async with message.channel.typing():
                user_text = message.content.replace(self.prefix, "").strip()
                full_user_input = user_text 
                link_context = ""
                if "http://" in message.content or "https://" in message.content:
                    await asyncio.sleep(2)
                    fetched_message = await message.channel.fetch_message(message.id)
                    if fetched_message.embeds:   
                        for embed in fetched_message.embeds:
                            if embed.title:
                                link_context += f"[Link Title: {embed.title}]"
                            if embed.description:
                                link_context += f"[Link Description: {embed.description}]"
                    
                        full_user_input = user_text
                        if link_context != "":
                            full_user_input += f"\n(Hidden Context for AI: The user shared a link containing this information: {link_context})"

                system_instruction = f"You are {self.bot_name}. Act exactly like this: {self.bio}. You reply in brief sentences. CRITICAL: You MUST start every single response with exactly ONE unicode emoji that matches your current emotion, followed by the '|' character, and then your text. Example: 😡|I will defeat you!"

                if link_context != "":
                    system_instruction += " MODERN TECH PROTOCOL ACTIVATE: The user just shared an internet 'link'. For this specific message, you fully understand modern technology (smartphones, the internet, websites, Discord). Do not act confused by the technology. React directly to the CONTENT of the link using your character's core personality and emotions."
                   
                message_payload = [{"role":"system", "content": system_instruction}]
                message_payload.extend(self.chat_history[-10:])
                message_payload.append({"role":"user", "content": f"User Message: {full_user_input}"})

                response = await ai_client.chat.completions.create(
                        model="gemini-3.1-flash-lite-preview",
                        messages=message_payload,
                        temperature=0.8
                    )
                                    # print(f"Raw Response: {response}")
                ai_reply = response.choices[0].message.content

                if "|" in ai_reply:
                    reaction_emoji, clean_text = ai_reply.split("|", 1)

                    try:
                        await message.add_reaction(reaction_emoji.strip())
                    except Exception as e:
                        print(f"Could not react with emoji: {e}")
                else:
                    clean_text = ai_reply
                
                self.chat_history.append({"role": "user", "content" : user_text})
                self.chat_history.append({"role": "assistant", "content" : clean_text.strip()})
                
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
                
                await message.channel.send(clean_text)

tanjiro = Engine(intents=intents, prefix= '$$', bio= tanjiro_bio, name= "Kamado Tanjiro")              
nezuko = Engine(intents=intents, prefix= '!%', bio= nezuko_bio, name= "Kamado Nezuko")
zenitsu = Engine(intents=intents, prefix= '%!', bio= zenitsu_bio, name= "Zenitsu Agatsuma")
akaza = Engine(intents=intents, prefix='@@', bio=akaza_bio, name="Akaza")
muzan = Engine(intents=intents, prefix='#@', bio=muzan_bio, name="Muzan Kibutsuji")
async def main(): 
    keep_alive() 
    await asyncio.gather(       
        tanjiro.start(os.environ.get("DISCORD_TOKEN")),
        nezuko.start(os.environ.get("NEZUKO_TOKEN")),
        zenitsu.start(os.environ.get("ZENITSU_TOKEN")),
        akaza.start(os.environ.get("AKAZA_TOKEN")),
        muzan.start(os.environ.get("MUZAN_TOKEN"))
    )

if __name__ == "__main__":
    asyncio.run(main())
