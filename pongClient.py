# =================================================================================================
# Contributing Authors:	    Kevin Cosby, Oskar Flores 
# Email Addresses:          knco259@uky.edu, oskar.flores@uky.edu
# Date:                     2023 November 15
# Purpose:                  handles the client side of the game
# Misc:                     Released under GNU GPL v3.0
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket
import ssl
import pdb
import json
import hashlib

import utility

from assets.code.helperCode import *

class PongClient:
    def __init__(self):
        # Pygame inits
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        self.client = None
        self.sync = 0
        self.desync = 0
        self.sync_every_n = 2

    def send_update_state(self, ypos, ballx, bally, ballxvel, ballyvel, sync_var, score):
            update_state = {
                "request": "update_state",
                "ypos": ypos,
                "ballx": ballx,
                "bally": bally,
                "ballxvel": ballxvel,
                "ballyvel": ballyvel,
                "sync": sync_var,
                "score": score,
            }
            utility.send_message(self.client, update_state)




# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
    def playGame(self, screenWidth, screenHeight, playerPaddle) -> None:
    
        # Constants
        WHITE = (255, 255, 255)
        clock = pygame.time.Clock()
        scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
        winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
        pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
        bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")


        # Display objects
        screen = pygame.display.set_mode((screenWidth, screenHeight))
        winMessage = pygame.Rect(0,0,0,0)
        topWall = pygame.Rect(-10,0,screenWidth+20, 10)
        bottomWall = pygame.Rect(-10, screenHeight-10, screenWidth+20, 10)
        centerLine = []
        for i in range(0, screenHeight, 10):
            centerLine.append(pygame.Rect((screenWidth/2)-5,i,5,5))

    

        # Paddle properties and init
        paddleHeight = 50
        paddleWidth = 10
        paddleStartPosY = (screenHeight/2)-(paddleHeight/2)
        leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, paddleWidth, paddleHeight))
        rightPaddle = Paddle(pygame.Rect(screenWidth-20, paddleStartPosY, paddleWidth, paddleHeight))

        ball = Ball(pygame.Rect(screenWidth/2, screenHeight/2, 5, 5), -5, 0)

        if playerPaddle == "player1":
            opponentPaddleObj = rightPaddle
            playerPaddleObj = leftPaddle
        else:
            opponentPaddleObj = leftPaddle
            playerPaddleObj = rightPaddle

        lScore = 0
        rScore = 0

        while True:
            # Wiping the screen
            screen.fill((0,0,0))

            # Getting keypress events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        playerPaddleObj.moving = "down"

                    elif event.key == pygame.K_UP:
                        playerPaddleObj.moving = "up"

                elif event.type == pygame.KEYUP:
                    playerPaddleObj.moving = ""

            # =========================================================================================
            # Your code here to send an update to the server on your paddle's information,
            # where the ball is and the current score.
            # Feel free to change when the score is updated to suit your needs/requirements

            which_score = 0
            if playerPaddle == "player1":
                which_score = lScore
            else:
                which_score = rScore

            self.send_update_state(playerPaddleObj.rect.y, ball.rect.x, ball.rect.y, ball.xVel, ball.yVel, self.sync, which_score)

            # =========================================================================================

            # Update the player paddle and opponent paddle's location on the screen
            for paddle in [playerPaddleObj, opponentPaddleObj]:
                if paddle.moving == "down":
                    if paddle.rect.bottomleft[1] < screenHeight-10:
                        paddle.rect.y += paddle.speed
                elif paddle.moving == "up":
                    if paddle.rect.topleft[1] > 10:
                        paddle.rect.y -= paddle.speed

            # If the game is over, display the win message
            if lScore > 4 or rScore > 4:
                winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
                textSurface = winFont.render(winText, False, WHITE, (0,0,0))
                textRect = textSurface.get_rect()
                textRect.center = ((screenWidth/2), screenHeight/2)
                winMessage = screen.blit(textSurface, textRect)
            else:

                # ==== Ball Logic =====================================================================
                ball.updatePos()

                # If the ball makes it past the edge of the screen, update score, etc.
                if ball.rect.x > screenWidth:
                    lScore += 1
                    #pointSound.play()
                    ball.reset(nowGoing="left")
                elif ball.rect.x < 0:
                    rScore += 1
                    #pointSound.play()
                    ball.reset(nowGoing="right")
                
                # If the ball hits a paddle
                if ball.rect.colliderect(playerPaddleObj.rect):
                    #bounceSound.play()
                    ball.hitPaddle(playerPaddleObj.rect.center[1])
                elif ball.rect.colliderect(opponentPaddleObj.rect):
                    #bounceSound.play()
                    ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
                # If the ball hits a wall
                if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                    #bounceSound.play()
                    ball.hitWall()
            
                pygame.draw.rect(screen,WHITE, ball)
                # ==== End Ball Logic =================================================================

            # Drawing the dotted line in the center
            for i in centerLine:
                pygame.draw.rect(screen, WHITE, i)
        
            # Drawing the player's new location
            for paddle in [playerPaddleObj, opponentPaddleObj]:
                pygame.draw.rect(screen, WHITE, paddle)

            pygame.draw.rect(screen, WHITE, topWall)
            pygame.draw.rect(screen, WHITE, bottomWall)
            scoreRect = updateScore(lScore, rScore, screen, WHITE, scoreFont)
            pygame.display.update([topWall, bottomWall, ball, leftPaddle, rightPaddle, scoreRect, winMessage])
            clock.tick(60)
    

            # This number should be synchronized between you and your opponent.  If your number is larger
            # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
            # catch up (use their info)
            self.sync += 1
        
            # =========================================================================================
            # Send your server update here at the end of the game loop to sync your game with your
            # opponent's game
            
            if (self.sync % self.sync_every_n == 0) or self.desync > self.sync_every_n:
                utility.send_message(self.client, {"request": "sync"})
                response = utility.receive_message(self.client)
            
                if response:
                    p1_ypos = response.get("p1_ypos")
                    p2_ypos = response.get("p2_ypos")
                    ballx = response.get("ballx")
                    bally = response.get("bally")
                    ballxvel = response.get("ballxvel")
                    ballyvel = response.get("ballyvel")
                    p1_score = response.get("p1_score")
                    p2_score = response.get("p2_score")
                    p1_sync = response.get("p1_sync")
                    p2_sync = response.get("p2_sync")
                
                    if playerPaddle == "player1" and (p2_sync < self.sync):
                        self.desync = self.sync - p2_sync
                        opponentPaddleObj.rect.y = p2_ypos
                    elif playerPaddle == "player2" and (p1_sync < self.sync):
                        self.desync = self.sync - p1_sync
                        opponentPaddleObj.rect.y = p1_ypos
                
                    #if self.desync > 1 or (self.sync % self.sync_every_n == 0):
                    ball.rect.x = ballx
                    ball.rect.y = bally
                    ball.xVel = ballxvel
                    ball.yVel = ballyvel
                    lScore = p1_score
                    rScore = p2_score
                    self.desync = 0
                else:
                    print("Error: did not receive a proper response from the server for syncing.", file=sys.stderr)
            

            # =========================================================================================

    # This is where you will connect to the server to get the info required to call the game loop.  Mainly
    # the screen width, height and player paddle (either "left" or "right")
    # If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
    # which client is which
    def joinServer(self, ip, port, username, password, gameid, errorLabel, app):
        # create a client-server connection using the ip/port provided
        try:
            # create a socket and connect to the server
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # set timeout
            self.client.settimeout(30)
            # attempt to connect
            self.client.connect((ip, int(port)))
        except Exception as e:
            # if it failed, print an error and update the error text in the GUI
            print(f"Error connecting to the server. Exception: {e}", file=sys.stderr)
            errorLabel.config(text=f"Exception received: {e}")
            errorLabel.update()
            return
   
        # get a response from the server. The server will request credentials at this point
        server_response = utility.receive_message(self.client)

        # Check if the server_response is not None before proceeding
        if server_response is None:
            print("Error: No response received from the server.", file=sys.stderr)
            errorLabel.config(text="No response received from the server.")
            errorLabel.update()
            return

        if server_response and server_response.get("request") == "credentials":
            credentials = {
                "request": "credentials",
                "username": username,
                "password": password,
                "gameid": gameid
            }
            # send credentials to the server
            utility.send_message(self.client, credentials)
    
        # wait for the go-ahead to start the game from the server
        while True:
            server_response = utility.receive_message(self.client)

            # Again, check if server_response is not None
            if server_response is None:
                print("No response received from server. Still waiting...", file=sys.stderr)
                errorLabel.config(text="No response received from server. Still waiting...")
                errorLabel.update()

            # if it's a request to start the game, perform related logic to begin the game
            if server_response.get("request") == "start_game":
                # collect parameters for initializing the game
                x_res = server_response.get("x_res", "Unknown")
                y_res = server_response.get("y_res", "Unknown")
                paddle = server_response.get("paddle", "Unknown")
            
                # test for validity of the parameters
                errors = []
                if not (isinstance(x_res, int) and isinstance(y_res, int)):
                    errors.append(f"Invalid x or y resolution received from the server. x_res: {x_res}, y_res: {y_res}")
                if paddle not in ["player1", "player2"]:
                    errors.append(f"Invalid paddle position, paddle: {paddle}")
            
                # display any errors that may have happened with the parameters accepted from the server
                if errors:
                    err_text = "\n".join(errors)
                    errorLabel.config(text=err_text)
                    errorLabel.update()
                    print(err_text, file=sys.stderr)
                    return

                # hides the window for the settings
                app.withdraw()
                # start the game
                self.playGame(x_res, y_res, paddle)
                # quit the program after the game has ended
                app.quit()
                return

    # This displays the opening screen, you don't need to edit this (but may if you like)
    def startScreen(self):
        # initialize TK app
        app = tk.Tk()
        app.title("Server Info")

        # display the logo for the pong game
        image = tk.PhotoImage(file="./assets/images/logo.png")

        # display the title
        titleLabel = tk.Label(image=image)
        titleLabel.grid(column=0, row=0, columnspan=2)

        # defaults for ease of use
        ipVar = tk.StringVar(value="localhost")
        portVar = tk.StringVar(value="1234")
        usernameVar = tk.StringVar(value="1")
        passwordVar = tk.StringVar(value="1")
        gameidVar = tk.StringVar(value="1")

        # ip label
        ipLabel = tk.Label(text="Server IP:")
        ipLabel.grid(column=0, row=1, sticky="W", padx=8)
        # ip entry box
        ipEntry = tk.Entry(app, textvariable=ipVar)
        ipEntry.grid(column=1, row=1)

        # port label
        portLabel = tk.Label(text="Server Port:")
        portLabel.grid(column=0, row=2, sticky="W", padx=8)
        # port entry box
        portEntry = tk.Entry(app, textvariable=portVar)
        portEntry.grid(column=1, row=2)

        # username label
        usernameLabel = tk.Label(text="Username:")
        usernameLabel.grid(column=0, row=3, sticky="W", padx=8)
        # username entry box
        usernameEntry = tk.Entry(app, textvariable=usernameVar)
        usernameEntry.grid(column=1, row=3)

        # password label
        passwordLabel = tk.Label(text="Password:")
        passwordLabel.grid(column=0, row=4, sticky="W", padx=8)
        # password entry box
        passwordEntry = tk.Entry(app, textvariable=passwordVar)
        passwordEntry.grid(column=1, row=4)

        # gameid label
        gameidLabel = tk.Label(text="Game ID:")
        gameidLabel.grid(column=0, row=5, sticky="W", padx=8)
        # gameid entry box
        gameidEntry = tk.Entry(app, textvariable=gameidVar)
        gameidEntry.grid(column=1, row=5)

        # error label
        errorLabel = tk.Label(text="")
        errorLabel.grid(column=0, row=7, columnspan=2)

        # display join button at the bottom. When the join button is clicked, the joinServer method is called
        joinButton = tk.Button(text="Join", command=lambda: self.joinServer(ipEntry.get(), 
                                                                            portEntry.get(), 
                                                                            usernameEntry.get(), 
                                                                            hashlib.sha256(passwordEntry.get().encode()).hexdigest(),
                                                                            gameidEntry.get(),
                                                                            errorLabel, 
                                                                            app))
        joinButton.grid(column=0, row=6, columnspan=2)
    
        # display the tkinter UI menu
        app.mainloop()


if __name__ == "__main__":
    client = PongClient()
    client.startScreen()
    
        # Uncomment the line below if you want to play the game without a server to see how it should work
        # the startScreen() function should call playGame with the arguments given to it by the server this is
        # here for demo purposes only
        #playGame(640, 480,"left",socket.socket(socket.AF_INET, socket.SOCK_STREAM))
