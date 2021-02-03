""" The intro quest """

from typing import Optional
import re
from datetime import datetime
from semver import VersionInfo  # type:  ignore

from character import character_garry, character_zelma
from ..quest import Quest, Difficulty, QuestBaseModel
from ..stage import (
    CreateIssueStage,
    CreateIssueConversationStage,
    CheckIssueCommentReply,
    FinalStage,
)


class IntroQuest(Quest):
    class QuestDataModel(QuestBaseModel):
        issue_id: Optional[str] = None
        last_comment: Optional[datetime] = None

    version = VersionInfo.parse("0.1.0")
    difficulty = Difficulty.BEGINNER
    description = "The intro quest"

    class Start(CreateIssueStage):
        children = ["CheckNumber1"]
        character = character_garry
        issue_id_variable = "issue_id"
        issue_title = "Welcome, can you give me a hand?"
        issue_body = """\
            Hello therre! Hmm...I hear you're the new arrival. Welcome welcome, it's so nice to see new faces around herre. Hmm...You know, I've lived around these parts for so long, but it's never borring with all the new people coming through. I hope you have a wonderful time, in fact I'm sure of it.

            Hmm...Oh! Beforre you rush off, can you give me hand with something?

            My memory's not what it used to be, I'm off to the shops but I've forgotten how many eggs I needed to get for tonight's meal! Hmm...Could you go through my files and find the numberr for me?

            My journal is [over here](https://github.com/LGTM-garry/garrys-journal), please look in the `food_stuff` folder, there should be a file called `dinner_plans.txt` where I keep notes for what to make for dinner. Can you please take a look in there and tell me know how many eggs I need? Just leave me a comment below with the numberr, thank you!
            """

    class CheckNumber1(CheckIssueCommentReply):
        children = ["ReplyGroup1"]
        character = character_garry
        regex_pattern = re.compile(
            r"(?<!\d)42(?!\d)"
        )  # exactly 42, no digits either side
        issue_id_variable = "issue_id"

        incorrect_responses = [
            "Hmm... that doesn't seem right",
            "No, it's not that",
            "Hmm... are you sure? Try again",
            "That doesn't seem right",
            "Could you check again? I don't think it's that",
        ]

    class ReplyGroup1(CreateIssueConversationStage):
        children = ["CheckNumber2"]
        character = character_garry
        issue_id_variable = "issue_id"
        comment_datetime_variable = "last_comment"
        character_comment_pairs = [
            (
                character_garry,
                """\
                Hmm...Oh... that rings a bell, but it does seem like an awful lot of eggs to eat. I can only manage a few usually, why did I plan to eat so many?

                I wonderr...
                """,
            ),
            (character_zelma, "Garry!"),
            (character_garry, "Uh oh, my wife is herre"),
            (
                character_zelma,
                """\
                What do you mean "Uh oh"? Garry you nincompoop, you must have messed up the numbers when you edited the file. You've been talking about it all day, trying to figure out how many eggs you're going to eat.

                I'm sorry you had to speak to this old fool of a husband of mine on your first visit here. Let's get his plans sorted out so you can be on your way.

                Now, I'm sure Garry must have messed up an edit somehow, can you take a look at the file's edit **history**? When you view a file's history like this, you are looking at past edits to the file, so you can look at old versions of files and see what's changed.

                Can you take a look now, and figure out how many eggs Garry originally intended to eat for dinner?
                """,
            ),
        ]

    class CheckNumber2(CheckIssueCommentReply):
        children = ["ReplyGroup2"]
        character = character_zelma
        regex_pattern = re.compile(
            r"(?<!\d)2(?!\d)"
        )  # exactly 42, no digits either side
        issue_id_variable = "issue_id"
        comment_datetime_variable = "last_comment"

        incorrect_responses = [
            "No, it wasn't that",
            "Try again, that's not it",
            "Oh, we would have known if it was that, try again",
            "It must be something different, try again",
            "Can't have been that, please check again",
        ]

    class ReplyGroup2(CreateIssueConversationStage):
        children = ["End"]
        issue_id_variable = "issue_id"
        character_comment_pairs = [
            (
                character_garry,
                """\
                Hmm... Oh yes! I wanted TWO eggs at first, and then I felt hungry and decided to have FOUR.
                """,
            ),
            (
                character_zelma,
                """\
                And then when you edited your file, you messed it up. Thankfully we've had the help of this kind soul, otherwise you'd be up all night eating those eggs.
                """,
            ),
            (character_garry, "Have mercy dearr!"),
            (
                character_zelma,
                """\
                Yes yes, dear.
                
                And thank YOU, I'm sure we'll bump into each other again sometime soon, perhaps drop by for some eggs, we're always only one typo away from having too many
                """,
            ),
        ]

    class End(FinalStage):
        pass
