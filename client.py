import socket
import time
import turtle
import keyboard
from os import path
import threading
from ipaddress import ip_address
from ctypes import windll
import Tkinter
Host = socket.gethostbyname(socket.gethostname())
running = True
my_places = []
others_places = []
MR_YESNO = 4
window = Tkinter.Tk()
window.title('Achtung')  # sets title of window
window.iconbitmap(path.realpath('icon.ico'))  # sets icon of window
Tkinter.Label(text='Enter the IP address of the server, press Enter when you are done\nMAKE SURE YOU ENTER THE CORRECT'
                   ' ONE\n (if server on same pc, just press Enter now)').pack()
ip = Tkinter.Entry(window)  # defines a widget to edit text on window
ip.bind("<Return>", lambda event: pressed())  # runs the function pressed when the key Enter gets pressed
ip.pack()


class Client(object):
    def __init__(self, port):  # defines the client's udp server for game
        global Host
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (Host, int(port))

    def start(self):  # tests connection and gets number of my player
        try:
            self.client.sendto('test', self.address)
            data, address = self.client.recvfrom(1024)
            Game(data, self.client, self.address).start()
        except socket.error as e:  # if server or client gets disconnected an error message is shown
            end(e)


class Game(object):
    def __init__(self, player, client, address):  # sets dictionary players, server's address and timeout for messages
        self.players = {'Colors': [], 'Scores': [], 'Start_position': [], 'Start_heading': [], 'Turtles': []}
        self.num_of_players = 0
        self.my_player = int(player)
        self.client = client
        self.client.settimeout(5)
        self.server_address = address
        self.window = None

    def start(self):  # does preparations for the game
        try:
            data, address = self.client.recvfrom(1024)
            colors = data.split(',')
            self.num_of_players = len(colors)
            self.boundaries()  # sets the game window
            for x in range(self.num_of_players):
                self.players['Colors'].append(colors[x])
                self.players['Scores'].append(0)
                self.players['Start_position'].append([0, 0])
                self.players['Start_heading'].append(0)
                self.players['Turtles'].append(turtle.Turtle('circle'))
            reply = self.client.recvfrom(1024)[0].split(':')
            while reply[0] != 'over':  # runs matches until server sends that the game is over
                for x in range(self.num_of_players):
                    self.players['Turtles'][x].clear()  # clears the trail of each player at end of match (besides last)
                    self.build_turtle(x)
                self.match()
                reply = self.client.recvfrom(1024)[0].split(':')
            time.sleep(0.5)
            for x in range(self.num_of_players):
                self.players['Turtles'][x].clear()  # clears trail of each player
                self.build_turtle(x)
            self.winner(int(reply[1]))
            time.sleep(10)
        except (socket.error, IOError, socket.timeout) as e: # if server or player disconnects
            #  an appropriate message is shown
            end(e)
            self.client.close()

    def winner(self, winner):  # writes the name of the winner on the screen with his color
        self.players['Turtles'][winner].setposition(-620, -70)
        self.players['Turtles'][winner].write(str(self.players['Colors'][winner]) + " Wins!", False, "left", ("Segoe Print", 100, "normal"))

    def boundaries(self):  # sets boundaries of screen and scores title
        self.window = turtle.Screen()
        self.window.setup(1280, 720)
        self.window.bgcolor('black')
        self.window.title('Achtung')
        bounder = turtle.Turtle("circle")
        bounder.speed(speed=5)
        bounder.turtlesize(0.3, 0.3)
        bounder.color("yellow")
        bounder.penup()
        bounder.setposition(-637, 355)
        bounder.pendown()
        bounder.pencolor("yellow")
        bounder.pensize(3)
        bounder.setposition(-637, -350)
        bounder.setposition(400, -350)
        bounder.setposition(400, 357)
        bounder.setposition(-637, 357)
        bounder.setposition(630, 357)
        bounder.setposition(630, -350)
        bounder.setposition(400, -350)
        bounder.setposition(400, 250)
        bounder.setposition(400, 275)
        bounder.penup()
        bounder.setposition(415, 275)
        bounder.write("Up To " + str(self.num_of_players*5), False, "left", ("Segoe Print", 30, "normal"))
        bounder.setposition(400, 250)
        bounder.pendown()
        bounder.setposition(635, 250)

    def match(self):  # does preparations for each match and starts game
        try:
            position, address = self.client.recvfrom(1024)
            heading, address = self.client.recvfrom(1024)
            positions = position.split('/')
            headings = heading.split(',')
            for x in range(self.num_of_players): # move players according to reply
                position = positions[x].split(',')
                self.players['Turtles'][x].setposition(int(position[0]), int(position[1]))
                self.players['Turtles'][x].setheading(int(headings[x]))
                self.players['Turtles'][x].speed(speed=0)
                self.players['Turtles'][x].pendown()
                self.players['Turtles'][x].forward(8)
            time.sleep(1)
            self.movement()
            time.sleep(0.5)
        except socket.error or socket.timeout as e:  # if server or player disconnects an appropriate message is shown
            end(e)

    def movement(self):  # shows the movements of each player on screen while game is running
        global my_places, others_places
        dis = {'L': -8, 'R': 8, 'S': 0}  # sets the possible angel distortions per keypress
        remaining = []
        speed = 9
        if self.num_of_players > 2:
            speed = 0
        for x in range(self.num_of_players):
            self.players['Turtles'][x].speed(speed=speed)
            remaining.append(x)
        count = 0
        try:
            while len(remaining) > 1:  # loop runs while current player isn't out
                if keyboard.is_pressed("Right") or keyboard.is_pressed("d"):
                    reply = 'L'
                elif keyboard.is_pressed("Left") or keyboard.is_pressed("a"):
                    reply = 'R'
                else:
                    reply = 'S'
                if 47 > count > 44:
                    for x in remaining:
                        self.players['Turtles'][x].penup()
                else:
                    if count > 46:
                        count = 0
                    for x in remaining:
                        self.players['Turtles'][x].pendown()
                        if x != self.my_player:
                            others_places.append(self.players['Turtles'][x].position())  # appends other players snd
                    my_places.append(self.players['Turtles'][self.my_player].position())  # my players positions
                if self.is_out():  # checks if current player is out                     # for collision detection
                    reply = 'O'
                    self.client.sendto(reply, self.server_address)
                    break
                self.client.sendto(reply, self.server_address)
                for x in remaining: # handles movement of each players
                    move, address = self.client.recvfrom(3)
                    command = move.split(':')
                    if command[0] == 'O' and int(command[1]) in remaining:
                        remaining.remove(int(command[1]))
                        for x in remaining:
                            self.players['Turtles'][x].speed(speed=9)
                    elif command[0] != 'O':
                        self.players['Turtles'][int(command[1])].left(dis[command[0]])
                        self.players['Turtles'][int(command[1])].forward(8)
                count += 1
            while len(remaining) > 1:  # runs when current player is out and num of players alive is not 1
                if 47 > count > 44:
                    for x in remaining:
                        self.players['Turtles'][x].penup() # sets players path as blank
                else:
                    if count > 46:
                        count = 0
                    for x in remaining:
                        self.players['Turtles'][x].pendown()  # sets players' path to their matching color
                for x in remaining:  # handles movement of each players
                    move, address = self.client.recvfrom(3)
                    command = move.split(':')
                    if command[0] == 'O' and int(command[1]) in remaining:
                        remaining.remove(int(command[1]))
                    elif command[0] != 'O':
                        self.players['Turtles'][int(command[1])].left(dis[command[0]])
                        self.players['Turtles'][int(command[1])].forward(8)
                count += 1
            score, address = self.client.recvfrom(1024)  # receives scores
            scores = score.split(',')
            for x in range(self.num_of_players):
                self.players['Scores'][x] = int(scores[x])  # updates scores
            del my_places[:]  # deletes my player positions
            del others_places[:]  # deletes other players positions
        except socket.timeout or socket.error as e:  # if server or player disconnects an appropriate message is shown
            end(e)

    def is_out(self):  # checks if my player collided with a trail or boundary on screen
        global my_places, others_places
        xp, yp = self.players['Turtles'][self.my_player].position()
        if xp >= 396 or xp <= -631 or yp >= 349 or yp <= -346:
            return True
        if len(my_places) > 2:  # bug fix condition
            for x, y in my_places[:-2]:
                if self.distance(xp, yp, x, y) < 6:
                    return True
        for x, y in others_places:
            if self.distance(xp, yp, x, y) < 6:
                return True

    def distance(self, x1, y1, x2, y2):  # returns the distance between two points
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def build_turtle(self, num):  # defines each player an writes it's score
        self.players['Turtles'][num].shape('circle')
        self.players['Turtles'][num].color('yellow')
        self.players['Turtles'][num].pencolor(self.players['Colors'][num])
        self.players['Turtles'][num].turtlesize(0.35, 0.35)
        self.players['Turtles'][num].penup()
        self.players['Turtles'][num].pensize(4)
        self.players['Turtles'][num].speed(speed=0)
        self.players['Turtles'][num].penup()
        self.players['Turtles'][num].setposition(415, 200 - 50*num)
        if num == self.my_player:  # draws an underline below my players score
            self.players['Turtles'][num].pendown()
        self.players['Turtles'][num].write(self.players['Colors'][num] + ': ' + str(self.players['Scores'][num]), True,
                                           "left", ("Segoe Print", 17, "normal"))
        self.players['Turtles'][num].pensize(6)
        self.players['Turtles'][num].penup()


