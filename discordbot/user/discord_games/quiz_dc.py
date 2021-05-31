import asyncio
import html
import random
from string import ascii_lowercase, ascii_uppercase

from discordbot.user.discord_games.minigame_dc import MinigameDisc
from discordbot.user.variables import TIMEOUT, WIN, LOSE
from discordbot.utils.emojis import ALPHABET, STOP, NUMBERS
from minigames.lexicon import Lexicon


class QuizDisc(MinigameDisc):
    def __init__(self, session):
        super().__init__(session)
        self.category = None
        self.question = None
        self.correct_answer = None
        self.answers = None
        self.user_answer = -1
        self.selecting_category = True
        self.categories = ["General Knowledge", "Sports", "Films", "Music", "Video Games"]

    async def start(self):
        await self.session.message.edit(content=self.get_content())

        for i in range(1, len(self.categories)+1):
            await self.add_reaction(NUMBERS[i])
        await self.add_reaction(STOP)

        def check(r, u):
            return r.message.id == self.session.message.id \
                   and r.emoji in self.emojis \
                   and u.id == self.session.context.author.id

        try:
            reaction, user = await self.session.bot.wait_for("reaction_add", check=check, timeout=TIMEOUT)
            if reaction.emoji == STOP:
                await self.end_game()
                return
            for n, e in NUMBERS.items():
                if e == reaction.emoji:
                    self.category = self.categories[n-1]
                    break
        except asyncio.TimeoutError:
            await self.end_game()
            return
        await self.clear_reactions()

        self.get_question()
        await self.session.message.edit(content=self.get_content())
        for i in range(len(self.answers)):
            await self.add_reaction(ALPHABET[ascii_lowercase[i]])
        await self.add_reaction(STOP)

        await self.wait_for_player()

    async def wait_for_player(self):
        def check(r, u):
            return r.message.id == self.session.message.id \
                   and u.id != self.session.message.author.id \
                   and u.id == self.session.context.author.id \
                   and r.emoji in self.emojis

        try:
            reaction, user = await self.session.bot.wait_for("reaction_add", check=check, timeout=TIMEOUT)
            if reaction.emoji == STOP:
                self.status = LOSE
            else:
                for c, e in ALPHABET.items():
                    if e == reaction.emoji:
                        self.user_answer = ascii_lowercase.index(c)
                        if self.user_answer == self.correct_answer:
                            self.status = WIN
                        else:
                            self.status = LOSE
                        break
        except asyncio.TimeoutError:
            self.status = LOSE

        await self.session.message.edit(content=self.get_content())
        await self.end_game()

    def get_question(self):
        self.selecting_category = False
        questions = Lexicon.QUESTIONS[self.category]
        random.shuffle(questions)
        quiz = questions[random.randint(0, len(Lexicon.QUESTIONS) - 1)]
        self.question = quiz['question']
        self.answers = list(set(quiz['incorrect_answers']))
        self.correct_answer = random.randint(0, len(self.answers))
        self.answers.insert(self.correct_answer, quiz['correct_answer'])

    def get_content(self):
        content = "```"
        if self.selecting_category:
            content += "Categories\n"
            for i in range(len(self.categories)):
                content += f"{NUMBERS[i+1]}   {self.categories[i]}\n"
        else:
            content += f"{self.category}\nQuestion:\n" \
                       f"{html.unescape(self.question)}\n\n"
            for i in range(len(self.answers)):
                if i == self.user_answer:
                    content += f"{ascii_uppercase[i]}: {html.unescape(self.answers[i])}   <- YOUR ANSWER\n"
                else:
                    content += f"{ascii_uppercase[i]}: {html.unescape(self.answers[i])}\n"
            if self.status == WIN:
                content += "You answered correct!\n"
            elif self.status == LOSE:
                content += f"Wrong! The correct answer was: {html.unescape(self.answers[self.correct_answer])}\n"
        content += "```"
        return content