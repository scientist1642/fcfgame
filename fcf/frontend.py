import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import Image

from client import Client

from kivy.config import Config
Config.set('graphics', 'width', '100')
Config.set('graphics', 'height', '200')

class Symbol(object):
    dark = '0' # can't see the board
    me = '1'
    empty = '2'
    frog = '3'
    fly = '4'

class Screen(GridLayout):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        # init keyboard 
        self.poll_interval = 0.2

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        strlayout = GridLayout(cols=3, row_force_default=True, row_default_height=40, size_hint_y=None, height=150) # string layouts
        
        self.username = TextInput(multiline=False, text='kenny')
        self.character = TextInput(multiline=False, text='frog')
        strlayout.add_widget(Label(text='username', size_hint_y=None,height=10))
        strlayout.add_widget(self.username)
        self.score_label = Label(text='0')
        strlayout.add_widget(self.score_label)
        strlayout.add_widget(Label(text='Ip address'))
        self.ip = TextInput(multiline=False, text='localhost')
        strlayout.add_widget(self.ip)
        self.connect_button = Button(text='connect')
        strlayout.add_widget(self.connect_button)
        strlayout.add_widget(Label(text='Character - frorg or fly',size_hint_y=None, height=10))
        strlayout.add_widget(self.character)
        
        self.join_button = Button(text='join game')
        strlayout.add_widget(self.join_button)
        self.connect_button.bind(on_press=self._connect_callback)
        self.join_button.bind(on_press=self._join_callback)

        self.rows = 2
        self.add_widget(strlayout)
        self.m = 10
        self.n = 11
        buttonLayout = GridLayout(cols = self.n)
        self.board = [[None for _ in xrange(self.m)] for _ in xrange(self.n)]
        for x in xrange(self.n):
            for y in xrange(self.m):
                self.board[x][y] = Button()
                buttonLayout.add_widget(self.board[x][y])
        self.add_widget(buttonLayout)
        
        self.game_started = False

        #client part
        self.client = Client()
        Clock.schedule_interval(self._render, self.poll_interval)
        
    def _connect_callback(self, r):
        if self.game_started:
            self._pop('Game already started')
            return 
        self.client.set_name(str(self.username.text))
        self.client.set_server_ip(str(self.ip.text))
        try:
            self.client.run()
        except Exception, e:
            self._pop('not able to connect' + e)
        self.game_started = True
    
    def _join_callback(self, r):
        if not self.game_started:
            self._pop("should connect first")
            return
        if not (self.character.text == 'fly' or 
                self.character.text == 'frog'):
            self._pop('please enter frog or fly')
            return
        self.client.choose_player(self.character.text[:2])

    def _pop(self, msg):
        p = Popup(title='warning',
                content=Label(text=msg),
                    size_hint=(None, None), size=(400, 400))
        p.open()

    def _color(self, symb, but):
        if symb == Symbol.dark:
            col =  (0, 0, 0, 1)
        elif symb == Symbol.empty:
            col= (0.282353 ,1, 1, 1)
        elif symb == Symbol.frog:
            col = (0.133333, 0.845098, 0.133333, 1)
        elif symb == Symbol.fly:
            col = ( 1, 0.0784314, 0.576471,1)
        elif symb == Symbol.me:
            col =  (0.117647, 0.564706, 1,1)
        but.background_color  = col

    def _render(self, dt):
        if not self.game_started:
            return
        s = self.client.get_board()
        if s is None:
            return
        # import pdb; pdb.set_trace()
        for x in xrange(self.n):
            for y in xrange(self.m):
                c = x * self.m + y
                self._color(s[c], self.board[x][y])

        self.score_label.text = str(self.client.get_score())

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        #self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        #self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        code = keycode[0]
        sym = keycode[1]
        d = sym[0] # d l r or u
        if len(modifiers) > 0:
            d += '2'
        else:
            d += '1'
        print(' - modifiers are %r' % modifiers)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        self.client.set_move(d)
        return True

class MyApp(App):
    def build(self):
        return Screen()

if __name__ == '__main__':
    MyApp().run()
