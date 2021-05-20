import PySimpleGUI as sg
import os
import base64
import random

#Global variables, these are known and used in all of the program in any function
WORD_LIST = []
IMAGE_LIST = []
GAME_WORD = []
LOSER_IMAGE = 0
WINNER_IMAGE = 0
#Dictionsry used to indicate if a letter has been perviously selected
LETTER_DICTIONARY = {'a':False,'b':False,'c':False,'d':False,'e':False,'f':False,'g':False,'h':False,'i':False,'j':False,'k':False,'l':False,'m':False,'n':False,'o':False,'p':False,'q':False,'r':False,'s':False,'t':False,'u':False,'v':False,'w':False,'x':False,'y':False,'z':False}

#implement logic to load all the images
def loadAllImages():
    #Declare IMAGE_LIST as global so that the interpreter knows that we are talking about the global variable,
    #and that we are not declaring it again in here
    global IMAGE_LIST
    #We have 10 possible tries to get the word (the number of images we use)
    for x in range(11):
        #We load a single image that is encoded in base64 because PySimpleGUI can only process images encoded in base64
        base64Image = loadImage(str(x))
        #So we don't have to load an image from file every time, we load them all in the beginning and store them
        #in an array in memory
        IMAGE_LIST.append(base64Image)

#Load a single image from a file to memory to be used by the program
#It is assumed that the path to the directory that contains the images is:
# The current working directory (cwd) + venv (Python virtual environment which is a part of PyCharm)
# + images (the image directory)
#We use base 64 encoding because we use PySimpleGUI to display the application and in order to display images
#PySimpleGUI needs them to be in PNG format and encoded in base 64 (which is just a way of representing the image values
#in one of 64 symbols)
def loadImage(imageName):
    cwd = os.getcwd()
    #Debug: uncomment the print statement to make sure the file path to the current working directory is correct
    #print(cwd)
    #file name is combined with the file type extension to point to the right file
    fname = imageName+'.png'
    #We use \\ to denote a single \ in a string. This is Windows specific, for Linux we need to change this to /
    img64 = open('{}\\venv\\images\\{}'.format(cwd, fname),'rb+')
    base64_image = base64.b64encode(img64.read())

    return base64_image

#Check that the user has only inputted a single letter
def checkForASingleLetter(pickedLetter):
    if len(pickedLetter) == 1:
        return True
    return False

#The main part of the program; Create the Window UI and process the user input and change output
#Note: The word length limit I put on this game is 10 characters, this is due to UI constraints more than anything else.
#More than 10 characters in the UI looks ugly
def createGameWindow():
    numberOfFailedLetterPicks = 1 #Counter for the number of guesses that user made that failed
    maxNumOfTries = len(IMAGE_LIST)  #Maximum number of tries that the user gets, this is the number of images that we have
    numberOfLettersFound = 0  #A counter for the number of letters in the word that have been found

    #It's OK to call global without explicitly decalring it a "global" but not to declare it
    imageElement = sg.Image(data=IMAGE_LIST[0])    #Starting image
    errorText = sg.Text('',size=(33, 1))   #Empty error text that will be used to tell the player that they have already selected this letter in the past
    firstLetter = sg.Text('  ',size=(2, 1),background_color='white')  #Display for the first letter
    secondLetter = sg.Text('  ',size=(2, 1),background_color='white')
    thirdLetter = sg.Text('  ',size=(2, 1),background_color='white')
    fourthLetter = sg.Text('  ',size=(2, 1),background_color='white')
    fifthLetter = sg.Text('  ',size=(2, 1),background_color='white')
    sixthLetter = sg.Text('  ',size=(2, 1),background_color='white')
    seventhLetter = sg.Text('  ',size=(2, 1),background_color='white')
    eighthLetter = sg.Text('  ',size=(2, 1),background_color='white')
    ninthLetter = sg.Text('  ',size=(2, 1),background_color='white')
    tenthLetter = sg.Text('  ',size=(2, 1),background_color='white')    #Display for the 10th letter

    #Global dictionary used to hold all the letters of the alphabet and mark each one as they are selected for the
    #first time so that we can let the player know that they selected the letter in the past
    global LETTER_DICTIONARY

    #Calculate the length of the word so you can show it in the UI
    lengthOfWord = str(len(GAME_WORD))
    
    #Design the layout of the UI
    layout = [
        [sg.Text('Let\'s play a game...',font='comic',text_color='red',key='-bold-')],
        [imageElement],
        [firstLetter,secondLetter,thirdLetter,fourthLetter,fifthLetter,sixthLetter,seventhLetter,eighthLetter,ninthLetter,tenthLetter],
        [sg.Text('There are '),sg.Text(lengthOfWord, size=(2,1)),sg.Text('letters in this word')],
        [sg.Text('Pick a letter'), sg.InputText(),sg.Button('Go')],
        [errorText],
        [sg.Button('Exit')]
    ]

    # Create the Window
    window = sg.Window('A Little Hangman', layout)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):  # if user closes window or clicks cancel
            window.close()
            break
        if event == 'Exit' or event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == 'Go':
            #read the letter the user picked
            pickedLetter = values[1]
            #before we do anything, we check for a single letter
            if checkForASingleLetter(pickedLetter) == False:
                errorText.Update('You can only select one letter at a time',text_color='red')
                continue
            pickedLetter = str(pickedLetter).lower()
            #check if the letter has been picked before, if it has, let the player know
            #but it still counts as an attempt
            if LETTER_DICTIONARY[pickedLetter] == False:
                #If we are in here, it is the first time the letter has been picked because its value is set to false
                #We change the value to true, and from now on we will know that the letter has been previously picked
                LETTER_DICTIONARY[pickedLetter] = True
                errorText.Update('')
            else:
                #The player has selected a letter that they selected in the past
                errorText.Update('Letter had been chosen previously',text_color='red')
                continue
            #Look for all of the occurences of the letter
            #Locations is an array with the place of the letter in the word, for all of the occurences of the letter
            #for example, in the word "hello", for the letter "l" locations will be [2,3] corresponding to the location
            #of "l"
            locations = findLetterInWord(pickedLetter)
            #If locations is empty, they we didnt find the selected letter
            if len(locations) == 0:
                #if we got here we did not guess a letter
                if numberOfFailedLetterPicks == maxNumOfTries:
                    #If we got here, we have reached the maximum number of tries
                    imageElement.Update(data=LOSER_IMAGE)
                    break
                #If we got here then we have not found another letter
                imageElement.Update(data=IMAGE_LIST[numberOfFailedLetterPicks])
                numberOfFailedLetterPicks = numberOfFailedLetterPicks +1
            else:
                #We want to keep track of how many letters we found so far so that we know when we completed the word
                #When the number of letters found = length of the word we have found all the letters in the word and
                # we can end the game
                #Each time locations is not empty, we add it to a running tally of the number of letters found so far
                numberOfLettersFound = numberOfLettersFound + len(locations)
                #update the user interface with the letters to form the word
                #In a for loop we iterate over each item in the array and get the location of the letter in the word
                #For each location, we update the UI with the letter that was picked
                for x in locations:
                    if x == 0:
                        firstLetter.Update(pickedLetter,text_color='black')
                    elif x == 1:
                        secondLetter.Update(pickedLetter,text_color='black')
                    elif x == 2:
                        thirdLetter.Update(pickedLetter,text_color='black')
                    elif x == 3:
                        fourthLetter.Update(pickedLetter,text_color='black')
                    elif x == 4:
                        fifthLetter.Update(pickedLetter,text_color='black')
                    elif x == 5:
                        sixthLetter.Update(pickedLetter,text_color='black')
                    elif x == 6:
                        seventhLetter.Update(pickedLetter,text_color='black')
                    elif x == 7:
                        eighthLetter.Update(pickedLetter,text_color='black')
                    elif x == 8:
                        ninthLetter.Update(pickedLetter,text_color='black')
                    elif x == 9:
                        tenthLetter.Update(pickedLetter,text_color='black')
                if numberOfLettersFound == len(GAME_WORD):
                    #If we got here, we have all the letters and we can show the winner image
                    imageElement.Update(data=WINNER_IMAGE)
        #Every time the loop finishes, we update the UI so that all changes are shown
        window.refresh()


