# =================================================================================================
# Contributing Authors:	    Kevin Cosby, Oskar Flores 
# Email Addresses:          knco259@uky.edu, oskar.flores@uky.edu
# Date:                     2023 November 1
# Purpose:                  handles the client side of the game
# Misc:                     Released under GNU GPL v3.0
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket
import ssl
import json
import hashlib

from assets.code.helperCode import *

# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket) -> None:
    
    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
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

    if playerPaddle == "left":
        opponentPaddleObj = rightPaddle
        playerPaddleObj = leftPaddle
    else:
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle

    lScore = 0
    rScore = 0

    sync = 0

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
        
        try: 
            paddle_info = {
                "y_pos": playerPaddleObj.rect.y,
                "request": "update_paddle",
            }
            client.sendall(json.dumps(paddle_info).encode('utf-8'))
        except Exception as e:
            errText = "Error in sending paddle info!"
            textSurface = winFont.render(errText, False, (255, 0, 0), (0,0,0))
            textrect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            errMessage = screen.blit(textSurface, textRect)

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
                pointSound.play()
                ball.reset(nowGoing="left")
            elif ball.rect.x < 0:
                rScore += 1
                pointSound.play()
                ball.reset(nowGoing="right")
                
            # If the ball hits a paddle
            if ball.rect.colliderect(playerPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(playerPaddleObj.rect.center[1])
            elif ball.rect.colliderect(opponentPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                bounceSound.play()
                ball.hitWall()
            
            pygame.draw.rect(screen, WHITE, ball)
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
        sync += 1
        sys.stderr.write(f"sync: {sync}")
        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        # opponent's game

        try: 
            get_opponent_info= {
                "request": "get_opponent_paddle"
            }
            client.sendall(json.dumps(paddle_info).encode('utf-8'))

            data = client.recv(1024)
            server_response = json.loads(data.decode('utf-8'))
            opponent_paddle_pos = server_response.get("opponent_y", "Unknown")
            
            if opponent_paddle_pos == "Unknown":
                raise ValueError("unknown opponent paddle position received from server.") 

            opponentPaddleObj.rect.y = opponent_paddle_pos

        except Exception as e:
            errText = f"Error in receiving opponent paddle info! {e}"
            textSurface = winFont.render(errText, False, (255, 0, 0), (0,0,0))
            textrect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            errMessage = screen.blit(textSurface, textRect)

        # =========================================================================================

# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which
def joinServer(ip: str, port: str, username: str, password: str, errorLabel: tk.Label, app: tk.Tk) -> None:
    # Author:        Kevin Cosby, Oskar Flores
    #
    # Purpose:       Creates an initial connection to the server, receives parameters to initialize the game with,
    #                handles any errors or exceptions gracefully, starts the game if valid parameters received and
    #                connection to the server was successful
    #
    # Pre:           expects ip and port to point to a valid server instance, otherwise an exception will be raised.
    #                expects the username and password to be a valid combination, with the password being a sha-256 hash
    #                and not a plaintext password. errorLabel is for displaying errors in the UI, and the app is so that
    #                this method can hide the window and kill the app once the game is over
    #
    # Post:          This method will hide the tk UI, start the game, and then finally kill the tk app and the entire
    #                program once the game has ended. Otherwise, just returns nothing and we remain in the UI
    #
    # Arguments:
    #                ip            A string holding the IP address of the server
    #                port          A string holding the port the server is using
    #                username      A string holding the plaintext username for the player
    #                password      A string holding the sha256 hash of the password in hexadecimal format.
    #                errorLabel    A tk label widget, modify it's text to display messages to the user (example below)
    #                app           The tk window object, needed to kill the window
    
    # Get the required information from your server (screen width, height & player paddle, "left" or "right")
    try:
        # create a socket and connect to the server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # set 5 second timeout
        client.settimeout(5)
        # attempt to connect
        client.connect((ip, int(port)))
        
        # use a dict to hold user information
        player_info = {
            "username": username,
            "password": password,
            "request": "get_parameters"
        }
        
        # send this data to the server.
        client.sendall(json.dumps(player_info).encode('utf-8'))

        # Receive server response (json):
        data = client.recv(1024)
        server_response = json.loads(data.decode('utf-8'))
        
        # parse the data received from the server
        x_res = server_response.get("x_res", "Unknown")
        y_res = server_response.get("y_res", "Unknown")
        paddle_position = server_response.get("paddle_position", "Unknown")
        
        # ensure the validity of the data we received
        errors = []
        if not isinstance(x_res, int):
            errors.append(f"invalid x resolution received from the server. Value: {x_res}")
        if not isinstance(y_res, int):
            errors.append(f"invalid y resolution received from the server. Value: {y_res}")
        if paddle_position not in ["left", "right"]:
            errors.append(f"invalid paddle position received from the server. Value: {paddle_position}")
        
        # if any errors were received, update the error label to display them and return from this function
        # this should result in the user still being on the startup screen with the error message printed.
        if errors:
            errorLabel.config(text="\n".join(errors))
            errorLabel.update()
            return
        
        # Hides the window for settings
        app.withdraw()
        # if we have passed these checks and have valid information, play the game with these params
        playGame(x_res, y_res, paddle_position, client)
        # kills the window (effectively quitting the program)
        app.quit()
    except Exception as e:
        # if any exceptions were caught, update the error label to display it and return from this function
        # this should result in the user still being on the startup screen with the error message printed.
        errorLabel.config(text=f"Exception received: {e}")
        errorLabel.update()
        return

# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    # initialize TK app
    app = tk.Tk()
    # set window title to "Server Info"
    app.title("Server Info")
    
    # display the logo for the pong game
    image = tk.PhotoImage(file="./assets/images/logo.png")
    
    # display the title
    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)
    
    # ip label
    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)
    # ip entry box
    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)
    
    # port label
    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)
    # port entry box
    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)
    
    # username label
    usernameLabel = tk.Label(text="Username:")
    usernameLabel.grid(column=0, row=3, sticky="W", padx=8)
    # username entry box
    usernameEntry = tk.Entry(app)
    usernameEntry.grid(column=1, row=3)

    # password label
    passwordLabel = tk.Label(text="Password:")
    passwordLabel.grid(column=0, row=4, sticky="W", padx=8)
    # password entry box
    passwordEntry = tk.Entry(app)
    passwordEntry.grid(column=1, row=4)
    
    # error label (this was here before, not written by us)
    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=6, columnspan=2)
    
    # display join button at the bottom. When the join button is clicked, the joinServer function is called.
    # joinSever will accept the ip, port, username, encrypted password, as well as a label where error text
    # can be displayed, and the tk app instance its self. 
    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), 
                                                                   portEntry.get(), 
                                                                   usernameEntry.get(), 
                                                                   hashlib.sha256(passwordEntry.get().encode()).hexdigest(),
                                                                   errorLabel, 
                                                                   app))
    
    # define location of jumpbutton
    joinButton.grid(column=0, row=5, columnspan=2)
    
    # display the tkinter UI menu
    app.mainloop()

if __name__ == "__main__":
    startScreen()
    
    # Uncomment the line below if you want to play the game without a server to see how it should work
    # the startScreen() function should call playGame with the arguments given to it by the server this is
    # here for demo purposes only
    #playGame(640, 480,"left",socket.socket(socket.AF_INET, socket.SOCK_STREAM))
