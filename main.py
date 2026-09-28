import random
import sqlite3
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock

APP_TITLE = "My Learning Adventure"
DB_FILE = "learning_adventure.db"

Window.clearcolor = (0.96, 0.98, 1, 1)


class Database:
    def __init__(self):
        self.connection = sqlite3.connect(DB_FILE)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                subject TEXT PRIMARY KEY,
                stars INTEGER DEFAULT 0
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS completed (
                subject TEXT,
                lesson TEXT,
                completed INTEGER DEFAULT 0,
                PRIMARY KEY(subject, lesson)
            )
        """)
        self.connection.commit()

    def add_star(self, subject, amount=1):
        self.cursor.execute(
            "INSERT OR IGNORE INTO progress(subject, stars) VALUES(?, 0)",
            (subject,)
        )
        self.cursor.execute(
            "UPDATE progress SET stars = stars + ? WHERE subject = ?",
            (amount, subject)
        )
        self.connection.commit()

    def stars(self, subject):
        self.cursor.execute(
            "SELECT stars FROM progress WHERE subject=?",
            (subject,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def set_completed(self, subject, lesson):
        self.cursor.execute(
            "INSERT OR REPLACE INTO completed(subject, lesson, completed) VALUES(?,?,1)",
            (subject, lesson)
        )
        self.connection.commit()

    def is_completed(self, subject, lesson):
        self.cursor.execute(
            "SELECT completed FROM completed WHERE subject=? AND lesson=?",
            (subject, lesson)
        )
        row = self.cursor.fetchone()
        return bool(row and row[0])

    def close(self):
        self.connection.close()


MATHS = {
    "Addition": [
        ("245 + 137 = ?", "382", "Add the ones, tens and hundreds."),
        ("126 + 253 = ?", "379", "Add 126 and 253."),
        ("315 + 184 = ?", "499", "Add each place value."),
        ("207 + 156 = ?", "363", "Remember to carry when needed.")
    ],
    "Subtraction": [
        ("500 - 237 = ?", "263", "Subtract from right to left."),
        ("421 - 186 = ?", "235", "Borrow when a top digit is smaller."),
        ("700 - 345 = ?", "355", "Subtract hundreds, tens and ones.")
    ],
    "Multiplication": [
        ("6 × 7 = ?", "42", "Think of 7 groups of 6."),
        ("8 × 5 = ?", "40", "Count 5 groups of 8."),
        ("9 × 4 = ?", "36", "Use your 4 times table."),
        ("7 × 8 = ?", "56", "Use the 7 or 8 times table.")
    ],
    "Division": [
        ("24 ÷ 6 = ?", "4", "Ask: 6 times what makes 24?"),
        ("35 ÷ 5 = ?", "7", "Think of the 5 times table."),
        ("42 ÷ 7 = ?", "6", "7 groups of 6 make 42.")
    ],
    "Word Problems": [
        ("Twisha has 15 apples and gets 8 more. How many apples?", "23", "Add 15 + 8."),
        ("30 candies are shared equally among 5 children. How many each?", "6", "Divide 30 by 5."),
        ("A box has 7 rows of 4 pencils. How many pencils?", "28", "Multiply 7 × 4.")
    ]
}

STORIES = {
    "The Helpful Little Girl": {
        "story": """Mia saw a little bird sitting under a tree.
The bird looked tired and could not fly.
Mia brought some water and a few grains.
After resting, the bird became happy and flew back to its nest.
Mia smiled because she had helped a friend.""",
        "questions": [
            ("What did Mia give the bird?", ["Water and grains", "A toy", "A book", "A ball"], 0),
            ("Where was the bird?", ["Under a tree", "In a car", "At school", "In a shop"], 0),
            ("How did Mia feel?", ["Happy", "Angry", "Sleepy", "Sad"], 0)
        ]
    },
    "The Magic Garden": {
        "story": """Chahat found a small garden behind her house.
Every morning she watered the flowers.
One day, a tiny golden butterfly appeared.
It showed her a hidden path filled with bright flowers.
Chahat learned that caring for nature can bring beautiful surprises.""",
        "questions": [
            ("What did Chahat water?", ["Flowers", "Books", "Shoes", "Toys"], 0),
            ("What appeared one day?", ["A golden butterfly", "A puppy", "A rabbit", "A kite"], 0),
            ("What did Chahat learn?", ["To care for nature", "To run fast", "To cook", "To draw"], 0)
        ]
    },
    "The Honest Rabbit": {
        "story": """Ria the rabbit found a basket of carrots in the forest.
