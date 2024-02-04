import random

previousScores = []

def play():

    guess = -1
    tries = 0

    upperBoundary = int(input("Enter upper boundary: "))
    randomNum = random.randint(0, int(upperBoundary))

    print("I'm thinking of a number between 0 and " + str(upperBoundary))

    while guess != randomNum:
        if tries > 0:
            print("Tries: " + str(tries))
        try:
            guess = int(input("Enter your guess: "))
            if guess < 0 or guess > upperBoundary:
                print("Number must be between 0 and " + str(upperBoundary))
            else:
                tries += 1
                if guess < randomNum:
                    print("Too low!")
                elif guess > randomNum:
                    print("Too high!")
                else:
                    print("Correct! You got it in " + str(tries) + " tries!")
                    if len(previousScores) > 0:
                        if tries < min(previousScores):
                            print("New record!!")
                    previousScores.append(int(tries))
                    print("Scores: ", end="")
                    i = 0
                    for s in previousScores:
                        i += 1
                        if i == len(previousScores):
                            print(str(s))
                        else:
                            print(str(s) + "-", end="")
        except ValueError:
            print("Invalid input!")

tryAgain = True

while tryAgain:
    play()
    tryAgain = input("Try again? (y/n): ") == "y"