from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
import threading
import pyttsx3
from firebase import firebase
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.screen import MDScreen

Window.size = (350, 650)

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)



class Command(MDLabel):
    text = StringProperty
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_size = 17


class Response(MDLabel):
    text = StringProperty
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_size = 17


class ResponseImage(Image):
    source = StringProperty()


class Chatbot(MDApp):
    def build(self):

        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("Main.kv"))
        screen_manager.add_widget(Builder.load_file("Chats.kv"))
        screen_manager.add_widget(Builder.load_file("Login.kv"))
        screen_manager.add_widget(Builder.load_file("Register.kv"))
        screen_manager.add_widget(Builder.load_file("Homescreen.kv"))
        screen_manager.add_widget(Builder.load_file("Language.kv"))
        screen_manager.add_widget(Builder.load_file("admin.kv"))



        return screen_manager



    def register(self, nickname, stud_id, year, course, section, password):
        from firebase import firebase

        # initialize Firebase
        firebase = firebase.FirebaseApplication('https://test-102ae-default-rtdb.firebaseio.com/', None)

        # Importing Data
        data = {
            'Nickname': nickname,
            'Student ID': stud_id,
            'Year': year,
            'Course': course,
            'Section': section,
            'Password': password
        }
        # post Data
        # Database Name/Table
        firebase.post('test-102ae-default-rtdb/Users', data)

    dialog = None  # Variable to hold the dialog instance

    def show_register_result(self, success=True):
        if success:
            message = "Registration successful!"
        else:
            message = "Registration failed. Please check your input."

        self.dialog = MDDialog(
            title="Registration Status",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=self.close_dialog
                )
            ]
        )
        self.dialog.open()

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def login(self, stud_id, password):
        if not stud_id:
            print("Login failed - Please enter Stud_id")
            return
        if not password:
            print("Login failed - Please enter Password")
            return
        firebase_app = firebase.FirebaseApplication('https://test-102ae-default-rtdb.firebaseio.com/', None)

        # Get Data
        result = firebase_app.get('test-102ae-default-rtdb/Users', '')

        for i in result.keys():
            if 'Stud_ID' in result[i] and result[i]['Stud_ID'] == stud_id:
                if 'Password' in result[i] and result[i]['Password'] == password:
                    print("Logged in")

                    return

                print("Login failed - User not found or incorrect password")


    def show_login_result(self, success=True):
        if success:
            message = "Login Successful!"
        else:
            message = "Login failed. Please check your input."

        self.dialog = MDDialog(
            title="Login Status",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=self.close_dialog
                )
            ]
        )
        self.dialog.open()


    def bot_name(self):
        if screen_manager.get_screen('Main').bot_name.text != "":
            screen_manager.get_screen('Chats').bot_name.text = screen_manager.get_screen('Main').bot_name.text
            screen_manager.current = "Chats"

    def response(self, value):
        response = ""
        if value == "Hello" or value == "hello":
            response = f"Hello. I am Your Personal Assistant {screen_manager.get_screen('Chats').bot_name.text}"
        elif value == "How are you?" or value == "how are you":
            response = f"I'm doing well. Thanks {screen_manager.get_screen('Chats').bot_name.text}"
        elif value == "Fuck off" or value == "fuck off":
            response = f"Fuck you too {screen_manager.get_screen('Chats').bot_name.text}"
        elif value == "Images":
            screen_manager.get_screen('Chats').chat_list.add_widget(ResponseImage(source="Chatimage1.JPG"))
        elif value == "Kamusta ka?" or value == "kamusta ka":
            response = f"Okay lang{screen_manager.get_screen('Chats').bot_name.text}"
        else:
            response = "Sorry, could you say that again?"

        # Create a thread to speak the response
        threading.Thread(target=self.speak_response, args=(response,)).start()

        # Display the response in the chat list immediately
        screen_manager.get_screen('Chats').chat_list.add_widget(Response(text=response, size_hint_x=.75))

    def speak_response(self, text):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if "fil" in voice.languages:  # Check if the voice supports Filipino (Tagalog)
                engine.setProperty('voice', voice.id)
                break  # Use the first Tagalog voice found
        engine.say(text)
        engine.runAndWait()

    def send(self):
        global size, halign, value
        if screen_manager.get_screen('Chats').text_input.text != "":
            value = screen_manager.get_screen('Chats').text_input.text  # Get the user input text
            if len(value) < 6:
                size = .22
                halign = "center"
            elif len(value) < 11:
                size = .32
                halign = "center"
            elif len(value) < 16:
                size = .45
                halign = "center"
            elif len(value) < 21:
                size = .58
                halign = "center"
            elif len(value) < 26:
                size = .71
                halign = "center"
            else:
                size = .71
                halign = "left"
            screen_manager.get_screen('Chats').chat_list.add_widget(
                Command(text=value, size_hint_x=size, halign=halign))
            Clock.schedule_once(lambda dt: self.response(value),
                                2)  # Schedule the response method with the user input text after 2 seconds
            screen_manager.get_screen('Chats').text_input.text = ""

if __name__ == '__main__':
    Chatbot().run()
