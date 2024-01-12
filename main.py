import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.core.audio import SoundLoader
from kivy.utils import get_color_from_hex
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from random import shuffle

class HardGameScreen(Screen):
    def __init__(self, **kwargs):
        super(HardGameScreen, self).__init__(**kwargs)
        self.images = ['assets/n.png', 'assets/o.png', 'assets/p.png', 'assets/q.png', 'assets/r.png', 'assets/s.png', 'assets/t.png', 'assets/u.png', 'assets/v.png', 'assets/w.png'] * 2
        shuffle(self.images)
        self.selected_images = []
        self.matched_images = []
        self.num_attempts = 0
        self.max_attempts = 12
        self.remaining_time = 60  # 2 minutes in seconds
        self.timer_event = None

        layout = self.ids.layout

        layout = BoxLayout(orientation='vertical', spacing=10)

        self.button_click_sound = SoundLoader.load('assets\mixkit-arcade-game-jump-coin-216.wav')
        self.button_click_sound.volume = 0 if MemoryGameApp.game_sound_state == 'On' else 1

        # Add a label to display remaining time
        self.time_label = Label(text=str(self.remaining_time), font_size=24, halign='right', size_hint=(1, 0.05), color=(0, 0, 0, 1), bold=True)
        layout.add_widget(self.time_label)

        # Add a label to display the number of attempts
        self.attempts_label = Label(text=f"Attempts: {self.num_attempts}/{self.max_attempts}", font_size=18, halign='left', size_hint=(1, 0.05), color=(1, 0, 0, 1), bold=True)
        layout.add_widget(self.attempts_label)

        self.grid = GridLayout(cols=4, spacing=10)
        layout.add_widget(self.grid)
        self.can_click = True

        for image in self.images:
            btn = Button(background_normal='', background_color=(1, 1, 1, 1))  # Set the background color to white (R, G, B, A)
            btn.bind(on_release=self.on_image_click)
            self.grid.add_widget(btn)

        back_to_menu_button = Button(
            text="Back to Main Menu",
            on_release=self.switch_to_menu,
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.5},
            background_normal='', 
            background_color=(1, 0.43, 0.85, 0.9)
        )
        layout.add_widget(back_to_menu_button)

        self.add_widget(layout)

    def start_timer(self):
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.remaining_time -= 1
        self.time_label.text = str(self.remaining_time)

        if self.remaining_time <= 0:
            self.game_over("Time is up! You ran out of time.")
            self.stop_timer()

    def stop_timer(self):
        if self.timer_event:
            self.timer_event.cancel()

    def on_image_click(self, button):
        if self.button_click_sound:
            self.button_click_sound.play()

        if not self.can_click or button in (image[0] for image in self.selected_images):
            return
    
        image_path = self.images[self.grid.children.index(button)]
        if image_path in self.matched_images:
            return
    
        if len(self.selected_images) < 2:
            button.background_normal = image_path
            self.selected_images.append((button, image_path))
    
        if len(self.selected_images) == 2:
            self.can_click = False  # Disable further clicks until the match check is complete
            Clock.schedule_once(self.check_match, 1)


    def check_match(self, dt):
        if self.selected_images[0][1] == self.selected_images[1][1]:
            self.matched_images.extend([self.selected_images[0][1], self.selected_images[1][1]])
            self.selected_images[0][0].disabled = True
            self.selected_images[1][0].disabled = True
            self.selected_images = []
            if len(self.matched_images) == len(self.images):
                self.game_over("Congratulations! You won!")
        else:
            self.selected_images[0][0].background_normal = ''
            self.selected_images[1][0].background_normal = ''
            self.selected_images = []
            self.num_attempts += 1
            if self.num_attempts >= self.max_attempts:
                self.game_over("Game over! You ran out of attempts.")

        self.can_click = True
        self.update_attempts_label()

    def update_attempts_label(self):
        self.attempts_label.text = f"Attempts: {self.num_attempts}/{self.max_attempts}"

    def game_over(self, message):
        self.stop_timer()
        self.show_game_over_popup(message)

    def show_game_over_popup(self, message):
        popup = Popup(title="Game Over",
                      content=BoxLayout(orientation='vertical', spacing=10, padding=10),
                      size_hint=(None, None), size=(400, 200),
                      auto_dismiss=False)  # Set auto_dismiss to False

        # Add the label to display the message
        popup.content.add_widget(Label(text=message, size_hint=(1, 0.8)))

        play_again_button = Button(text="Play Again", on_release=lambda btn: self.reset_game(btn, popup))
        popup.content.add_widget(play_again_button)

        popup.open()

    def switch_to_menu(self, instance):
        # sound_manager = SoundManager
        self.manager.current = 'main_menu'
        

    def reset_game(self, button, popup):
        popup.dismiss()
        self.manager.current = 'easy'
        self.manager.get_screen('easy').reset()
        self.start_timer()  # Restart the timer
        self.num_attempts = 0  # Reset the number of attempts
        self.update_attempts_label()

    def reset(self):
        self.grid.clear_widgets()
        self.images = ['assets/n.png', 'assets/o.png', 'assets/p.png', 'assets/q.png', 'assets/r.png', 'assets/s.png', 'assets/t.png', 'assets/u.png', 'assets/v.png', 'assets/w.png'] * 2
        shuffle(self.images)
        self.selected_images = []
        self.matched_images = []
        self.num_attempts = 0
        self.remaining_time = 60  # Reset the timer
        self.update_attempts_label()

        for image in self.images:
            btn = Button(background_normal='', background_color=(1, 1, 1, 1))
            btn.bind(on_release=self.on_image_click)
            self.grid.add_widget(btn)

        self.can_click = True


    def on_leave(self):
        self.reset()
        self.stop_timer()