#This function opens the file that contains a list of words
#It is assumed that the words are separated by a single white space, if they are not we will need to change the split
#function to use a differnet separator
#WORD_LIST is a global array that will hold all the words from the file
def loadWordList():
    #declare WORD_LIST as global since it is not a variable in this function, but it's declared outside the function
    #for the entire program to use
    global WORD_LIST
    #open the file with the word list and create the list with words
    with open('wordlist.txt', "r") as wordFile:
        for line in wordFile:
            WORD_LIST.extend(line.split())

    #After we have created WORD_LIST we get its length which is the number of words that we have to choose from
    #We then select a random number in the range of 0 to the length of WORD_LIST - 1
    #The -1 is improtant since the count starts from zero and the function randint is inclusive, which means that the
    #numbers at the edges can also be picked, for example, randInt(0,6) can pick a random number between 0 and 6,
    #but also 0 or 6. In tha case of an array of size 6, picking 6 is bad because it will try and get a value
    #immediately after the end of the array. This will crash the program. The reason is that the count of an array
    #starts at zero and finishes at the length of the array - 1 and that's not good
    #select a random word
    listLen = len(WORD_LIST)
    randNum = random.randint(0,listLen-1)
    return WORD_LIST[randNum]

def findLetterInWord(letter):
    #counter will be used to indicate the location of the letter inside the word
    #For example in the word "python", if we look for the letter "t" counter will have a value of 2 which is
    #the location of the letter "t" in the array, starting from position 0
    counter = 0
    #We use an array for location because a letter can appear in a word more than once
    #for example, in the word "Shahar" h and a appear twice, for the search for the letter h
    #location array will hold two values 1 and 3 indicating all the locations of the letter h in the word
    location = []
    #Cycle over all the letters in the word and try to find an occurence of the letter in the word
    #If the letter was found, add the location of the letter to the "location" array
    #The location array will be used to display the letter in the right place in the user interface
    for i in GAME_WORD:
        if i == letter or str(i).lower() == letter:
           location.append(counter)
        counter = counter + 1
    return location

def splitWord(gameWord):
    #split the word into an array of characters
    return [char for char in gameWord]

def setUp():
    #Use a global reference since these variables are not declared inside this function but outside of it,
    # and can be used anywhere in the code
    global GAME_WORD
    global LOSER_IMAGE
    global WINNER_IMAGE

    gameWord = loadWordList()
    #split the word into its characters and store it in an array called GAME_WORD
    GAME_WORD = splitWord(gameWord)
    #For debugging purposes
    #print(GAME_WORD)
    #Load all images to memory to save time and make the game faster
    loadAllImages()
    LOSER_IMAGE = loadImage('loser')
    WINNER_IMAGE = loadImage('winner')
    #Finally, start the game
    createGameWindow()

if __name__ == '__main__':
    #Indicate to the Python interpreter which function is the starting point
    setUp()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