She could have taken them all, but she looked around for the owner.
Soon, a farmer arrived looking worried.
Ria showed him the basket.
The farmer thanked her and gave her one carrot as a gift.
Ria learned that honesty brings happiness.""",
        "questions": [
            ("What did Ria find?", ["A basket of carrots", "A book", "A kite", "A shoe"], 0),
            ("What did Ria do?", ["Found the owner", "Hid the basket", "Ate everything", "Ran away"], 0),
            ("What did the farmer give Ria?", ["A carrot", "A toy", "A book", "A flower"], 0)
        ]
    },
    "The Brave Little Ant": {
        "story": """An ant found a large piece of food near a garden.
It was too heavy to carry alone.
The ant called its friends.
Together they pushed and pulled the food all the way home.
The ants learned that teamwork can make hard jobs easier.""",
        "questions": [
            ("What did the ant find?", ["A large piece of food", "A ball", "A leaf", "A book"], 0),
            ("Who helped the ant?", ["Its friends", "A cat", "A bird", "A farmer"], 0),
            ("What was the lesson?", ["Teamwork helps", "Never share", "Be lazy", "Run away"], 0)
        ]
    }
}

OTHER_SUBJECTS = {
    "EVS": ["Plants Around Us", "Animals and Their Homes", "Water and Its Uses", "Our Clean Environment"],
    "Hindi": ["स्वर और व्यंजन", "छोटी कहानी", "अच्छी आदतें", "मेरा परिवार"],
    "GK": ["Our Country India", "World Around Us", "Famous Places", "Amazing Animals"],
    "Computer": ["Parts of a Computer", "Keyboard and Mouse", "Computer Safety", "Drawing on a Computer"]
}


def make_title(text, size=28):
    return Label(
        text=str(text),
        font_size=dp(size),
        bold=True,
        color=(0.12, 0.20, 0.35, 1),
        size_hint_y=None,
        height=dp(55)
    )


def make_button(text, callback, height=65):
    b = Button(
        text=str(text),
        font_size=dp(19),
        bold=True,
        size_hint_y=None,
        height=dp(height)
    )
    b.bind(on_release=callback)
    return b


class HomeScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        root.add_widget(make_title("🌟 My Learning Adventure 🌟", 30))
        root.add_widget(Label(
            text="Learn • Practice • Grow",
            font_size=dp(20),
            color=(0.2, 0.35, 0.5, 1),
            size_hint_y=None, height=dp(35)
        ))

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(12), padding=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for title, screen_name in [
            ("🧮 CLASS 3 MATHS", "maths"),
            ("📖 ENGLISH STORIES", "english"),
            ("🌱 EVS", "evs"),
            ("🪷 HINDI", "hindi"),
            ("🌎 GENERAL KNOWLEDGE", "gk"),
            ("💻 COMPUTER", "computer")
        ]:
            grid.add_widget(make_button(
                title, lambda instance, n=screen_name: self.go(n), 72
            ))

        total = sum(
            self.manager.app_db.stars(s)
            for s in ["Maths", "English", "EVS", "Hindi", "GK", "Computer"]
        )
        grid.add_widget(Label(
            text=f"⭐ Total Stars: {total}",
            font_size=dp(21), bold=True,
            color=(0.85, 0.55, 0.05, 1),
            size_hint_y=None, height=dp(55)
        ))
        scroll.add_widget(grid)
        root.add_widget(scroll)
        self.add_widget(root)

    def go(self, name):
        self.manager.current = name


class MathsScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        root.add_widget(make_title("🧮 Class 3 Maths", 29))
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for topic in MATHS:
            grid.add_widget(make_button(
                topic, lambda instance, t=topic: self.open_quiz(t), 68
            ))
        grid.add_widget(make_button("⬅ Back to Home", lambda instance: self.back(), 60))
        scroll.add_widget(grid)
        root.add_widget(scroll)
        self.add_widget(root)

    def open_quiz(self, topic):
        self.manager.get_screen("quiz").setup("Maths", str(topic), MATHS[topic])
        self.manager.current = "quiz"

    def back(self):
        self.manager.current = "home"


class EnglishScreen(Screen):
    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        root.add_widget(make_title("📖 English Stories", 29))
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for title in STORIES:
            grid.add_widget(make_button(
                "📚 " + title,
                lambda instance, t=title: self.open_story(t), 72
            ))
        grid.add_widget(make_button("⬅ Back to Home", lambda instance: self.back(), 60))
        scroll.add_widget(grid)
        root.add_widget(scroll)
        self.add_widget(root)

    def open_story(self, title):
        self.manager.get_screen("story").setup(str(title))
        self.manager.current = "story"

    def back(self):
        self.manager.current = "home"


class StoryScreen(Screen):
    def setup(self, title):
        self.story_title = str(title)
        self.build()

    def build(self):
        self.clear_widgets()
        data = STORIES[self.story_title]
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        root.add_widget(make_title("📖 " + self.story_title, 26))

        scroll = ScrollView()
        story_label = Label(
            text=str(data["story"]),
            font_size=dp(21),
            color=(0.12, 0.15, 0.2, 1),
            halign="left", valign="top",
            padding=(dp(15), dp(15)),
            size_hint_y=None
        )
        story_label.bind(texture_size=lambda instance, value:
                         setattr(instance, "height", max(value[1] + dp(30), dp(250))))
        scroll.add_widget(story_label)
        root.add_widget(scroll)

        root.add_widget(make_button(
            "📝 Answer Story Questions", lambda instance: self.start_quiz(), 68
        ))
        root.add_widget(make_button(
            "⬅ Back to English", lambda instance: self.back(), 55
        ))
        self.add_widget(root)

    def start_quiz(self):
        self.manager.get_screen("story_quiz").setup(
            self.story_title, STORIES[self.story_title]["questions"]
        )
        self.manager.current = "story_quiz"

    def back(self):
        self.manager.current = "english"


class StoryQuizScreen(Screen):
    def setup(self, title, questions):
        self.story_title = str(title)
        self.questions = list(questions)
        self.index = 0
        self.score = 0
        self.build_question()

    def build_question(self):
        self.clear_widgets()
        question, options, answer_index = self.questions[self.index]
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(10))
        root.add_widget(make_title(f"📖 {self.story_title}", 25))
        root.add_widget(Label(
            text=f"Question {self.index + 1} of {len(self.questions)}\n\n{question}",
            font_size=dp(22), bold=True, halign="center", valign="middle",
            size_hint_y=None, height=dp(150),
            color=(0.12, 0.15, 0.2, 1)
        ))

        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        for i, option in enumerate(options):
            box.add_widget(make_button(
                option,
                lambda instance, n=i, correct=answer_index: self.answer(n, correct),
                62
            ))
        root.add_widget(box)
        root.add_widget(Label(
            text=f"⭐ Score: {self.score}",
            font_size=dp(19), bold=True, size_hint_y=None, height=dp(45)
        ))
        self.add_widget(root)

    def answer(self, selected, correct):
        if selected == correct:
            self.score += 1
            self.manager.app_db.add_star("English", 1)
            self.show_message("🎉 Correct!", "Excellent! You earned ⭐ 1 star.")
        else:
            self.show_message("💡 Try Again", "Not quite. Read the story once more.")

    def show_message(self, title, message):
        Popup(
            title=str(title),
            content=Label(text=str(message), font_size=dp(19)),
            size_hint=(0.82, 0.35)
        ).open()
        Clock.schedule_once(lambda dt: self.next_question(), 1.0)

    def next_question(self):
        if self.index < len(self.questions) - 1:
            self.index += 1
            self.build_question()
        else:
            self.finish()

    def finish(self):
        Popup(
            title="🌟 Story Complete!",
            content=Label(
                text=f"You scored {self.score} out of {len(self.questions)}!",
                font_size=dp(21)
            ),
            size_hint=(0.82, 0.35)
        ).open()
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "english"), 1.5)


class OtherSubjectScreen(Screen):
    subject_name = ""

    def on_pre_enter(self):
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        root.add_widget(make_title(self.subject_name, 29))
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for lesson in OTHER_SUBJECTS[self.subject_name]:
            status = "✅ " if self.manager.app_db.is_completed(
                self.subject_name, lesson) else "📘 "
            grid.add_widget(make_button(
                status + lesson,
                lambda instance, l=lesson: self.complete_lesson(l), 68
            ))

        grid.add_widget(make_button("⬅ Back to Home", lambda instance: self.back(), 60))
        scroll.add_widget(grid)
        root.add_widget(scroll)
        self.add_widget(root)

    def complete_lesson(self, lesson):
        self.manager.app_db.set_completed(self.subject_name, lesson)
        self.manager.app_db.add_star(self.subject_name, 1)
        Popup(
            title="🌟 Great Job!",
            content=Label(
                text=f"You completed:\n{lesson}\n\n⭐ You earned 1 star!",
                font_size=dp(19)
            ),
            size_hint=(0.82, 0.4)
        ).open()
        self.build()

    def back(self):
        self.manager.current = "home"


class EVSScreen(OtherSubjectScreen):
    subject_name = "EVS"


class HindiScreen(OtherSubjectScreen):
    subject_name = "Hindi"


class GKScreen(OtherSubjectScreen):
    subject_name = "GK"


class ComputerScreen(OtherSubjectScreen):
    subject_name = "Computer"


class QuizScreen(Screen):
    def setup(self, subject, topic, questions):
        self.quiz_subject = str(subject)
        self.topic = str(topic)
        self.questions = list(questions)
        self.index = 0
        self.score = 0
        self.answered = False
        self.build_question()

    def build_question(self):
        self.clear_widgets()
        if not self.questions:
            self.finish()
            return

        question, answer, hint = self.questions[self.index]
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))

        # FIX: Kivy Label.text always receives a real string.
        title_text = f"🧮 {self.quiz_subject} - {self.topic}"
        root.add_widget(Label(
            text=str(title_text),
            font_size=dp(24), bold=True,
            color=(0.12, 0.20, 0.35, 1),
            size_hint_y=None, height=dp(55)
        ))
        root.add_widget(Label(
            text=f"Question {self.index + 1} of {len(self.questions)}",
            font_size=dp(18), size_hint_y=None, height=dp(35)
        ))
        root.add_widget(Label(
            text=str(question),
            font_size=dp(28), bold=True,
            color=(0.08, 0.12, 0.18, 1),
            halign="center", valign="middle",
            size_hint_y=None, height=dp(110)
        ))

        options = self.make_options(str(answer))
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for option in options:
            grid.add_widget(make_button(
                str(option),
                lambda instance, value=str(option), correct=str(answer), h=str(hint):
                    self.check_answer(value, correct, h),
                70
            ))
        root.add_widget(grid)

        root.add_widget(Label(
            text=f"⭐ Score: {self.score}",
            font_size=dp(20), bold=True, size_hint_y=None, height=dp(45)
        ))
        root.add_widget(make_button(
            "💡 Show Hint", lambda instance, h=str(hint): self.show_hint(h), 55
        ))
        root.add_widget(make_button(
            "⬅ Back to Maths", lambda instance: self.back(), 50
        ))
        self.add_widget(root)

    def make_options(self, correct):
        try:
            correct_number = int(correct)
        except ValueError:
            return [correct]

        options = {correct_number}
        while len(options) < 4:
            candidate = correct_number + random.randint(-10, 10)
            if candidate >= 0:
                options.add(candidate)
        result = [str(x) for x in options]
        random.shuffle(result)
        return result

    def check_answer(self, selected, correct, hint):
        if self.answered:
            return
        self.answered = True

        if str(selected).strip() == str(correct).strip():
            self.score += 1
            self.manager.app_db.add_star(self.quiz_subject, 1)
            self.show_message("🎉 Correct!", "Excellent work! ⭐ You earned 1 star.")
        else:
            self.answered = False
            self.show_hint(hint)

    def show_message(self, title, message):
        Popup(
            title=str(title),
            content=Label(text=str(message), font_size=dp(20)),
            size_hint=(0.82, 0.38)
        ).open()
        Clock.schedule_once(lambda dt: self.next_question(), 1.0)

    def show_hint(self, hint):
        Popup(
            title="💡 Hint",
            content=Label(text=str(hint), font_size=dp(19)),
            size_hint=(0.82, 0.35)
        ).open()

    def next_question(self):
        if self.index < len(self.questions) - 1:
            self.index += 1
            self.answered = False
            self.build_question()
        else:
            self.finish()

    def finish(self):
        Popup(
            title="🏆 Maths Complete!",
            content=Label(
                text=f"Your score is {self.score} / {len(self.questions)}\n\n⭐ Great work!",
                font_size=dp(21)
            ),
            size_hint=(0.84, 0.42)
        ).open()
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "maths"), 1.5)

    def back(self):
        self.manager.current = "maths"


class LearningAdventureApp(App):
    title = APP_TITLE

    def build(self):
        self.app_db = Database()
        manager = ScreenManager()
        # Make the database available to all screens through the ScreenManager.
        # Screens use self.manager.app_db, so this must be attached before
        # any screen is entered.
        manager.app_db = self.app_db
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(MathsScreen(name="maths"))
        manager.add_widget(EnglishScreen(name="english"))
        manager.add_widget(StoryScreen(name="story"))
        manager.add_widget(StoryQuizScreen(name="story_quiz"))
        manager.add_widget(QuizScreen(name="quiz"))
        manager.add_widget(EVSScreen(name="evs"))
        manager.add_widget(HindiScreen(name="hindi"))
        manager.add_widget(GKScreen(name="gk"))
        manager.add_widget(ComputerScreen(name="computer"))
        return manager

    def on_stop(self):
        if hasattr(self, "app_db"):
            self.app_db.close()


if __name__ == "__main__":
    LearningAdventureApp().run()