class Connection(threading.Thread):
    def __init__(self):  # defines the TCP client
        global Host
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (Host, 505)
        threading.Thread.__init__(self)

    def run(self):  # tries to connect multiple times to main server
        while True:
            try:
                self.client.connect(self.server_address)
                port = self.client.recv(1024)
                self.client.close()
                if port:
                    Client(port).start()
                    break
            except socket.error:
                pass


def end(e):  # displays an appropriate message in case the server or on of the players gets disconnected
    windll.user32.MessageBoxA(None, 'One of the players or the server got disconnected.\n Press OK and start the program'
                                    ' again', None, 0)
    exit()


def pressed(): # checks ip entered on window's entry
    global Host, ip, window
    host = ip.get()
    try:
        if not host:  # if there's no text in entry the server's ip equals to client's ip (both running on same pc)
            Host = socket.gethostbyname(socket.gethostname())
        else:  # if ip is valid or empty no exception is raised, window gets closed and the connection starts
            ip_address(unicode(host))
            Host = host
        window.destroy()
        Connection().start()
    except ValueError:  # if the ip entered is invalid, an exception is raised, a message is shown asking to correct ip
        if windll.user32.MessageBoxA(None, 'invalid ip\npress ok and try again', None, 1) == 2:
            exit()


window.mainloop()
