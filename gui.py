from Amadeus import getOutput, getTranslation
from AmadeusSpeak import generateVoice, play_sound
from tkinter import *
from tkinter import ttk, PhotoImage

#Pygame 

def makeWindow():
    window = Tk()                       #Main Window
    window.title("Amadeus")
    window.geometry('640x640')  
    window.iconbitmap('Images/MakiseKurisu.ico')

    image_path= PhotoImage(file="Images/amadeusImage.gif")         #BG
    bg_image = Label(window, image=image_path)
    bg_image.place(x=0, y=0, relheight=1, relwidth=1)

    output_string = StringVar()
    output_string.set("Amadeus is waiting...")
    translated_string = StringVar()
    translated_string.set("No message yet")

    def send_message(): 
        user_input = entry_string.get()
        response = getOutput(user_input)
        translated = getTranslation(response)

        generateVoice(response)
        output_string.set(response)
        translated_string.set(translated)
    
    def on_send():
        send_message()
        input_frame.after(20, play_sound)


    input_frame = ttk.Frame(master=window)          #This contains entry_frame and button
    entry_string = StringVar()
    entry = ttk.Entry(master=input_frame, textvariable=entry_string)
    button = ttk.Button(master = input_frame, text = "Send", command=on_send)
    entry.pack(side='left')
    button.pack(side='left')
    input_frame.pack()

    chat_log = ttk.Label(
        window, 
        textvariable=output_string,
        wraplength=450)

    chat_log.pack(pady=100)

    translated_log = ttk.Label(
        window, 
        textvariable=translated_string,
        wraplength=450)
    
    translated_log.pack(pady=5)


    window.mainloop()


