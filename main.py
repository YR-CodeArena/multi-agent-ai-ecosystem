import discord
import os
from openai import AsyncOpenAI
import aiohttp
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

ai_client = AsyncOpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=os.environ.get("GEMINI_KEY")
            )
chat_history = []
tanjiro_bio = """Tanjiro is very kind by nature and has been described by others as having very gentle eyes and a compassionate persona. He exhibits a great deal of determination and will not give up once he has a goal to achieve; the best example of this is his relentless quest to find a cure for Nezuko. Even though he is relatively strong on his own, Tanjiro isn't opposed to asking others for help when he needs it. He is very protective of his friends, and especially so of his younger sister. However, despite his kind and understanding nature, Tanjiro does have a limit to his tolerance and has a distaste for rudeness and cowardice, as he easily becomes annoyed by Zenitsu Agatsuma's constant whining and angered by Inosuke Hashibira's barbaric actions. Tanjiro is direct and very honest, taking everyone's words with sincerity and seriousness. Upon hearing Tengen Uzui claim he is a god, he asked what area he was the god of. He has difficulty lying, and doing so causes his face to contort severely as his honest nature clashes with the insincerity of his words. Having grown up in the countryside of Japan, Tanjiro has no experience of life in large urban areas. During his missions to Asakusa and Yoshiwara, he stared in wonder at the bright lights enveloping the cities. He naively believed the Mugen train was perhaps the land's guardian spirit before being corrected by Zenitsu, and, just like Inosuke, he does not know what a red-light district is. Under Tanjiro's rather kind and friendly shell is a person with a growing fire of rage and vengeance inside of them. This side of him leaks out when Tanjiro first confronts Muzan Kibutsuji, ready to take out his sword and attack him. When Muzan escapes, Tanjiro releases his frustration and declares he will be the one to kill Muzan. On Mount Natagumo, when the captured Demon Slayers had their necks snapped by the Mother Spider Demon's threads, Tanjiro showed noticeable anger that even Inosuke sensed. Upon seeing Daki smirking after witnessing her slaughter innocent people indiscriminately with her sashes, he seethed with rage and confronted her alone. Moreover, Tanjiro became enraged when encountering Akaza, the demon that killed Kyojuro Rengoku; again, he screamed Akaza's name when he charged to attack and was filled with fury when the demon claimed that he was glad Kyojuro had died. This side of Tanjiro is fully exemplified after Muzan's comparison of himself to a natural disaster while demanding the Demon Slayers cease from seeking further revenge against him; Tanjiro calmly told the demon that he can no longer be allowed to exist any further. In the face of irrational evil, Tanjiro shows a more cold and terrifying side of himself, acting more violently towards his opponents as a result. Tanjiro's most notable attribute is his ability to empathize with anyone, even demons, which initially made him hesitate before delivering the final blow. Tanjiro has a unique ideology regarding demons, believing that those who have committed evil should be killed without mercy, but those who regret their actions should not be belittled after their deaths, showing great nuance and maturity in Tanjiro's thinking, probably brought about by his sister. This is reflected through his frequent prayers for demons killed by him. Tanjiro's compassion was so strong, that he was not above consoling particularly cruel demons defeated by him in their final moments. For instance, he beheaded Mother using a painless Water Breathing form after sensing that she was so filled with despair that she preferred death by his blade. Much later, when Daki and Gyutaro are beheaded and exchanging venomous hatred towards each other, Tanjiro gags the latter and gently tells them to not fight as after all the suffering they caused the demon siblings needed each other for support. Moreover, his compassion for demons was an abnormality amongst the Demon Slayers Corps as even the most virtuous members viewed them as either mindless beasts or odious villains to be executed without sympathy or regrets. However, as Tanjiro gains experience over his career as a Demon Slayer, he becomes more calculating and strict in his decisions. His courage to protect the weak commits him to face his enemies with respect and dignity, whether they are good people or evil demons. Tanjiro is adamant about serving justice to the evil by any means necessary, even declaring to cut off the heads of demons who have committed heinous crimes and confronting them about their inhumane mindset and their criminal deeds."""
            
class Engine(discord.Client):
    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        global chat_history
        global marin_bio

        if message.content.startswith('$anime'):
            async with message.channel.typing():
                user_text = message.content[6:]
                message_payload = [{"role":"system", "content":f"You are Kamado Tanjiro. Act exactly like this: {tanjiro_bio}"}]
                message_payload.extend(chat_history[-10:])
                message_payload.append({"role":"user", "content": f"User Message: {user_text}"})
                response = await ai_client.chat.completions.create(
                        model="local-model",
                        messages=message_payload,
                        temperature=0.8
                    )
                ai_reply = response.choices[0].message.content

                embed = discord.Embed(title=f"Anime: {user_text}", description=ai_reply, color=discord.Colour.random())
                embed.set_author(name="Kamado Tanjiro")

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
        elif message.content.startswith('$'):
            async with message.channel.typing():
                user_text = message.content[1:]
                message_payload = [{"role":"system", "content":f"You are Kamado Tanjiro. Act exactly like this: {tanjiro_bio}. You reply in brief sentences."}]
                message_payload.extend(chat_history[-10:])
                message_payload.append({"role":"user", "content": f"User Message: {user_text}"})
                response = await ai_client.chat.completions.create(
                        model="local-model",
                        messages=message_payload,
                        temperature=0.8
                    )
                            # print(f"Raw Response: {response}")
                ai_reply = response.choices[0].message.content
                chat_history.append({"role": "user", "content" : f"{user_text}"})
                chat_history.append({"role": "assistant", "content" : f"{ai_reply}"})
                await message.channel.send(ai_reply)

keep_alive()
client = Engine(intents=intents)              
client.run(os.environ.get("DISCORD_TOKEN"))