class NormalGameScreen(Screen):
    def __init__(self, **kwargs):
        super(NormalGameScreen, self).__init__(**kwargs)
        self.images = ['assets/h.png', 'assets/i.png', 'assets/j.png', 'assets/k.png', 'assets/l.png', 'assets/m.png', 'assets/x.png', 'assets/y.png'] * 2
        shuffle(self.images)
        self.selected_images = []
        self.matched_images = []
        self.num_attempts = 0
        self.max_attempts = 16
        self.remaining_time = 90  # 2 minutes in seconds
        self.timer_event = None

        layout = self.ids.layout

        layout = BoxLayout(orientation='vertical', spacing=10)

        self.button_click_sound = SoundLoader.load('assets\mixkit-arcade-game-jump-coin-216.wav')
        self.button_click_sound.volume = 0 if MemoryGameApp.game_sound_state == 'On' else 1

        # Add a label to display remaining time
        self.time_label = Label(text=str(self.remaining_time), font_size=24, halign='right', size_hint=(1, 0.05), color=(0, 0, 0, 1), bold=True)
        layout.add_widget(self.time_label)

        # Add a label to display the number of attempts
        self.attempts_label = Label(text=f"Attempts: {self.num_attempts}/{self.max_attempts}", font_size=18, halign='left', size_hint=(1, 0.05), color=(1, 0, 0, 1), bold=True)
        layout.add_widget(self.attempts_label)

        self.grid = GridLayout(cols=4, spacing=10)
        layout.add_widget(self.grid)
        self.can_click = True

        for image in self.images:
            btn = Button(background_normal='', background_color=(1, 1, 1, 1))  # Set the background color to white (R, G, B, A)
            btn.bind(on_release=self.on_image_click)
            self.grid.add_widget(btn)

        back_to_menu_button = Button(
            text="Back to Main Menu",
            on_release=self.switch_to_menu,
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.5},
            background_normal='', 
            background_color=(1, 0.43, 0.85, 0.9)
        )
        layout.add_widget(back_to_menu_button)

        self.add_widget(layout)

    def start_timer(self):
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.remaining_time -= 1
        self.time_label.text = str(self.remaining_time)

        if self.remaining_time <= 0:
            self.game_over("Time is up! You ran out of time.")
            self.stop_timer()

    def stop_timer(self):
        if self.timer_event:
            self.timer_event.cancel()

    def on_image_click(self, button):
        if self.button_click_sound:
            self.button_click_sound.play()

        if not self.can_click or button in (image[0] for image in self.selected_images):
            return
    
        image_path = self.images[self.grid.children.index(button)]
        if image_path in self.matched_images:
            return
    
        if len(self.selected_images) < 2:
            button.background_normal = image_path
            self.selected_images.append((button, image_path))
    
        if len(self.selected_images) == 2:
            self.can_click = False  # Disable further clicks until the match check is complete
            Clock.schedule_once(self.check_match, 1)


    def check_match(self, dt):
        if self.selected_images[0][1] == self.selected_images[1][1]:
            self.matched_images.extend([self.selected_images[0][1], self.selected_images[1][1]])
            self.selected_images[0][0].disabled = True
            self.selected_images[1][0].disabled = True
            self.selected_images = []
            if len(self.matched_images) == len(self.images):
                self.game_over("Congratulations! You won!")
        else:
            self.selected_images[0][0].background_normal = ''
            self.selected_images[1][0].background_normal = ''
            self.selected_images = []
            self.num_attempts += 1
            if self.num_attempts >= self.max_attempts:
                self.game_over("Game over! You ran out of attempts.")

        self.can_click = True
        self.update_attempts_label()

    def update_attempts_label(self):
        self.attempts_label.text = f"Attempts: {self.num_attempts}/{self.max_attempts}"

    def game_over(self, message):
        self.stop_timer()
        self.show_game_over_popup(message)

    def show_game_over_popup(self, message):
        popup = Popup(title="Game Over",
                      content=BoxLayout(orientation='vertical', spacing=10, padding=10),
                      size_hint=(None, None), size=(400, 200),
                      auto_dismiss=False)  # Set auto_dismiss to False

        # Add the label to display the message
        popup.content.add_widget(Label(text=message, size_hint=(1, 0.8)))

        play_again_button = Button(text="Play Again", on_release=lambda btn: self.reset_game(btn, popup))
        popup.content.add_widget(play_again_button)

        popup.open()

    def switch_to_menu(self, instance):
        # sound_manager = SoundManager
        self.manager.current = 'main_menu'
        

    def reset_game(self, button, popup):
        popup.dismiss()
        self.manager.current = 'easy'
        self.manager.get_screen('easy').reset()
        self.start_timer()  # Restart the timer
        self.num_attempts = 0  # Reset the number of attempts
        self.update_attempts_label()

    def reset(self):
        self.grid.clear_widgets()
        self.images = ['assets/h.png', 'assets/i.png', 'assets/j.png', 'assets/k.png', 'assets/l.png', 'assets/m.png', 'assets/x.png', 'assets/y.png'] * 2
        shuffle(self.images)
        self.selected_images = []
        self.matched_images = []
        self.num_attempts = 0
        self.remaining_time = 90  # Reset the timer
        self.update_attempts_label()

        for image in self.images:
            btn = Button(background_normal='', background_color=(1, 1, 1, 1))
            btn.bind(on_release=self.on_image_click)
            self.grid.add_widget(btn)

        self.can_click = True


    def on_leave(self):
        self.reset()
        self.stop_timer()

