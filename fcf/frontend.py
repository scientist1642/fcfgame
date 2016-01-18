import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import Image

from pyro_client import Client
import Pyro4
import select

from kivy.config import Config
Config.set('graphics', 'width', '100')
Config.set('graphics', 'height', '200')

class Symbol(object):
    dark = '0' # can't see the board
    me = '1'
    empty = '2'
    frog = '3'
    fly = '4'

class MainScreen(GridLayout, Screen):
    def __init__(self, scr_manager, client, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.sm = scr_manager
        self.client = client
        # init keyboard
        self.poll_interval = 0.2
        self.pyro_interval = 0.1

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        strlayout = GridLayout(cols=3, row_force_default=True, row_default_height=40, size_hint_y=None, height=150) # string layouts

        strlayout.add_widget(Label(text=''))
        strlayout.add_widget(Label(text=''))
        self.score_label = Label(text='12323')
        strlayout.add_widget(self.score_label)

        self.username = TextInput(multiline=False, text='kenny')
        self.character = TextInput(multiline=False, text='frog')
        strlayout.add_widget(Label(text='username', size_hint_y=None,height=10))
        strlayout.add_widget(self.username)
        self.join_button = Button(text='join game')
        strlayout.add_widget(self.join_button)
        self.join_button.bind(on_press=self._join_callback)

        #self.connect_button.bind(on_press=self._connect_callback)
        #strlayout.add_widget(Label(text='Pyro address'))
        #self.ip = TextInput(multiline=False, text='localhost')
        #strlayout.add_widget(self.ip)
        #self.connect_button = Button(text='connect')
        #strlayout.add_widget(self.connect_button)

        strlayout.add_widget(Label(text='Character - frorg or fly',size_hint_y=None, height=10))
        strlayout.add_widget(self.character)
        strlayout.add_widget(Button(text='Exit', on_press=self.change_to_init_scr))

        self.rows = 2
        self.add_widget(strlayout)
        self.m = 10
        self.n = 13
        buttonLayout = GridLayout(cols = self.n)
        self.board = [[None for _ in xrange(self.m)] for _ in xrange(self.n)]
        for x in xrange(self.n):
            for y in xrange(self.m):
                self.board[x][y] = Button()
                buttonLayout.add_widget(self.board[x][y])
        self.add_widget(buttonLayout)
        
        self.game_started = False
        self.client.start_updating_servers()

        #client part
        Clock.schedule_interval(self._render, self.poll_interval)

    """
    def _connect_callback(self, r):
        if self.game_started:
            self._pop('Game already started')
            return 
        self.client.set_name(str(self.username.text))
        self.client.set_uri(str(self.ip.text))
        try:
            self.client.connect()
        except Exception, e:
            self._pop('not able to connect' + str(e))
            print "".join(Pyro4.util.getPyroTraceback())
            raise e
        self.game_started = True
    """

    def _join_callback(self, r):
        if not self.client.game_started:
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
        but.background_color = col

    def _render(self, dt):
        if not self.client.game_started:
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
    
    def disconnect(self):
        if self.game_started:
            self.client.disconnect()

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
        if not self.client.game_started:
            return True
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        self.client.set_move(d)
        return True

    def change_to_init_scr(self, r):
        self.client.stop_server()
        self.client.start_updating_servers()
        self.sm.current = 'initial'
        self.sm.get_screen("initial").render()

class InitialScreen(Screen):
    def __init__(self, scr_manager, client, **kwargs):
        super(InitialScreen, self).__init__(**kwargs)
        self.sm = scr_manager
        self.client = client
        self.render()
    
    def _pop(self, msg):
        p = Popup(title='warning',
                content=Label(text=msg),
                    size_hint=(None, None), size=(400, 400))
        p.open()

    def render(self):
        # create content and add to the popup
        connect_but = Button(text='Connect to game!')
        create_but = Button(text='Create game')
        check_servers = Button(text='Update servers')
        #button box
        button_box = BoxLayout(orientation='vertical', spacing=10)
        self.username_text = TextInput(text="username", size_hint=(1, 1))
        button_box.add_widget(self.username_text)
        button_box.add_widget(connect_but)
        button_box.add_widget(create_but)
        button_box.add_widget(check_servers)
        #servers box
        servers_box = BoxLayout(orientation='vertical')
        self.servers_label = Label(text="Servers list",
                                   size_hint=(1.0, 1.0),
                                   halign='left',
                                   valign='top',
                                   padding=(10, 10))
        self.servers_label.bind(size=self.servers_label.setter('text_size'))
        servers_box.add_widget(self.servers_label)
        self.server_text = TextInput(text="enter server Number!", size_hint=(1, .1))
        servers_box.add_widget(self.server_text)
        #outer box
        outer_box = BoxLayout()
        outer_box.add_widget(button_box)
        outer_box.add_widget(servers_box)
        self.popup = Popup(title='Initial screen',
                           content=outer_box,
                           auto_dismiss=False,
                           size_hint=(0.7,0.7),
                           )

        connect_but.bind(on_press=self.connect_btn_callback)
        create_but.bind(on_press=self.create_btn_callback)
        #check_servers.bind(on_press=self._update_servers)
        self.popup.open()
        self.servupd_interval = 2 
        Clock.schedule_interval(self._upd_servers, self.servupd_interval)

    def _upd_servers(self, dt):
        av_servers = self.client.get_aval_servers()
        self.servers_label.text = '\n'.join(av_servers)
        serv_with_nums = map(lambda (x, y): str(x) + ') ' + y, enumerate(av_servers))
        self.servers_label.text = '\n'.join(serv_with_nums)

    def connect_btn_callback(self, dt):
        def is_int(s):
            try: 
                int(s)
                return True
            except ValueError:
                return False

        #self.client.stop_server()
        #self.servers_label.text = '1)PYRO:server.game@25.63.229.152:60562'
        server_text = str(self.servers_label.text)
        server_num = self.server_text.text.strip()
        if not is_int(server_num):
            self._pop('Enter server number only without ")"!')
            #return
        
        to_connect = None 
        for serv in server_text.split('\n'):
            if serv.startswith(server_num):
                _, to_connect = serv.split(')', 1)
         
        if not to_connect:
            self._pop("no server was found with such server")
            #return

        # start the server
        
        self.client.stop_updating_servers()
        #self._pop(to_connect.strip())
        # connect
        self.connect_to_serv(str(self.username_text.text), str(self.server_text))

    
    def connect_to_serv(self, username, uri):
        self.client.set_name(username)
        self.client.set_uri(uri)
        print "uri is -", uri
        try:
            self.client.connect()
        except Exception, e:
            self._pop('not able to connect' + str(e))
            print "".join(Pyro4.util.getPyroTraceback())
            raise e

        self.client.game_started = True


    def create_btn_callback(self, r):
        
        self.client.stop_updating_servers()
        self.client.start_server()
        #connect
        self.connect_to_serv(str(self.username_text.text), self.client.server.uri)

        ### 
        self.popup.dismiss()
        self.sm.current = 'main'

    def _update_servers(self, r):
        text = '\n'.join([str(i)+". " for i in xrange(10)])
        self.servers_label.text = text
        pass

    def disconnect(self):
        pass


class MyApp(App):
    def build(self):
        # Create the screen manager
        self.sm = ScreenManager()
        self.client = Client() # client for gui
        self.main_scr = MainScreen(self.sm, self.client, name='main')
        self.init_scr = InitialScreen(self.sm, self.client, name='initial')
        self.sm.add_widget(self.init_scr)
        self.sm.add_widget(self.main_scr)
        return self.sm
    def on_stop(self):
        self.client.stop_updating_servers() 
        self.main_scr.disconnect()
        self.init_scr.disconnect()

if __name__ == '__main__':
    MyApp().run()
