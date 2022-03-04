from tkinter import *
from Client import Client
from threading import Thread

# create a window
window = Tk()
# set the title
window.title("Client GUI")
# set the size
window.geometry("300x200")
# set the background color
window.configure(background='lightgray')
# create a label
connect_msg = Label(window, text="enter your name to connect:", font=("Arial", 15))
# place the label
connect_msg.place(x=30, y=20)
# input window
name_txt = Entry(window, width=40)
# place the input window
name_txt.place(x=30, y=70)
# start button
cl = Client()
# create a button
connect = Button(window, text="Connect", bg="lightgreen", fg="white",
                 command=lambda: Thread(target=start_client, args=(cl, name_txt.get())).start())
# place the button
connect.place(x=45, y=100, width=200)


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
    window.geometry("500x500")
    window.resizable(False,False)

    get_users = Button(window, text="Get Users", bg="lightgreen", fg="white", command=lambda: cl.write("<get_users>"))
    # place the button
    get_users.place(x=30, y=400, width=100)

    get_files = Button(window, text="Get files", bg="lightgreen", fg="white", command=lambda: cl.write("<get_files>"))
    # place the button
    get_files.place(x=30, y=450, width=100)

    disconnect = Button(window, text="Disconnect", bg="lightgreen", fg="white", command=lambda: cl.write("disconnect"))
    # place the button
    disconnect.place(x=0, y=0, width=500)

    message = Entry(window, width=70)
    # place the input window
    message.place(x=0, y=370)

    text_download = entry = Entry(window, width=20)
    # place the input window
    text_download.place(x=300, y=400)

    download = Button(window, text="Download", bg="lightgreen", fg="white",
                      command=lambda: cl.write("download:" + text_download.get()))
    # place the button
    download.place(x=430, y=400, width=70)
    text_box = Text(window, width=62, height=20)
    # place the text box
    text_box.place(x=0, y=27)
    text_box.insert(END, "Connected to server\n")
    # disable the text_box
    text_box.config(state=DISABLED)

    # send button
    send = Button(window, text="Send", bg="lightgreen", fg="white", command=lambda: sender(message.get(), message))
    cl.func.append(lambda m: update_text_box(text_box, m))
    send.place(x=430, y=368, width=70)
    client.connect(nickname)
    # disable btn


# start the GUI
window.mainloop()
