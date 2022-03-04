from tkinter import *
from Client import Client
from threading import Thread

# create a window
window = Tk()
# set the title
window.title("Client GUI")
# set the size
window.geometry("800x600")
# set the background color
window.configure(background='lightgray')
# create a label
connect_msg = Label(window, text="enter your name to connect", font=("Arial", 15))
# place the label
connect_msg.place(x=90, y=20)
# input window
name_txt = Entry(window, width=10)
# place the input window
name_txt.place(x=200, y=70)
# start button
cl = Client()
# create a button
connect = Button(window, text="Connect", bg="lightgreen", fg="white",
                 command=lambda: Thread(target=start_client, args=(cl, name_txt.get())).start())
# place the button
connect.place(x=200, y=100)


def sender(mess, message):  # a function to write messages in the textbox
    cl.write(mess)
    message.delete(0, END)


def update_text_box(text_box, m):  # a function to update the textbox
    text_box.config(state=NORMAL)
    text_box.insert(END, m + "\n")
    text_box.see(END)
    text_box.config(state=DISABLED)


def start_client(client, nickname):  # we close the connection window and show the chat window
    connect.destroy()
    name_txt.destroy()
    connect_msg.destroy()
    window.geometry("800x600")

    get_users = Button(window, text="Get Users", bg="lightgreen", fg="white", command=lambda: cl.write("<get_users>"))
    # place the button
    get_users.place(x=400, y=375)

    get_files = Button(window, text="Get files", bg="lightgreen", fg="white", command=lambda: cl.write("<get_files>"))
    # place the button
    get_files.place(x=350, y=375)

    disconnect = Button(window, text="Disconnect", bg="lightgreen", fg="white", command=lambda: cl.write("disconnect"))
    # place the button
    disconnect.place(x=0, y=0, width=800)

    message = Entry(window, width=120)
    # place the input window
    message.place(x=0, y=350)

    text_download = entry = Entry(window, width=15)
    # place the input window
    text_download.place(x=300, y=450)

    download = Button(window, text="Download", bg="lightgreen", fg="white",
                      command=lambda: cl.write("download:" + text_download.get()))
    # place the button
    download.place(x=400, y=450)
    text_box = Text(window, width=80, height=20)
    # place the text box
    text_box.place(x=75, y=25)
    text_box.insert(END, "Connected to server\n")
    # disable the text_box
    text_box.config(state=DISABLED)
    # create a new thread to handle the incoming messages

    # send button
    send = Button(window, text="Send", bg="lightgreen", fg="white", command=lambda: sender(message.get(), message))
    cl.func.append(lambda m: update_text_box(text_box, m))
    send.place(x=720, y=345, width=70)
    client.connect(nickname)
    # disable btn


# start the GUI
window.mainloop()
