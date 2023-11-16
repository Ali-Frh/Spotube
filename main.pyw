import sys
from PyQt5.QtWidgets import QApplication, QDialog, QSlider, QMainWindow, QListWidget, QListWidgetItem, QAbstractItemView, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi
import threading
import newcore as core
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QUrl, QSize, QThread, pyqtSignal

from ytsearch import YoutubeSearch



import json

# thread1 = threading.Thread(target=worker, args=("Thread 1",))


player = None
playing = False
paused = False


import time

import yt_dlp as youtube_dl
# from youtube_search import YoutubeSearch
import os
import re




# def humantime(milliseconds):
#     seconds = int((milliseconds / 1000) % 60)
#     minutes = int((milliseconds / (1000 * 60)) % 60)
#     hours = int((milliseconds / (1000 * 60 * 60)) % 24)

#     return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

def humantime(milliseconds):
    seconds = int((milliseconds / 1000) % 60)
    minutes = int((milliseconds / (1000 * 60)) % 60)

    return "{:02d}:{:02d}".format(minutes, seconds)

import os

class MyDialog(QDialog):
    

    def dl(self,link, title=""):
        try:
            # Define the options
            ydl_opts = {
                'format': 'bestaudio/best',
                'progress_hooks': [self.progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                    'ffmpeg_location': self.ffmpeg_path,  # Specify the path to ffmpeg executable
                # 'outtmpl': r'downloads\%(title)s.%(ext)s', 
                'outtmpl': 'downloads\/'+ core.coolname(title) + r'.%(ext)s', 


            }

            if self.proxyenabled:
                ydl_opts[ "proxy" ] = self.proxyurl

            # Specify the video URL
        #    video_url = 'https://www.youtube.com/watch?v=eO23weLKT8M'
            video_url = link

            # Create a YouTubeDL object with the options
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                # Download the audio
                try:
                    t = ydl.download([video_url])
                    print(t,"\n",title)
                #os.rename("downloads/"+title+".mp3", "downloads/"+coolname(title) + ".mp3")
                    return True
                except Exception as er:
                    self.alert("Err while downloading!"  +   str(er))
        except Exception as er:
            self.alert("Error while downloading!"  +   str(er))
            return False

    def set_state_durr(self, text, durr, after):
        self.state.setText(text)
        time.sleep(durr)
        self.state.setText(after)



    def set_state(self,text,durr=-1,after=""):
        if durr == -1:
            self.state.setText(text)
        else:
            t = threading. Thread(target=self.set_state_durr, args=(text,durr,after))
            t.start()

    def search(self, term,res=10):
        query = term
        proxy = None
        if self.proxyenabled:
            proxy =  self.proxyurl
            print("proxy:",proxy)
        
        results = YoutubeSearch(query, max_results=res, proxy=proxy).to_dict()
        #  title = video['title']
        # video_id = video['id']
        return results


    def progress_hook(self, data):
        print("status:",data["status"])
        if data['status'] == 'downloading':
            total_size = data.get('total_bytes')
            downloaded_bytes = data.get('downloaded_bytes')
            if total_size and downloaded_bytes:
                percentage = (downloaded_bytes / total_size) * 100
                self.percentage = percentage
                print("perc",percentage)
                if int(percentage) == 100:
                    self.set_state(f"Download Done, Converting to MP3...")
                else:                  
                    self.state.setText(f"Downloading {int(percentage)}%")
                #print(percentage)
                # self.progress_signal.emit(percentage)

    def stucker(self,filename,forfirst):
        i = 0
        while i < 100:
            z = os.path.exists("downloads/"+filename+".mp3")
            zz = os.path.exists("downloads/"+filename+".webm")
            
            if self.downloadfailed == True:
                self.downloadfailed = False
                break
                

            if z and not zz:
                print("its donne :D")
                self.set_state("Conversion Done, Ready to Play. ",2,"Playing")
                i = 100
                if forfirst:
                    self.playing = False
                    self.test(True)
            else:
                time.sleep(1)
            i = i + 1
            


    def show_progress(self, percentage):
        self.state.setText(f"Downloading {int(percentage)}")


    def test(self, skipdl=False):
        if not os.path.exists(self.ffmpeg_path):
            self.alert("Dude, Please set your ffmpeg path in settings section (the gear icon)\nIts Used for some conversion stuff and its vital.")
            return
        if self.playlist.rowCount() == 0:
            self. alert("There is no track dude! Add some songs first.")
            return

        # self.playing=False
        if self.playing:
            if self.paused:
               self.player.play()
               self.set_state("Playing")
            else:
               self.player.pause()
               self.set_state("Paused")
            
            self.paused = not self.paused
            # pass
        else:
            if skipdl == False:
                z = self.getitem(0,forfirst=True)
          #  else:
               # self.player=QMediaPlayer()
            try:
                if not os.path.exists("downloads/"+ core.coolname(self.playlist.item(0,0).text()) + ".mp3"):
                    self.set_state("Downloading Song...")
                    return
            except:
                return


            print("-")
            file_list = []
            extension = ""
            try:
                fname = self.playlist.item(0,0).text()
            except:
                print("Last Item")
                self.passtime.setText("00:00:00")
                self.currentname.setText("Noting.")
                self.seek.setRange(0,0)
                return
            path = "downloads/" + core.coolname(fname) + ".mp3"
            # return None  # File not found
            

            print(path)


            media_content = QMediaContent(QUrl.fromLocalFile(path))
            
            self.player.setMedia(media_content)

            self.player.positionChanged.connect(self.seek_position)
            self.player.durationChanged.connect(self.seek_durr)
            self.player.play()

            self.set_state("Playing")

            self.got_next= False
            self.eightypercentdurr = self.player.duration() * 0.8
            self.playing = True
            title = os.path.splitext(os.path.basename(path))[0]
            self.currentname.setText(title)
            self.player.durationChanged.connect(self.wholetimesetter)
            # self.wholetime.setText(humantime (self.player.duration()))
    
    def wholetimesetter(self, timez):
        self.wholetime.setText(humantime (timez))
    


    def select_full_row(self, row, column):
        self.playlist.selectRow(row)

    def togglelist(self):
        if self.playlistadd:
            icon = QIcon()
            icon.addPixmap(QPixmap('icon/dellist.png'))
            self.listtoggle.setIcon(icon)
        else:
            icon = QIcon()
            icon.addPixmap(QPixmap('icon/addlist.png'))
            self.listtoggle.setIcon(icon)
        self.playlistadd = not self.playlistadd

    def save_settings(self):
        z = open("settings.json", "w")
        data = {}
        data["proxyenabled"] = self.setting.proxyenabled.isChecked()
        data["ffmpeg_path"] = self.setting.ffmpegpath.text()
        self.ffmpeg_path = self.setting.ffmpegpath.text()
        # print(d)
        self.proxyenabled = data["proxyenabled"]
        data["proxyurl"] = self.setting.proxyurl.text()
        print("save",data)
        self.proxyurl = data["proxyurl"] 

        z.write(json.dumps( data ))
        z.close()



    def load_settings(self):
        if os.path.exists("settings.json"):
            try:
                z = open("settings.json", "r")
                x = z. read ()
                z . close ()
                data = json.loads(x)
                self.proxyenabled = data["proxyenabled"]
                self.ffmpeg_path = data["ffmpeg_path"]
                self.proxyurl = data["proxyurl"]
                print(self.proxyurl)
            except:
                print("looks like config is broken, making one")
                os.remove("settings.json")
                self.load_settings()

        else:
            print("making conf file")
          #  if self.proxyenabled:
          #      self.setting.proxyenabled.setChecked(True)
          #  self.setting.proxyurl = self.proxyurl
            # self.save_settings()
            z = open("settings.json", "w")
            data = {}
            data["proxyenabled"] = False
            data["proxyurl"] = ""
            data["ffmpeg_path"] = "ffmpeg"
            print("save",data)
            z.write(json.dumps( data ))
            z.close()
      #  print("load",data)
        
        
    def settingssave(self):
        self.save_settings()
        self.setting.close()

    def settingsopen(self) :
        self.load_settings()
        self. setting = QDialog()
        loadUi("setting.ui", self.setting)
        self.setting.proxyurl.setText(self.proxyurl)
        if self.proxyenabled:
            self.setting.proxyenabled.setChecked(True)
        self.setting.ffmpegpath.setText(self.ffmpeg_path)
        self.setting.savesettings.clicked.connect(self.settingssave)
        self.setting.exec_() 

    def __init__(self):
        self.player = None
        self.playing = False
        self.paused = False
        self.media = None
        self.ffmpeg_path = ""  
        self.ytres = []
        self.got_next=False
        self.tracklist = []
        self.eightypercentdurr = 0
        self.player = QMediaPlayer()
        self.playlistadd = True
        self.ismute = False
        self.proxyurl = ""
        self.proxyenabled = False
        self.downloadfailed = False

        self.load_settings()
        super(MyDialog, self).__init__()

        # Load the UI file
        loadUi('main.ui', self)

        self.setWindowIcon(QIcon('icon/logo.png'))

        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.Dialog | Qt.WindowTitleHint)

        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.WindowStaysOnBottomHint)
        self.playlist.cellDoubleClicked.connect(self.playitem)
    #    self.playlist.setDragDropMode(QAbstractItemView.InternalMove)
        
        self.playlist.cellClicked.connect(self.select_full_row)

        # Connect signals to slots (optional)
        self.plus.clicked.connect(self.button_clicked)
        self.button.clicked.connect(self.testcrap)
        self.up.clicked.connect(self.moveup)
        self.down.clicked.connect(self.movedown)
        self.mute.clicked.connect(self.muteornot)
        
        self.listtoggle.clicked.connect(self.togglelist)

        self.settinggs.clicked.connect(self.settingsopen)



        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        # self.player.positionChanged.connect(self.seek_position)
        # self.player.durationChanged.connect(self.seek_durr)
        self.playlist.setEditTriggers(QTableWidget.NoEditTriggers)

        # self.button.hide()
        self.playorpause.clicked.connect(self.test)
        self.savebtn.clicked.connect(self.save)
        self.loadbtn.clicked.connect(self.load)
        self.stop.clicked.connect(self.stopshit)
        self.next.clicked.connect(self.nextshit)
        self.prev.clicked.connect(self.prevshit)
        self.delbutton.clicked.connect(self.delete)
        self.info.clicked.connect(self.infodialog)
        #self.seek = QSlider(PyQt5.Orientation.Horizontal)
        try:
            self.seek.setRange(0, self.player.get_length() // 1000)  # Set the range in seconds
        except:
            self.seek.setRange(0, 100)
        self.seek.sliderMoved.connect(self.on_seek)
       # self.setCentralWidget(self.seek)

        self.playlist.setColumnCount(3)
        self.playlist.setColumnHidden(2, True)
        header = self.playlist.horizontalHeader()
        header.setStretchLastSection(True)
        self.playlist.setHorizontalHeaderItem(0, QTableWidgetItem("Title"))
        self.playlist.setHorizontalHeaderItem(1, QTableWidgetItem("Duration"))
        self.playlist.setColumnWidth(0, 210)
        
        self.playorpause.setDefault(True)

    def refresh_data(self):
        if self.addnew.query.text() !=  "":
            self.addnew.results.hide()
            self.addnew.loading.show()
            #  print("searching for",addnew.query.text())
            try:
                self.ytres = self. search(self.addnew.query.text())
                items = []
                # print(ytres)
                row = 0
                for i in self.ytres:
                    self.addnew.results.setItem(row, 0, QTableWidgetItem(i["title"]))
                    self.addnew.results.setItem(row, 1, QTableWidgetItem( i["duration"] ))
                    row = row +  1
                self.addnew.loading.hide()
                self.addnew.results.show()
            except Exception as e:
                self.alert("Bruh, there was a problem during search!\n\n"+str(e))
                self.addnew.loading.hide()


    def done(self):            
        selected_items = self.addnew.results.selectedItems()
        item_indices = [(item.row(), item.column()) for item in selected_items]
        # print("Selected Item Indices:", item_indices)
        tracks = []
        for i in item_indices:
            tracks.append(i[0])
        tracks = list(set(tracks))
        print(tracks)
        # print()
        self.add_to_list(self.ytres, tracks)
        self.addnew. close()

    def button_clicked(self):
        print("Button clicked!")
       # def open_new_window(self):
        self.addnew = QDialog(self)
        loadUi("addnew.ui", self.addnew)
        self.addnew.setWindowTitle("Add New Track")
        self.addnew.query.setText("")
        self.addnew.search.clicked.connect(self.refresh_data)
        self.addnew.done.clicked.connect(self.done)

        self.addnew.results.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set the table dimensions
        self.addnew.results.setRowCount(10)
        self.addnew.results.setColumnCount(2)
        self.addnew.loading.hide()
        self.addnew.results.hide()
        self.addnew.results.setSelectionMode(QAbstractItemView.MultiSelection)
        self.addnew.results.setColumnWidth(0, 170)  # Set width of column 0 to 100 pixels
        self.addnew.results.setColumnWidth(1, 10)  # Set width of column 1 to 200 pixels
        # addnew.results.resizeColumnToContents(2)
        header = self.addnew.results.horizontalHeader()
        header.setStretchLastSection(True)
        self.addnew.results.setHorizontalHeaderItem(0, QTableWidgetItem("Title"))
        self.addnew.results.setHorizontalHeaderItem(1, QTableWidgetItem("Duration"))
        self.addnew.exec_()

    def on_media_status_changed(self,status):
        if status == QMediaPlayer.EndOfMedia:
            # Song has reached its end
            print("Song has finished playing")
            if self.playlistadd:
                self.moverow(0,self.playlist.rowCount())
            else:
                self.playlist.removeRow(0)
            self.playing = not self.playing
            self.test()


    def stopshit(self):
        self.player.stop()
        self.playing = False

    def nextshit(self):
        if self.playlist.rowCount() == 1:
            self. alert("Have you seen any other tracks? Which drug are you high on?")
            return
        if self.playlist.rowCount() == 0:
            self. alert("There is no track dude! Which drug are you high on?")
            return

        self.player.stop()
        if self.playlistadd:
            self.moverow(0,self.playlist.rowCount())
        else:
            self.playlist.removeRow(0)
        self.playing = False
        self.test()

    def prevshit(self):
        
        if self.playlistadd:
            if self.playlist.rowCount() == 1:
                self. alert("Have you seen any other tracks? Which drug are you high on?")
                return
            if self.playlist.rowCount() == 0:
                self. alert("There is no track dude! Which drug are you high on?")
                return

            self.player.stop()
           
          #  self.playlist.setRowCount(row + 1)

            self.playlist.insertRow(0)
            
            self.moverow(self.playlist.rowCount()-1, 0)
            self.playlist.removeRow(self.playlist.rowCount()-1 )
            self.playing = False
            self.test()
        else:
            # do nothing
            self.alert("Bro, In current mode, we dont keep previous track, you should change your playlist mode first.")
            #self.playlist.removeRow(0)
        
    def alert(self, text):
        z = QMessageBox()
        z.setText(text)
        z.setWindowTitle("Alert")
        z.exec_()

    def infodialog(self):
        text = "Spotube v1.0 \nCreated with Love by ALi Frh\n \n I would be thrilled if you Star this project in github."
        z = QMessageBox()
        z.setText(text)
        z.setWindowTitle("Info")
        z.addButton(QMessageBox.Ok)
        z.setDefaultButton(QMessageBox.Ok)
        # z.addButton("Project's Github")
        # z.addButton("My Github")
        button = QPushButton("Project's Github")
        z.addButton(button, QMessageBox.ButtonRole.ActionRole)
        button = QPushButton("My Github")
        z.addButton(button, QMessageBox.ButtonRole.ActionRole)

        t = z.exec_()
        import webbrowser
        if t == 0:
            webbrowser.open("https://github.com/Ali-Frh/Spotube")
        elif t == 1:
            webbrowser.open("https://github.com/ALi-Frh")
        else:
            pass
        # print(t)

        # self.alert("https://google.com")

    def moverow(self, row1, row2):
        print("moving",row1,row2)
        z = self.playlist.rowCount()
        self.playlist.setRowCount(z+1)
        for i in range(0,3) :
            self.playlist.setItem(row2, i, QTableWidgetItem( self.playlist.item(row1,i).text() ))
        self.playlist.removeRow(row1)


    def switchrows(self,row1,row2):
        temp = [self.playlist.item(row1,0).text(),self.playlist.item(row1,1).text(),self.playlist.item(row1,2).text()  ]
        for i in range(0,3) :
            self.playlist.setItem(row1,i,QTableWidgetItem(self.playlist.item(row2,i).text()))

        for i in range(0,3) :
            self.playlist.setItem(row2, i, QTableWidgetItem( temp[i] ))

    def muteornot(self):
        if self.ismute:
            self.player.setMuted(False)
            self.set_state("Unmuted")
            self.ismute = False
        else:
            self.player.setMuted(True)
            self.set_state("Muted")
            self.ismute = True

    def moveup(self):
        z = self.playlist.selectedItems()
        print(z)
        selected_rows = set()
        for item in self.playlist.selectedItems():
            selected_rows.add(item.row())
        if len(selected_rows) > 1:
            self.alert("just select one row at a time!")
        elif len(selected_rows) == 0:
            self.alert("Select a row first!")
        else:
            row = list(selected_rows)[0]
            if row == 0:
                self.alert("You cant move playing item!")
            elif row == 1:
                self.alert("You cant move item to the playing place, use Next Button Instead!")
            else:
               # temp = [self.playlist.item(row,0),self.playlist.item(selected_rows[0],1),self.playlist.item(selected_rows[0],2)]
                self.switchrows(row,row-1)
                self.playlist.setCurrentCell(row-1, 0)
                


        # print(butt)/

    def movedown(self):
        z = self.playlist.selectedItems()
        selected_rows = set()
        for item in self.playlist.selectedItems():
            selected_rows.add(item.row())
        print(list(selected_rows)[0])
        if len(selected_rows) > 1:
            self.alert("just select one row at a time!")
        elif len(selected_rows) < 1:
            self.alert("Select a row first!")
        else:
            row = list(selected_rows)[0]
            if row+1 == self.playlist.rowCount():
                # self.alert("You cant move playing item!")
                self.alert("Last Item cant go deeper than this")
            elif row == 0:
                self.alert("You cant move currently playing item deeper, use Next Button Instead!")
            else:
               # temp = [self.playlist.item(row,0),self.playlist.item(selected_rows[0],1),self.playlist.item(selected_rows[0],2)]
                self.switchrows(row+1,row)
                self.playlist.setCurrentCell(row+1, 0)

    def get_next(self):
        self.getitem( 0 + 1 )
        self.got_next = True

    def seek_position(self, position):
        # print(position * 1)
        seek_position_ms = position * 1000        
        self.passtime.setText(humantime(position))
        self.seek.setValue(position)

        if position > self.eightypercentdurr and not self.got_next:
            print("getting next now bruh")
            self.get_next()
        
    def seek_durr(self,duration):
        self.seek.setMaximum(duration)
    
    def on_seek(self, position):
        # Seek to the desired position
        self.player.setPosition(position)

    def testcrap(self):
        msg_box = QMessageBox()
        disclaimer = """Disclaimer:

This button is provided for demonstration purposes only and does not perform any intended or functional action. It is purely a simulated representation of a button for instructional or illustrative purposes. Pressing or interacting with this button will not result in any actual action, transaction, or modification of data.

Please be aware that the mock button is not connected to any backend or functionality, and its visual appearance or behavior does not reflect any intended functionality of an actual button. It is meant to be used solely for testing, training, or educational purposes.

By using or interacting with this mock button, you acknowledge and understand that it is not intended to perform any action or provide any real-world functionality. Any expectations or assumptions about the button's behavior or consequences are unfounded and should not be considered valid.

Furthermore, the owner or provider of this software or interface shall not be held liable for any misunderstanding, misuse, or misinterpretation of the mock button or any associated actions.

Please exercise caution and refrain from interacting with the mock button under any mistaken belief that it will perform any actual action.

If you have any questions or concerns, please contact the software provider or administrator for clarification.

Did you read the whole thing ? get a job dude.

"""
        msg_box.setText(disclaimer)
        msg_box.setWindowTitle("Message Box")
        msg_box.setIcon(QMessageBox.Information)
        
        # Add buttons to the message box
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        # Execute the message box and get the user's choice
        choice = msg_box.exec_()

    
    # progress_signal = pyqtSignal(float)

    
    # Create and start multiple threads
    # for i in range(5):
    #     thread = threading.Thread(target=worker, args=(i,))
    #     thread.start()

    # # Wait for all threads to complete
    # main_thread = threading.current_thread()
    # for thread in threading.enumerate():
    #     if thread is not main_thread:
    #         thread.join()








    def getitem(self,item=0,forfirst=False):
        if self.playlist.rowCount() > item:
            title = self.playlist.item(item,0).text()
            if os.path.exists("downloads/"+ core.coolname(title) + ".mp3"):
                self.set_state("Loading Cached Song",2,"Playing ")
                print("We Have it Already, Skip Download.")
                return
            print("downloading", )
            self.set_state("Downloading Song")
            # threading.Thread(target=self.worker, args=())
            args = ("https://youtube.com/watch?v="+self.playlist.item(item,2).text(), self.playlist.item(item,0).text())
            self.thread = threading.Thread(target=self.dl, args=args)
            self.thread.start()
        # if forfirst:
            args = (core.coolname(self.playlist.item(item,0).text()), forfirst)
            self.stuck = threading.Thread(target=self.stucker, args=args)
            self.stuck .start()
            #  DownloadThread(url)
            # self.thread.progress_signal.connect(self.show_progress)
            
            # self.thread.finished.connect(self.download_finished)
            # self.thread.start()


    def closeEvent(self, event):
        # Stop and release the media player when closing the window
        self.player.stop()
      #  self.player.release()
        event.accept()
    
    # def update_playlist(self):

    def playitem(self, item):
        #temp = self.
        print(item)



    def add_to_list(self,vids,which):
        row = self.playlist.rowCount()
        self.playlist.setRowCount(row + len(which))
        print(row,len(which))

        for i in range(0,len(which)):
            #self.tracklist.append(vids[which[i]])
            vid = vids[which[i]]
            self.playlist.setItem(row, 0, QTableWidgetItem(vid["title"]))
            self.playlist.setItem(row, 1, QTableWidgetItem(vid["duration"]))
            self.playlist.setItem(row, 2, QTableWidgetItem(vid["id"]))
            row = row + 1
            #print(self.tracklist)
            print("added",vid["title"])
        
        # for i in self.tracklist:
        #     self.playlist.setItem(row, 0, QTableWidgetItem(i["title"]))
        #     self.playlist.setItem(row, 1, QTableWidgetItem(i["duration"]))
        #     self.playlist.setItem(row, 2, QTableWidgetItem(i["id"]))

    def save(self):
        # import json
        all_items = []
        print("="*10)
        for row in range(self.playlist.rowCount()):
            p = {}
            itr = 0
            for column in range(self.playlist.columnCount()):
                item = self.playlist.item(row, column)
                if item is not None:
                    if itr == 0:
                        p["title"] = item.text()
                    elif itr == 1:
                        p["duration"] = item.text()
                    elif itr == 2:
                        p["id"] = item.text()
                    itr = itr + 1
             #   print(p)
            all_items.append(p)
                # print(p)
        print(all_items)
        f = open("playlist.json","w")
        data = json.dumps(all_items)
        f.write(data)
        f.close()

    def load(self):
        f = open("playlist.json", "r")
        data = json.loads(f.read())
        f.close()
        
        self.add_to_list(data,   [i for i in range(len(data))])

    def delete(self):
        z = self.playlist.selectedItems()
        print(z)
        selected_rows = set()
        for item in self.playlist.selectedItems():
            selected_rows.add(item.row())

        for row in sorted(selected_rows, reverse=True):
            self.playlist.removeRow(row)


            
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = MyDialog()
    dialog.show()
    sys.exit(app.exec_())

