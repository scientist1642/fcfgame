import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock

from client import Client

class Screen(GridLayout):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        # init keyboard 

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        strlayout = GridLayout(cols=3, row_force_default=True, row_default_height=40) # string layouts
        
        
        self.username = TextInput(multiline=False)
        self.character = TextInput(multiline=False)
        strlayout.add_widget(Label(text='username', size_hint_y=None,height=10))
        strlayout.add_widget(self.username)
        self.score_label = Label(text='25')
        strlayout.add_widget(self.score_label)
        strlayout.add_widget(Label(text='Ip address'))
        self.ip = TextInput(multiline=False)
        strlayout.add_widget(self.ip)
        self.connect_button = Button(text='connect')
        strlayout.add_widget(self.connect_button)
        strlayout.add_widget(Label(text='Character - fr or fl',size_hint_y=None, height=10))
        strlayout.add_widget(self.character)
        
        self.join_button = Button(text='join game')
        strlayout.add_widget(self.join_button)
        self.connect_button.bind(on_press=self._connect_callback)
        self.join_button.bind(on_press=self._join_callback)

        self.rows = 2
        self.add_widget(strlayout)
        self.m = 10
        self.n = 10
        buttonLayout = GridLayout(cols = self.n)
        self.board = [[None for _ in xrange(self.m)] for _ in xrange(self.n)]
        for x in xrange(self.n):
            for y in xrange(self.m):
                self.board[x][y] = Button(text='H')
                buttonLayout.add_widget(self.board[x][y])
        self.add_widget(buttonLayout)
        
        self.game_started = False

        #client part
        self.client = Client()
        Clock.schedule_interval(self._render, 0.5)
        
    def _connect_callback(self, r):
        self.client.set_name(self.username.text)
        self.client.set_server_ip(self.ip)
        self.client.run()
    
    def _join_callback(self, r):
        print 'bb'

    def _render(self, dt):
        if not self.game_started:
            return
        s = self.client.get_board()
        for x in xrange(self.n):
            for y in xrange(self.m):
                c = x * m + y
                if s[c] == '0':
                    self.board[x][y].backgrund_color = (0,1,1,2)


    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        if keycode[0] == 102:
            self.board[2][3].background_color = (1, 0, 0, 1) 
        print(' - modifiers are %r' % modifiers)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

class MyApp(App):
    def build(self):
        return Screen()

if __name__ == '__main__':
    MyApp().run()
