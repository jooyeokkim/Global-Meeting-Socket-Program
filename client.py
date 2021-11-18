import socket 
import threading
from tkinter import *
import tkinter.messagebox as msgbox
import tkinter
import tkinter.scrolledtext as scrolledtext
from PIL import ImageTk, Image
import datetime
import sys
from rest import translator


class SampleApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self._frame = None
        self.username = None
        self.language = None
        self.lang_list=[("Korean","ko"), ("English","en"), ("Japanese","ja"), ("Chinese(Simplified)","zh-CN"), ("Chinese(Traditional)","zh-TW"), ("French","fr"), 
            ("Italian","it"), ("Russian","ru"), ("Spanish","es"), ("Filipino","tl"), ("German","de"), ("Vietnamese","vi"), ("Portuguese","pt")]
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()




class StartPage(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        Label(self, text="회의에 참석하신 여러분들을 환영합니다.", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", padx=20, pady=20)

        img = ImageTk.PhotoImage(Image.open("meeting.jpg").resize((400,300), Image.ANTIALIAS))  
        panel = Label(self, image=img)
        panel.photo = img
        panel.pack(pady=15)

        Label(self, text="회의에 표시할 이름을 입력해주세요.", font=('Helvetica', 10, "bold")).pack(side="top")
        input_name = Entry(self, width=30)
        input_name.pack()
        Label(self, text="사용 언어를 선택해주세요.", font=('Helvetica', 10, "bold")).pack(side="top", pady=10)
        lang_var=IntVar()
        for n, lang in enumerate(master.lang_list):
            Radiobutton(self, text=lang[0], value=n, variable=lang_var, command=None).pack()
        Button(self, text="회의 참여", command=lambda: self.validator(master, input_name.get(), lang_var.get())).pack(anchor=SE, padx=10, pady=10)

    def validator(self, master, name, lang):
        if len(name.strip()):
            master.username=name
            master.language=master.lang_list[lang][1]
            master.switch_frame(MeetingRoom)
        else:
            msgbox.showerror("알림","이름을 입력해주세요")
            master.switch_frame(StartPage)      



class MeetingRoom(Frame):
    def __init__(self, master):
        self.message=""
        self.lines=0
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
        Host = 'localhost'
        Port = 9000
        client_sock.connect((Host, Port))
        self.client_sock=client_sock
        print('Connecting to ', Host, Port)
        
        Frame.__init__(self, master)
        Label(self, text="Meeting Room", font=('Helvetica', 18, "bold")).pack(side="top", fill="x", pady=5)
        chatwin = scrolledtext.ScrolledText(self, undo=True)
        chatwin.configure(state='disabled', width=50, height=25, font=('Arial'))
        chatwin.pack(expand=True)
        self.chatwin=chatwin
        input_msg = Entry(self, width=40)
        input_msg.pack(padx=10, pady=10)
        self.input_msg=input_msg
        Button(self, text="전송", command=lambda:self.validator(master)).pack()
        Button(self, text="회의 나가기",
                  command=lambda:self.close_sock(master)).pack(side='bottom', anchor=E, padx=10, pady=10)
        
        thread1 = threading.Thread(target=self.send, args=(master, client_sock, ))
        thread1.start()
        thread2 = threading.Thread(target=self.recv, args=(master, client_sock, ))
        thread2.start()
        
    def validator(self, master):
        msg=self.input_msg.get()
        if len(msg):
            if master.language!="en":
                msg=translator(msg, master.language, "en")
            self.message=master.username+" >"+msg
        else:
            msgbox.showerror("알림", "메시지를 입력해주세요.")

    def send(self, master, client_sock):
        while True:
            if(len(self.message)):
                client_sock.send(bytes(self.message.encode()))
                self.chatwin.configure(state='normal')
                mymsg='['+datetime.datetime.now().strftime('%H:%M:%S')+'] '+master.username+" >"+self.input_msg.get()+'\n'
                self.chatwin.insert(END, mymsg)
                self.lines=self.lines+1
                self.chatwin.tag_add("id"+str(self.lines),str(self.lines)+".0",str(self.lines)+"."+str(len(mymsg)))
                self.chatwin.tag_config("id"+str(self.lines), foreground="red")
                self.chatwin.configure(state='disabled')
                self.input_msg.delete(0,END)
                self.message=""

    def recv(self, master, client_sock):
        try:
            while True:
                recv_data = client_sock.recv(1024).decode()
                find_arrow = recv_data.find(">")
                header=recv_data[0:find_arrow+1]
                message=recv_data[find_arrow+1:]
                if master.language!="en":
                    message=translator(message, "en", master.language)
                print("translated")
                self.chatwin.configure(state='normal')
                self.chatwin.insert(END, header+message+'\n')
                self.lines=self.lines+1
                self.chatwin.configure(state='disabled')
        except:
            print("recv 종료")

    def close_sock(self, master):
        print("연결 종료")
        self.client_sock.close()
        master.destroy()





if __name__ == "__main__":
    app = SampleApp()
    app.title("Global Meeting")
    app.mainloop()