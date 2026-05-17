import wx
import wx.html2

class YouTubePlayerFrame(wx.Frame):
    def __init__(self, video_url):
        super().__init__(None, title="Dora YouTube Player - The Bluebird Project", size=(800, 600))
        self.browser = wx.html2.WebView.New(self)
        self.browser.LoadURL(video_url)
        self.Show()

def launch_player(url=None):
    app = wx.App()
    
    if not url:
        dialog = wx.TextEntryDialog(None, "Please enter the YouTube video URL:", "Dora YouTube Player - The Bluebird Project")
        if dialog.ShowModal() == wx.ID_OK:
            url = dialog.GetValue()
        else:
            return # Cancelled
        dialog.Destroy()
        
    if url:
        YouTubePlayerFrame(url)
        app.MainLoop()
