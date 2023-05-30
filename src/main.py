import os
import sys
import requests
import threading
import traceback
from yt_dlp import YoutubeDL, utils
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext, Text
import sv_ttk
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

thepath = os.path.realpath(os.path.expanduser("~/Downloads")+'/kaicheng music')
task = dict()
n = 0
#LINK https://www.youtube.com/watch?v=wiHYx9NX4DM


def error_handling(func):
    def err_inner(*args,**kwargs): #kwargs mean any other args avai
        try:
            func(*args,**kwargs)
        except Exception as error:
            table.item(args[1],tags=('red',))
            fullerror = "".join(traceback.TracebackException.from_exception(error).format())
            displayhelp(f'❌ {error}',fullerror,True)
            traceback.print_exception(type(error), error, error.__traceback__, file = sys.stderr)
        else:
            print('[safe] iid=',args[1])
            table.item(args[1],tags=('green',))
    return err_inner

def insertquery(x=None,query=None):
    global n
    n += 1
    url = False
    if query is None:
        query = inputvalue.get()
    inputvalue.set("")
    entry.focus_set()
    if query == None or query == '': #invalid
        return displayhelp('Invalid Input!','Please enter youtube url or a specific search string.\n\nTo download playlist, please enable playlist mode.')
    elif ':' in query or '/' in query: #url
        if 'youtu' not in query: 
            return displayhelp('Invalid Input!','Only youtube url is supported.')
        else:
            url = True
            table.insert("", tk.END, values=(f"🔗 {query}",), tags=('default'),iid=n)
    else:
        table.insert("", tk.END, values=(query,), tags=('default'),iid=n)
    task[n] = query
    thread = threading.Thread(target= downloadyoutube, args=(task[n],n,url))#QQ yt
    thread.start()       

@error_handling
def downloadyoutube(arg,iid,url):
    table.item(iid,tags=('cyan',))
    with YoutubeDL({'format': 'bestaudio','outtmpl': thepath+'\%(title)s.mp3','--windows-filenames': True,'nocheckcertificate': True,'ignoreerrors': False,'logtostderr': False,'default_search': 'auto','source_address': '0.0.0.0'}) as ydl:
        if url:
            result = ydl.extract_info(arg, download=True)
            if playlistmode.get() == False:
                arg = result['requested_downloads'][0]['_filename'] 
        else:
            result = ydl.extract_info(f"ytsearch:{arg}", download=True)['entries'][0:1][0]
    #renaming file
    if playlistmode.get() == False:
        filename = f"{result['requested_downloads'][0]['_filename']}"
        if os.path.exists(f'{thepath}\{arg}.mp3'):
            print('[exist] skipped')
        else:
            os.rename(filename, f'{thepath}\{arg}.mp3')

def displayhelp(title='About Us', content=None, error=False):
    helpui = tk.Toplevel(root)
    helpui.title("KaiCheng YT downloader")
    helpui.geometry('400x600')
    helpui.attributes('-alpha', 0.94)
    displayframe = ttk.LabelFrame(helpui, text=title, width=350, height=200)
    displayframe.place(x=20, y=20)
    if content == None:
        ttk.Label(helpui, text='2023 @ KaiCheng', font=("Bahnschrift SemiBold", 14), foreground = "#E6E6E6").place(x=87,y=90)
        ttk.Label(helpui, text='Made possible by yt-dlp', font=("Consolas", 10), foreground = "grey").place(x=75,y=150)
    else:
        T = Text(helpui, height = 7, width = 29, wrap=tk.WORD, bd=0, font =("consolas", 10))
        T.place( x=35, y=60)
        if error:
            T.insert(tk.END,f"{title}\n\nWe apologize for the inconvinience caused.\n\n" )
            displayframe.config(labelwidget=ttk.Label(helpui, text='Error', font=("Consolas", 10), foreground = "#C70039"), text=None)
        T.insert(tk.END,content)
    ttk.LabelFrame(helpui, text='Download Status', width=350, height=350).place(x=20, y=235)
    ttk.Label(helpui, text='Error', font=("Consolas", 10), foreground = "#C70039").place(x=47,y=300)
    ttk.Label(helpui, text='Done', font=("Consolas", 10), foreground = "#1ABC9C").place(x=47,y=400)
    ttk.Label(helpui, text='Downloading', font=("Consolas", 10), foreground = "#2E86C1").place(x=47,y=500)
    ttk.Label(helpui, text='Error has occured, \nunable to download\nmedia you want', font=("Consolas", 9), foreground = "white").place(x=150,y=300,width=200)
    ttk.Label(helpui, text='Your song has\ndownloaded and saved', font=("Consolas", 9), foreground = "white").place(x=150,y=400,width=200)
    ttk.Label(helpui, text='Downloading\ntask is ongoing', font=("Consolas", 9), foreground = "white").place(x=200,y=495,width=200)
    entry.focus_set()

def changelocation():
    global thepath
    thepath = filedialog.askdirectory(title='select location to save your music') 
    pathlabel.config(text=f'📂 {thepath}')
    entry.focus_set()