class EasyGameScreen(Screen):
    def __init__(self, **kwargs):
        super(EasyGameScreen, self).__init__(**kwargs)
        self.images = ['assets/a.png', 'assets/b.png', 'assets/c.png', 'assets/d.png', 'assets/e.png', 'assets/f.png'] * 2
        shuffle(self.images)
        self.selected_images = []
        self.matched_images = []
        self.num_attempts = 0
        self.max_attempts = 20
        self.remaining_time = 90  # 2 minutes in seconds
        self.timer_event = None

        layout = self.ids.layout

        layout = BoxLayout(orientation='vertical', spacing=10)

        self.button_click_sound = SoundLoader.load('assets\mixkit-arcade-game-jump-coin-216.wav')
        self.button_click_sound.volume = 0 if MemoryGameApp.game_sound_state == 'On' else 1

        # Add a label to display remaining time
        self.time_label = Label(text=str(self.remaining_time), font_size=24, halign='right', size_hint=(1, 0.05), color=(0, 0, 0, 1), bold=True)
        layout.add_widget(self.time_label)

        # Add a label to display the number of attempts
        self.attempts_label = Label(text=f"Attempts: {self.num_attempts}/{self.max_attempts}", font_size=18, halign='left', size_hint=(1, 0.05), color=(1, 0, 0, 1), bold=True)
        layout.add_widget(self.attempts_label)

        self.grid = GridLayout(cols=4, spacing=10)
        layout.add_widget(self.grid)
        self.can_click = True

        for image in self.images:
            btn = Button(background_normal='', background_color=(1, 1, 1, 1))  # Set the background color to white (R, G, B, A)
            btn.bind(on_release=self.on_image_click)
            self.grid.add_widget(btn)

        back_to_menu_button = Button(
            text="Back to Main Menu",
            on_release=self.switch_to_menu,
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.5},
            background_normal='', 
            background_color=(1, 0.43, 0.85, 0.9)
        )
        layout.add_widget(back_to_menu_button)

        self.add_widget(layout)

    def start_timer(self):
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.remaining_time -= 1
        self.time_label.text = str(self.remaining_time)

        if self.remaining_time <= 0:
            self.game_over("Time is up! You ran out of time.")
            self.stop_timer()

    def stop_timer(self):
        if self.timer_event:
            self.timer_event.cancel()

    def on_image_click(self, button):
        if self.button_click_sound:
            self.button_click_sound.play()

        if not self.can_click or button in (image[0] for image in self.selected_images):
            return
    
        image_path = self.images[self.grid.children.index(button)]
        if image_path in self.matched_images:
            return
    
        if len(self.selected_images) < 2:
            button.background_normal = image_path
            self.selected_images.append((button, image_path))
    
        if len(self.selected_images) == 2:
            self.can_click = False  # Disable further clicks until the match check is complete
            Clock.schedule_once(self.check_match, 1)


    def check_match(self, dt):
        if self.selected_images[0][1] == self.selected_images[1][1]:
            self.matched_images.extend([self.selected_images[0][1], self.selected_images[1][1]])
            self.selected_images[0][0].disabled = True
            self.selected_images[1][0].disabled = True
            self.selected_images = []
            if len(self.matched_images) == len(self.images):
                self.game_over("Congratulations! You won!")
        else:
            self.selected_images[0][0].background_normal = ''
            self.selected_images[1][0].background_normal = ''
            self.selected_images = []
            self.num_attempts += 1
            if self.num_attempts >= self.max_attempts:
                self.game_over("Game over! You ran out of attempts.")

        self.can_click = True
        self.update_attempts_label()

    def update_attempts_label(self):
        self.attempts_label.text = f"Attempts: {self.num_attempts}/{self.max_attempts}"

    def game_over(self, message):
        self.stop_timer()
        self.show_game_over_popup(message)

    def show_game_over_popup(self, message):
        popup = Popup(title="Game Over",
                      content=BoxLayout(orientation='vertical', spacing=10, padding=10),
                      size_hint=(None, None), size=(400, 200),
                      auto_dismiss=False)  # Set auto_dismiss to False

        # Add the label to display the message
        popup.content.add_widget(Label(text=message, size_hint=(1, 0.8)))

        play_again_button = Button(text="Play Again", on_release=lambda btn: self.reset_game(btn, popup))
        popup.content.add_widget(play_again_button)

        popup.open()

    def switch_to_menu(self, instance):
        # sound_manager = SoundManager
        self.manager.current = 'main_menu'
        

    def reset_game(self, button, popup):
        popup.dismiss()
        self.manager.current = 'easy'
        self.manager.get_screen('easy').reset()
        self.start_timer()  # Restart the timer
        self.num_attempts = 0  # Reset the number of attempts
        self.update_attempts_label()

    def reset(self):
        self.grid.clear_widgets()
        self.images = ['assets/a.png', 'assets/b.png', 'assets/c.png', 'assets/d.png', 'assets/e.png', 'assets/f.png'] * 2
        shuffle(self.images)
        self.selected_images = []
        self.matched_images = []
        self.num_attempts = 0
        self.remaining_time = 90  # Reset the timer
        self.update_attempts_label()

        for image in self.images:
            btn = Button(background_normal='', background_color=(1, 1, 1, 1))
            btn.bind(on_release=self.on_image_click)
            self.grid.add_widget(btn)

        self.can_click = True


    def on_leave(self):
        self.reset()
        self.stop_timer()

