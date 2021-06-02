import asyncio
from string import ascii_lowercase

from discordbot.user.discord_games.minigame_dc import MinigameDisc
from discordbot.user.variables import TIMEOUT, WIN, LOSE
from discordbot.utils.emojis import ALPHABET, STOP
from minigames.hangman import Hangman, HANGMEN


class HangmanDisc(MinigameDisc):
    def __init__(self, session):
        super().__init__(session)
        self.hangman_game = Hangman()

    async def start(self):
        await self.session.message.edit(content=self.get_content())

        for i in range(len(ascii_lowercase)):
            if i < 13:
                await self.add_reaction(ALPHABET[ascii_lowercase[i]])
            if i >= 13:
                await self.add_reaction(ALPHABET[ascii_lowercase[i]], True)
        await self.add_reaction(STOP, True)

        await self.wait_for_player()

    async def wait_for_player(self):
        def check(r, u):
            return r.message.id in [self.session.message.id, self.session.message_extra.id] \
                   and r.emoji in self.emojis \
                   and u.id == self.session.message.author.id

        try:
            while True:
                reaction, user = await self.session.bot.wait_for("reaction_add", check=check, timeout=TIMEOUT)
                if reaction.emoji == STOP:
                    self.status = LOSE
                    break

                for letter, emoji in ALPHABET.items():
                    if emoji == reaction.emoji:
                        self.hangman_game.guess(letter)
                        break

                if self.hangman_game.has_won():
                    self.status = WIN
                    break
                elif self.hangman_game.has_lost():
                    self.status = LOSE
                    break
                await self.session.message.edit(content=self.get_content())

        except asyncio.TimeoutError:
            self.status = LOSE

        await self.session.message_extra.clear_reactions()
        await self.end_game()

    def get_content(self):
        word = self.hangman_game.current_word
        hangman = HANGMEN[self.hangman_game.lives]
        word_ = ""
        for c in word:
            if c == "_":
                word_ += "__ "
            else:
                word_ += f"{c} "

        content = f"```{hangman}\n\nWord: {word_}```"
        if self.status == WIN:
            content += "```You have won the game!```"
        elif self.status == LOSE:
            content += f"```You have lost the game!\nThe word was: '{''.join(self.hangman_game.word)}'```"
        return content
