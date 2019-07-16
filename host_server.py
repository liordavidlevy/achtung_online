# -*- coding: utf-8 -*-
import threading
from socket import *
import time
import random
import ctypes

HOST = gethostbyname(gethostname())  # gets the servers' ip address
Udp_Port = 507  # second room server's port
ADDR = (HOST, 505)  # address of main server


class Game(threading.Thread):  # manages each game
    def __init__(self, IPs, clients):  # defines room server, players' dictionary and their number
        global Udp_Port
        self.udp_server = socket(AF_INET, SOCK_DGRAM)
        self.udp_server.bind((HOST, Udp_Port))
        self.num_of_players = len(IPs)
        self.IPs = IPs
        self.clients = clients
        self.players = {'Addresses': [], 'Colors': [], 'Scores': [], 'Start_position': [], 'Start_heading': [],
                        'Alive': []}
        """" dictionary consisting players' colors, start positions and headings, addresses and scores """
        self.colors = ['red', 'green', 'magenta', 'blue', 'grey', 'tomato', 'salmon', 'tan',  # list of available of
                       'chocolate', 'purple', 'deep sky blue', 'orange red', 'forest green']  # players
        threading.Thread.__init__(self)

    def run(self):  # sets some of the values in players, does preparations for game
        try:
            global Udp_Port
            for client in self.clients:  # sends each client port of room server
                client.send(str(Udp_Port))
                client.close()
            Udp_Port += 1
            addresses = []
            for x in range(self.num_of_players):
                data, address = self.udp_server.recvfrom(4)
                if address[0] in self.IPs:
                    addresses.append(address)
            self.players['Addresses'] = addresses
            random.shuffle(self.colors)
            for x in range(self.num_of_players):  # assigns each player a random color
                self.players['Colors'].append(self.colors[x])
                self.players['Scores'].append(0)
                self.players['Start_position'].append([0, 0])
                self.players['Start_heading'].append(0)
                self.udp_server.sendto(str(x), self.players['Addresses'][x])
            for x in range(self.num_of_players):
                self.udp_server.sendto(','.join(self.players['Colors']), self.players['Addresses'][x])
            while max(self.players['Scores']) < self.num_of_players * 5:  # runs matches until one player won
                for x in range(self.num_of_players):
                    self.players['Alive'].append(x)
                    self.udp_server.sendto('not over:' + str(self.players['Scores'].index(max(self.players['Scores']))),
                                           self.players['Addresses'][x])
                self.match()
            for x in range(self.num_of_players):  # when game is over, server sends the clients the winner
                self.udp_server.sendto('over:' + str(self.players['Scores'].index(max(self.players['Scores']))),
                                       self.players['Addresses'][x])
        except error as e:  # in case one of the players gets disconnected or the game ends, the server closes
            print e
        time.sleep(3)
        self.udp_server.close()

    def match(self):  # does preparations for each match
        positions = ''
        for x in range(self.num_of_players):
            self.players['Start_position'][x][0] = str(random.randint(-615, 375))
            self.players['Start_position'][x][1] = str(random.randint(-325, 335))
            self.players['Start_heading'][x] = str(random.randint(0, 360))
            positions += ','.join(self.players['Start_position'][x]) + '/'
        positions = positions[:-1]
        for x in range(self.num_of_players):
            self.udp_server.sendto(positions, self.players['Addresses'][x])
            self.udp_server.sendto(','.join(self.players['Start_heading']), self.players['Addresses'][x])
        time.sleep(0.5)
        self.movements()  # starts the game in each match

    def movements(self):  # sends each client's movements to the rest, send scores when match ends
        while len(self.players['Alive']) > 1:  # runs until there's only one player left
            data, address = self.udp_server.recvfrom(1)
            num = self.players['Addresses'].index(address)
            if data == 'R' or data == 'L' or data == 'S':
                reply = data + ':' + str(num)
            elif data == 'O' and num in self.players['Alive']:  # removes player from alive list whe is out plus bug fix
                self.players['Alive'].remove(num)
                for x in self.players['Alive']:
                    self.players['Scores'][x] += 1
                reply = data + ':' + str(num)
            else:
                continue  # bug fix
            for x in range(self.num_of_players):
                self.udp_server.sendto(reply, self.players['Addresses'][x])
        self.udp_server.settimeout(0.3)  # bug fix start
        try:
            data, address = self.udp_server.recvfrom(1)
        except timeout:
            pass
        self.udp_server.settimeout(None)  # bug fix end
        self.players['Alive'].pop()
        scores = ','.join(map(str, self.players['Scores']))
        for x in range(self.num_of_players):  # sends current scores
            self.udp_server.sendto(scores, self.players['Addresses'][x])


class Timer(threading.Thread):
    def __init__(self, time_to):  # sets the time for the timer to run as attribute
        self.time_to = time_to
        threading.Thread.__init__(self)

    def run(self):  # starts the timer for x seconds
        time.sleep(self.time_to)


class Connection(threading.Thread):
    def __init__(self):  # defines the main server that connects to players and assigns them to room every 15 seconds
        self.running = None
        self.left_player = None
        self.clients = None
        self.IPs = None
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(ADDR)
        self.socket.listen(20)  # max twenty players connecting to server playing at the same time
        threading.Thread.__init__(self)

    def run(self):  # sets the timer for 15 seconds and each run of loop tries to set a new room
        while True:
            self.clients = []
            self.IPs = []
            t = Timer(15)
            t.start()
            threading.Thread(target=self.append_players).start()
            t.join()
            if not t.is_alive():
                self.stop()
            if len(self.clients) > 1:
                game = Game(self.IPs, self.clients)
                game.start()
            elif len(self.clients) == 1:
                """" if there's only one player in current room the game doesn't start and
                 player transferred to left player"""
                self.left_player = (self.IPs[0], self.clients[0])

    def append_players(self):
        self.running = True
        if self.left_player:  # if there's left player, he gets in the room first before listening to requests
            IP, client = self.left_player[0], self.left_player[1]
            self.clients.append(client)
            self.IPs.append(IP)
            self.left_player = None
        while self.running:
            if len(self.clients) == 3:
                break
            print "waiting"
            client, address = self.socket.accept()
            self.clients.append(client)
            self.IPs.append(address[0])
            print 'Got Connection from %s' % address[0] + ' port ' + str(address[1])

    def stop(self):  # stops receiving client's requests to connect when num of players in current room reaches three
        self.running = False


def show_ip():  # displays a window showing the server's ip address with one button OK
    ctypes.windll.user32.MessageBoxA(None, 'The server''s ip address is: ' + HOST, 'Achtung', None)


Connection().start()  # initiates the main server
threading.Thread(target=show_ip).start()