class ChooseLevelScreen(Screen):
    def __init__(self, **kwargs):
        super(ChooseLevelScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

        self.button_click_sound = SoundLoader.load('assets\mixkit-arcade-game-jump-coin-216.wav')

        level_label = Label(text='Choose Level', font_size=40, color=(1, 0.48, 0.66, 1), bold=True)
        layout.add_widget(level_label)

        levels = ["Easy", "Normal", "Hard"]
        level_spinner = Spinner(text='Easy', values=levels, size_hint_y=None, height=44)
        layout.add_widget(level_spinner)

        start_button = Button(text="Start", size_hint_y=0.2, height=40, background_normal='', background_color=(0.32, 0.83, 0.85, 1))
        start_button.bind(on_release=self.start_button_callback)
        layout.add_widget(start_button)

        self.add_widget(layout)

    def start_button_callback(self, instance):
        # Add your code to handle the "Start" button action and level selection
        chosen_level = self.children[0].children[1].text  # Access the Spinner's selected value
        print(f"Start button pressed for level: {chosen_level}")
        # Add your logic to handle the chosen level and navigate accordingly

        if self.button_click_sound:
            self.button_click_sound.play()

        if chosen_level=='Easy':
            easy_game_screen = self.manager.get_screen('easy')
            easy_game_screen.start_timer()
            self.manager.current = 'easy'
        elif chosen_level=='Normal':
            normal_game_screen = self.manager.get_screen('normal')
            normal_game_screen.start_timer()
            self.manager.current = 'normal'
        elif chosen_level=='Hard':
            hard_game_screen = self.manager.get_screen('hard')
            hard_game_screen.start_timer()
            self.manager.current = 'hard'


class MyScreen(Screen):
    def __init__(self, **kwargs):
        super(MyScreen, self).__init__(**kwargs)

        layout = self.ids.layout  # Reference to the GridLayout in memorygame.kv

        # Add a Label for Main Menu with decoration
        main_menu_label = Label(text='Main Menu', font_size=40, color=(1, 0.48, 0.66, 1), bold=True)
        layout.add_widget(main_menu_label)

        # Add buttons for Start, Settings, Info, and Quit with decoration
        buttons = ["Start", "Settings", "Info", "Quit"]
        for btn_text in buttons:
            button = Button(text=btn_text, size_hint_y=0.2, height=40,background_normal='', background_color=(0.32, 0.83, 0.85, 1))
            button.bind(on_release=self.button_callback)
            layout.add_widget(button)

        # Load and play background sound
        self.background_sound = SoundLoader.load('assets/minifunk-67270.mp3')
        if self.background_sound:
            self.background_sound.loop = True
            self.background_sound.play()

        # Load sound for button click
        self.button_click_sound = SoundLoader.load('assets\mixkit-arcade-game-jump-coin-216.wav')

        # Initialize sound state
        self.bg_sound_state = 'Off'
        self.game_sound_state = 'Off'
        # MemoryGameApp.game_sound_state = self.game_sound_state

    def button_callback(self, instance):
        # Play sound when a button is clicked
        if self.button_click_sound:
            self.button_click_sound.play()

        button_text = instance.text
        if button_text == "Start":
            print("Start button pressed")
            # Navigate to the ChooseLevelScreen
            self.manager.current = "choose_level_screen"
        elif button_text == "Settings":
            print("Settings button pressed")
            # Add your code to handle the "Settings" button action
            self.show_settings_popup()
        elif button_text == "Info":
            print("Info button pressed")
            self.show_info_popup()
        elif button_text == "Quit":
            print("Quit button pressed")
            # Add your code to handle the "Quit" button action
            App.get_running_app().stop()

    def show_settings_popup(self):
        # Create the settings pop-up
        content = BoxLayout(orientation='vertical')

        mute_bg_label = Label(text='Mute Background Sound')
        mute_bg_toggle = ToggleButton(text=self.bg_sound_state,group='mute_bg', state='down',background_color=get_color_from_hex('#756AB6'))
        mute_bg_toggle.bind(on_release=self.toggle_bg_sound)

        content.add_widget(mute_bg_label)
        content.add_widget(mute_bg_toggle)

        popup = Popup(title='Settings', content=content, size_hint=(None, None), size=(400, 300))
        popup.open()

    def show_info_popup(self):
        # Create the info pop-up
        content = Label(text='This app make by CPE SWU 65')

        popup = Popup(title='Info', content=content, size_hint=(None, None), size=(400, 300))
        popup.open()
 

    def toggle_bg_sound(self, instance):
        print("Background sound toggled")
        if self.background_sound:
            self.bg_sound_state = 'On' if self.bg_sound_state == 'Off' else 'Off'
            self.background_sound.volume = 0 if self.bg_sound_state == 'On' else 1
            instance.text = self.bg_sound_state


class MemoryGameApp(App):
    game_sound_state = 'Off'  # Class-level variable to store the state of the game sound

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MyScreen(name="main_menu"))
        sm.add_widget(EasyGameScreen(name="easy"))
        sm.add_widget(NormalGameScreen(name="normal"))
        sm.add_widget(HardGameScreen(name="hard"))
        sm.add_widget(ChooseLevelScreen(name="choose_level_screen"))
        return sm

if __name__ == "__main__":
    MemoryGameApp().run()