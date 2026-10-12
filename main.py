
import os
import json
from datetime import date
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView

BG = (0.025, 0.035, 0.055, 1)
PANEL = (0.075, 0.09, 0.13, 1)
BLUE = (0.02, 0.45, 0.9, 1)
CYAN = (0.1, 0.75, 0.95, 1)
WHITE = (0.9, 0.93, 0.98, 1)


class Nexus(App):
    def build(self):
        Window.clearcolor = BG
        self.data_file = os.path.join(
            self.user_data_dir, "nexus_data.json"
        )
        self.data = {"tasks": [], "notes": ""}
        self.load_data()
        self.page = "tasks"

        self.root_box = BoxLayout(
            orientation="vertical", padding=dp(16), spacing=dp(10)
        )
        self.show_page()
        return self.root_box

    def load_data(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (OSError, ValueError):
            pass

    def save_data(self):
        os.makedirs(self.user_data_dir, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def label(self, text, size=16, color=WHITE):
        return Label(
            text=text, font_size=sp(size), color=color,
            size_hint_y=None, height=dp(38)
        )

    def btn(self, text, callback, color=BLUE):
        b = Button(
            text=text, size_hint_y=None, height=dp(48),
            background_normal="", background_color=color,
            color=WHITE, font_size=16
        )
        b.bind(on_release=callback)
        return b

    def show_page(self):
        self.root_box.clear_widgets()

        self.root_box.add_widget(
            self.label("N E X U S", 29, CYAN)
        )
        self.root_box.add_widget(
            self.label("DAILY TASK MANAGER", 13)
        )

        nav = GridLayout(
            cols=2, spacing=dp(8),
            size_hint_y=None, height=dp(48)
        )
        nav.add_widget(self.btn(
            "TASKS", lambda *_: self.change_page("tasks")
        ))
        nav.add_widget(self.btn(
            "NOTES", lambda *_: self.change_page("notes"),
            PANEL
        ))
        self.root_box.add_widget(nav)

        if self.page == "tasks":
            self.show_tasks()
        else:
            self.show_notes()

    def change_page(self, page):
        self.page = page
        self.show_page()

    def show_tasks(self):
        today = date.today().isoformat()
        todays = [t for t in self.data["tasks"]
                  if t.get("date") == today]
        done = sum(1 for t in todays if t.get("done"))
        percent = int(100 * done / len(todays)) if todays else 0

        self.root_box.add_widget(
            self.label(f"TODAY'S PROGRESS  {percent}%", 20, CYAN)
        )
        self.root_box.add_widget(
            self.label(f"{done} completed out of {len(todays)} tasks")
        )

        self.task_input = TextInput(
            hint_text="Write your task...",
            multiline=False, size_hint_y=None, height=dp(48),
            background_color=PANEL, foreground_color=WHITE,
            cursor_color=CYAN
        )
        self.root_box.add_widget(self.task_input)

        self.category = Spinner(
            text="Personal",
            values=("Personal", "Study", "Work", "Health", "Other"),
            size_hint_y=None, height=dp(44),
            background_normal="", background_color=PANEL,
            color=WHITE
        )
        self.root_box.add_widget(self.category)

        fields = GridLayout(
            cols=2, spacing=dp(8),
            size_hint_y=None, height=dp(46)
        )
        self.date_input = TextInput(
            text=today, hint_text="YYYY-MM-DD", multiline=False,
            background_color=PANEL, foreground_color=WHITE
        )
        self.time_input = TextInput(
            text="18:00", hint_text="HH:MM", multiline=False,
            background_color=PANEL, foreground_color=WHITE
        )
        fields.add_widget(self.date_input)
        fields.add_widget(self.time_input)
        self.root_box.add_widget(fields)

        self.root_box.add_widget(self.btn(
            "+ ADD TASK", self.add_task
        ))

        scroll = ScrollView()
        items = BoxLayout(
            orientation="vertical", spacing=dp(8),
            size_hint_y=None
        )
        items.bind(minimum_height=items.setter("height"))

        for index, task in enumerate(self.data["tasks"]):
            row = BoxLayout(
                size_hint_y=None, height=dp(76), spacing=dp(5)
            )
            status = "☑" if task.get("done") else "☐"
            info = (
                f"{status} {task['title']}\n"
                f"{task.get('category', 'Personal')} | "
                f"{task.get('date', '')} {task.get('time', '')}"
            )
            text = Button(
                text=info, halign="left", valign="middle",
                background_normal="", background_color=PANEL,
                color=CYAN if task.get("done") else WHITE
            )
            text.bind(size=lambda w, s: setattr(w, "text_size", s))
            text.bind(on_release=lambda _, i=index: self.toggle_task(i))
            row.add_widget(text)
            row.add_widget(self.btn(
                "X", lambda _, i=index: self.delete_task(i),
                (0.65, 0.08, 0.18, 1)
            ))
            items.add_widget(row)

        scroll.add_widget(items)
        self.root_box.add_widget(scroll)

    def add_task(self, *_):
        title = self.task_input.text.strip()
        if not title:
            self.task_input.hint_text = "Enter a task first!"
            return

        task_date = self.date_input.text.strip()
        task_time = self.time_input.text.strip()

        try:
            date.fromisoformat(task_date)
            hour, minute = map(int, task_time.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError()
        except ValueError:
            self.task_input.text = title
            self.date_input.text = date.today().isoformat()
            self.time_input.text = "18:00"
            return

        self.data["tasks"].append({
            "title": title,
            "category": self.category.text,
            "date": task_date,
            "time": task_time,
            "done": False
        })
        self.save_data()
        self.show_page()

    def toggle_task(self, index):
        self.data["tasks"][index]["done"] = not (
            self.data["tasks"][index].get("done", False)
        )
        self.save_data()
        self.show_page()

    def delete_task(self, index):
        del self.data["tasks"][index]
        self.save_data()
        self.show_page()

    def show_notes(self):
        self.root_box.add_widget(self.label("MY NOTES", 22, CYAN))
        self.notes_input = TextInput(
            text=self.data.get("notes", ""),
            hint_text="Write your notes here...",
            multiline=True, background_color=PANEL,
            foreground_color=WHITE, cursor_color=CYAN
        )
        self.root_box.add_widget(self.notes_input)
        self.root_box.add_widget(self.btn(
            "SAVE NOTES", self.save_notes
        ))

    def save_notes(self, *_):
        self.data["notes"] = self.notes_input.text
        self.save_data()
        self.root_box.clear_widgets()
        self.root_box.add_widget(self.label("NOTES SAVED", 22, CYAN))
        self.root_box.add_widget(self.btn(
            "BACK TO NOTES", lambda *_: self.show_page()
        ))
        Clock.schedule_once(lambda _: self.show_page(), 1.2)


def sp(value):
    return dp(value)


if __name__ == "__main__":
    Nexus().run()