def startimport():
    global importui
    importui = tk.Toplevel(root)
    importui.title("Instruction")
    importui.geometry('400x540')
    importui.attributes('-alpha', 0.94)
    ttk.LabelFrame(importui, text='Batch Downloader', width=350, height=500).place(x=20, y=20)
    ttk.Label(importui, text='Please follow the instruction\nbelow: \n\n1. The file import must be \n   a txt file\n\n2. The TITLE of the music \n   you wanted to download\n   are seperated by lines\n\n3. We will download your\n   one by one line\n   follow the sequence\n   (max: 100)', font=("Consolas", 10), foreground = "#E6E6E6").place(x=40,y=80)
    ttk.Button(importui, text='Import txt',style="Accent.TButton", command=importtxt,cursor="hand2").place(x=35, y=450, width=150, height=50)
    ttk.Button(importui, text='Example >', command=lambda: importui.geometry('800x540'),cursor="hand2").place(x=205, y=450, width=150, height=50)
    ttk.LabelFrame(importui, text='Example of TXT file', width=350, height=370).place(x=400, y=20)
    ttk.Label(importui, text='song1\nsong2\nsong3\nsong4\nsong5\nsong6\nsong7\nsong8\nsong9\nsong10\nsong11\nsong12\nsong13\n\n\n*We will download the song\nin text file from song1\nto song13*', font=("Consolas", 10), foreground = "#E6E6E6").place(x=415,y=70)
    ttk.Separator(importui).place(x=415,y=389, width=300)

def importtxt():
    global n
    error = False
    txtpath = filedialog.askopenfilename(title='select location') 
    with open(txtpath, "r", encoding='utf-8') as f:
        importquery = f.readlines()
        print(importquery)
    importui.destroy()

    if not importquery:
        return displayhelp('Invalid file','The txt file provided is empty')
    for query in importquery:
        n += 1
        insertquery(query = query.replace('\n',''))


root = tk.Tk()
root.title("KaiCheng YT downloader")
sv_ttk.set_theme("dark")
root.geometry ("930x470")
root.attributes('-alpha', 0.94)
root.tk.call('tk','scaling','2.0') #DPI
s = ttk.Style()
#input
frame1 = ttk.LabelFrame(root, text='Enter link / Music Title', width=450, height=200).place(x=20, y=20)
inputvalue = tk.StringVar()
entry = ttk.Entry(frame1, textvariable = inputvalue, font=('Consolas', 8))
entry.place (x=40, y=70, width=400, height=50)
entry.focus_set()
entry.bind('<Return>', insertquery)
playlistmode = tk.BooleanVar() 
ttk.Checkbutton(root, text=" Playlist Mode", style="Switch.TCheckbutton", command=lambda: displayhelp('Playlist mode','1. Private playlist, shorts collection and youtube mix is not accepted.\n\n2. Number of video in playlist should not exceed 100\n\n'), variable = playlistmode).place(x=60,y=152, width=300)
ttk.Button(root, text='Go ⤓', command=insertquery,style="Accent.TButton",cursor="hand2").place(x=338, y=147, width=100, height=50)
#table
frame = tk.Frame(root)
frame.place(x=500,y=32,width=400, height=408)
s.configure('Treeview', rowheight=40)
table = ttk.Treeview(frame, columns=("Music"), height=10, show='headings', selectmode='extended',cursor="hand2")
table.place(x=0,y=0)
table.heading("Music", text="Music", anchor=tk.CENTER, command=displayhelp)
table.column("Music", anchor=tk.CENTER, width=200)
table.tag_configure('default', font=("consolas", 10, 'bold'))
table.tag_configure('red', foreground="#C70039", font=("consolas", 10, 'bold'))
table.tag_configure('green',foreground="#1ABC9C", font=("consolas", 10, 'bold'))
table.tag_configure('cyan',foreground="#2E86C1", font=("consolas", 10, 'bold'))
scrollbar = ttk.Scrollbar(frame)
scrollbar.pack(side="right", fill="y")
table.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=table.yview)
table.pack(expand=True, fill="both")
ttk.Button(root, text='Import txt  📄', command=startimport,cursor="hand2").place(x=720, y=382, width=150, height=50)
#setting
frame2 = ttk.LabelFrame(root, text='Download option ', width=450, height=200).place(x=20, y=240)
ttk.Button(root, text='About  \u24D8', command=displayhelp,cursor="hand2").place(x=290, y=300, width=150, height=50)
ttk.Button(root, text='Change location',style="Accent.TButton", command=changelocation,cursor="hand2").place(x=50, y=300, width=180, height=50)
pathlabel = ttk.Label(root, text=f'📂 {thepath}', font=("consolas", 9), foreground = "white",cursor="hand2")
pathlabel.place(x=60, y=380, width=350, height=30)
pathlabel.bind("<Button-1>", lambda e: os.startfile(thepath))
print('[thepath]',thepath)
# changelocation()
root.mainloop()