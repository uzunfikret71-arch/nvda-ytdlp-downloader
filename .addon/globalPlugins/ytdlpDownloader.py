# -*- coding: UTF-8 -*-

import os
import subprocess
import threading

import globalPluginHandler
import gui
import scriptHandler
import wx


ADDON_DIR = os.path.dirname(os.path.dirname(__file__))
BIN_DIR = os.path.join(ADDON_DIR, "bin")
YTDLP_EXE = os.path.join(BIN_DIR, "yt-dlp.exe")
FFMPEG_EXE = os.path.join(BIN_DIR, "ffmpeg.exe")
DENO_EXE = os.path.join(BIN_DIR, "deno.exe")


class DownloadDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="yt-dlp indirici", size=(660, 520))
		self.process = None
		self.updateProcess = None
		self.worker = None
		self.updateWorker = None
		self.closed = False
		panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)

		urlLabel = wx.StaticText(panel, label="Video adresi:")
		self.urlCtrl = wx.TextCtrl(panel)
		mainSizer.Add(urlLabel, 0, wx.ALL, 8)
		mainSizer.Add(self.urlCtrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

		typeBox = wx.StaticBoxSizer(wx.StaticBox(panel, label="İndirme türü"), wx.VERTICAL)
		self.videoRadio = wx.RadioButton(panel, label="Video olarak indir", style=wx.RB_GROUP)
		self.audioRadio = wx.RadioButton(panel, label="Ses olarak indir")
		typeBox.Add(self.videoRadio, 0, wx.ALL, 6)
		typeBox.Add(self.audioRadio, 0, wx.ALL, 6)
		mainSizer.Add(typeBox, 0, wx.EXPAND | wx.ALL, 8)

		formatSizer = wx.FlexGridSizer(2, 2, 8, 8)
		formatSizer.AddGrowableCol(1, 1)
		formatSizer.Add(wx.StaticText(panel, label="Video biçimi:"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.videoFormat = wx.Choice(panel, choices=["En iyi video (mp4 tercih et)", "En iyi video (orijinal)", "mp4", "mkv", "webm"])
		self.videoFormat.SetSelection(0)
		formatSizer.Add(self.videoFormat, 1, wx.EXPAND)
		formatSizer.Add(wx.StaticText(panel, label="Ses biçimi:"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.audioFormat = wx.Choice(panel, choices=["En iyi ses (webm hariç)", "En iyi ses (orijinal)", "mp3", "m4a", "flac", "wav"])
		self.audioFormat.SetSelection(0)
		formatSizer.Add(self.audioFormat, 1, wx.EXPAND)
		mainSizer.Add(formatSizer, 0, wx.EXPAND | wx.ALL, 8)

		self.audioOptionsBox = wx.StaticBoxSizer(wx.StaticBox(panel, label="Ses dosyası seçenekleri"), wx.VERTICAL)
		self.metadataCheck = wx.CheckBox(panel, label="Başlık, sanatçı ve benzeri medya bilgilerini dosyaya ekle")
		self.thumbnailCheck = wx.CheckBox(panel, label="Video küçük resmini ses dosyasına kapak görseli olarak ekle")
		self.audioOptionsBox.Add(self.metadataCheck, 0, wx.ALL, 6)
		self.audioOptionsBox.Add(self.thumbnailCheck, 0, wx.ALL, 6)
		mainSizer.Add(self.audioOptionsBox, 0, wx.EXPAND | wx.ALL, 8)

		pathSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.outputCtrl = wx.TextCtrl(panel)
		self.browseButton = wx.Button(panel, label="Klasör seç...")
		pathSizer.Add(self.outputCtrl, 1, wx.EXPAND | wx.RIGHT, 8)
		pathSizer.Add(self.browseButton, 0)
		mainSizer.Add(wx.StaticText(panel, label="İndirilecek klasör:"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		mainSizer.Add(pathSizer, 0, wx.EXPAND | wx.ALL, 8)

		self.logCtrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
		mainSizer.Add(self.logCtrl, 1, wx.EXPAND | wx.ALL, 8)

		buttonSizer = wx.StdDialogButtonSizer()
		self.startButton = wx.Button(panel, wx.ID_OK, label="İndirmeyi başlat")
		self.updateButton = wx.Button(panel, label="yt-dlp güncelle")
		self.closeButton = wx.Button(panel, wx.ID_CANCEL, label="Kapat")
		buttonSizer.AddButton(self.updateButton)
		buttonSizer.AddButton(self.startButton)
		buttonSizer.AddButton(self.closeButton)
		buttonSizer.Realize()
		mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, 8)

		panel.SetSizer(mainSizer)
		self.Bind(wx.EVT_RADIOBUTTON, self.onTypeChanged, self.videoRadio)
		self.Bind(wx.EVT_RADIOBUTTON, self.onTypeChanged, self.audioRadio)
		self.Bind(wx.EVT_BUTTON, self.onBrowse, self.browseButton)
		self.Bind(wx.EVT_BUTTON, self.startUpdater, self.updateButton)
		self.Bind(wx.EVT_BUTTON, self.onStart, self.startButton)
		self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.onTypeChanged(None)

	def onTypeChanged(self, event):
		isAudio = self.audioRadio.GetValue()
		self.audioFormat.Enable(isAudio)
		self.videoFormat.Enable(not isAudio)
		self.metadataCheck.Enable(isAudio)
		self.thumbnailCheck.Enable(isAudio)

	def onBrowse(self, event):
		with wx.DirDialog(
			self,
			message="İndirilecek klasörü seç",
			style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
		) as dialog:
			if dialog.ShowModal() == wx.ID_OK:
				self.outputCtrl.SetValue(dialog.GetPath())

	def setBusy(self, busy):
		if self.closed:
			return
		self.startButton.Enable(not busy)
		self.updateButton.Enable(not busy)
		self.browseButton.Enable(not busy)

	def buildProcessEnv(self):
		env = os.environ.copy()
		env["PATH"] = BIN_DIR + os.pathsep + env.get("PATH", "")
		return env

	def startUpdater(self, event=None):
		if self.updateProcess and self.updateProcess.poll() is None:
			return
		if self.process and self.process.poll() is None:
			wx.MessageBox("İndirme devam ederken güncelleme yapılamaz.", "İşlem sürüyor", wx.OK | wx.ICON_WARNING, self)
			return
		if not os.path.isfile(YTDLP_EXE):
			self.appendLog("yt-dlp.exe bulunamadı; güncelleme kontrolü atlandı.\r\n")
			return
		answer = wx.MessageBox(
			"yt-dlp sık güncellendiği için bazı sitelerde indirme sorunlarını gidermek amacıyla güncelleme yapılabilir. "
			"Bu işlem internet bağlantısı kullanır ve paket içindeki yt-dlp.exe dosyasını güncelleyebilir. Devam etmek istiyor musunuz?",
			"yt-dlp güncelle",
			wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
			self,
		)
		if answer != wx.YES:
			return
		self.setBusy(True)
		self.appendLog("yt-dlp güncellemesi kontrol ediliyor...\r\n")
		self.updateWorker = threading.Thread(target=self.runUpdater, daemon=True)
		self.updateWorker.start()

	def runUpdater(self):
		try:
			self.updateProcess = subprocess.Popen(
				[YTDLP_EXE, "-U"],
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
				encoding="utf-8",
				errors="replace",
				creationflags=subprocess.CREATE_NO_WINDOW,
				env=self.buildProcessEnv(),
			)
			for line in self.updateProcess.stdout:
				wx.CallAfter(self.appendLog, line)
			returnCode = self.updateProcess.wait()
			if returnCode == 0:
				wx.CallAfter(self.appendLog, "Güncelleme kontrolü tamamlandı.\r\n\r\n")
			else:
				wx.CallAfter(self.appendLog, "Güncelleme kontrolü tamamlanamadı; indirme yine de kullanılabilir.\r\n\r\n")
		except Exception as exc:
			wx.CallAfter(self.appendLog, "Güncelleme kontrolü sırasında hata: %s\r\n\r\n" % exc)
		finally:
			wx.CallAfter(self.setBusy, False)

	def appendLog(self, text):
		if self.closed:
			return
		self.logCtrl.AppendText(text)

	def onStart(self, event):
		url = self.urlCtrl.GetValue().strip()
		outputDir = self.outputCtrl.GetValue().strip()
		if not url:
			wx.MessageBox("Lütfen indirilecek video adresini yazın.", "Eksik bilgi", wx.OK | wx.ICON_WARNING, self)
			return
		if not outputDir:
			wx.MessageBox("Lütfen Klasör seç düğmesiyle hedef klasörü seçin.", "Eksik bilgi", wx.OK | wx.ICON_WARNING, self)
			return
		if not os.path.isdir(outputDir):
			wx.MessageBox("Seçilen hedef klasör bulunamadı.", "Eksik bilgi", wx.OK | wx.ICON_WARNING, self)
			return
		if not os.path.isfile(YTDLP_EXE):
			wx.MessageBox("yt-dlp.exe eklenti klasöründe bulunamadı.", "Eksik bağımlılık", wx.OK | wx.ICON_ERROR, self)
			return
		if not os.path.isfile(FFMPEG_EXE):
			wx.MessageBox("ffmpeg.exe eklenti klasöründe bulunamadı.", "Eksik bağımlılık", wx.OK | wx.ICON_ERROR, self)
			return
		if not os.path.isfile(DENO_EXE):
			wx.MessageBox("deno.exe eklenti klasöründe bulunamadı.", "Eksik bağımlılık", wx.OK | wx.ICON_ERROR, self)
			return

		command = self.buildCommand(url, outputDir)
		self.setBusy(True)
		self.logCtrl.SetValue("İndirme başlatılıyor...\r\n")
		self.worker = threading.Thread(target=self.runDownload, args=(command,), daemon=True)
		self.worker.start()

	def buildCommand(self, url, outputDir):
		command = [
			YTDLP_EXE,
			"--ffmpeg-location",
			BIN_DIR,
			"--windows-filenames",
			"--no-playlist",
			"-P",
			outputDir,
			"-o",
			"%(title)s.%(ext)s",
		]
		if self.audioRadio.GetValue():
			audioFormat = self.audioFormat.GetStringSelection()
			if audioFormat == "En iyi ses (orijinal)":
				command.extend(["-f", "ba"])
			else:
				command.extend(["-f", "ba[ext!=webm]/ba", "-x"])
				if audioFormat.startswith("En iyi ses"):
					command.extend(["--audio-format", "best"])
				else:
					command.extend(["--audio-format", audioFormat])
			if self.metadataCheck.GetValue():
				command.append("--add-metadata")
			if self.thumbnailCheck.GetValue():
				command.append("--embed-thumbnail")
		else:
			videoFormat = self.videoFormat.GetStringSelection()
			if videoFormat == "En iyi video (orijinal)":
				command.extend(["-f", "bv*+ba/b"])
			elif videoFormat.startswith("En iyi video"):
				command.extend(["-f", "bv*[ext=mp4]+ba[ext!=webm]/b[ext=mp4]/bv*+ba[ext!=webm]/b", "--merge-output-format", "mp4"])
			else:
				command.extend(["-f", "bv*+ba/b", "--merge-output-format", videoFormat])
		command.append(url)
		return command

	def runDownload(self, command):
		try:
			self.process = subprocess.Popen(
				command,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
				encoding="utf-8",
				errors="replace",
				creationflags=subprocess.CREATE_NO_WINDOW,
				env=self.buildProcessEnv(),
			)
			for line in self.process.stdout:
				wx.CallAfter(self.appendLog, line)
			returnCode = self.process.wait()
			if returnCode == 0:
				wx.CallAfter(self.appendLog, "\r\nTamamlandı.\r\n")
				wx.CallAfter(self.showDoneAndClose)
			else:
				wx.CallAfter(self.appendLog, "\r\nİndirme başarısız oldu. Ayrıntılar yukarıdaki çıktıda.\r\n")
		except Exception as exc:
			wx.CallAfter(self.appendLog, "\r\nHata: %s\r\n" % exc)
		finally:
			wx.CallAfter(self.setBusy, False)

	def showDoneAndClose(self):
		wx.MessageBox("İndirme tamamlandı.", "Tamamlandı", wx.OK | wx.ICON_INFORMATION, self)
		self.Destroy()

	def onClose(self, event):
		runningProcess = self.process if self.process and self.process.poll() is None else self.updateProcess
		if runningProcess and runningProcess.poll() is None:
			answer = wx.MessageBox(
				"Bir işlem devam ediyor. İşlemi durdurup pencereyi kapatmak istiyor musunuz?",
				"İşlem sürüyor",
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
				self,
			)
			if answer != wx.YES:
				return
			runningProcess.terminate()
		self.closed = True
		self.Destroy()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = "yt-dlp indirici"

	def __init__(self):
		super().__init__()
		self.menuItem = None
		wx.CallAfter(self.addMenuItem)

	def addMenuItem(self):
		toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.menuItem = toolsMenu.Append(wx.ID_ANY, "yt-dlp ile video veya ses indir...")
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onMenuItem, self.menuItem)

	def terminate(self):
		if self.menuItem:
			try:
				gui.mainFrame.sysTrayIcon.toolsMenu.Remove(self.menuItem)
			except Exception:
				pass
		super().terminate()

	def onMenuItem(self, event):
		self.showDialog()

	def showDialog(self):
		dialog = DownloadDialog(gui.mainFrame)
		dialog.Show()

	@scriptHandler.script(
		description="yt-dlp video ve ses indirme penceresini açar",
		gesture="kb:NVDA+shift+y",
	)
	def script_openDownloader(self, gesture):
		wx.CallAfter(self.showDialog)
