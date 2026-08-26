# -*- coding: UTF-8 -*-
# ytdlpDownloader: NVDA add-on for downloading video and audio with yt-dlp.
# Copyright (C) 2026 Fikret Uzun
# Licensed under the GNU General Public License version 2 or later.

import os
import json
import subprocess
import tempfile
import threading

import addonHandler
import config
import globalPluginHandler
import gui
import scriptHandler
import wx


addonHandler.initTranslation()

ADDON_DIR = os.path.dirname(os.path.dirname(__file__))
BIN_DIR = os.path.join(ADDON_DIR, "bin")
YTDLP_EXE = os.path.join(BIN_DIR, "yt-dlp.exe")
FFMPEG_EXE = os.path.join(BIN_DIR, "ffmpeg.exe")
DENO_EXE = os.path.join(BIN_DIR, "deno.exe")
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
PROCESS_FLAGS = CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
CONFIG_SECTION = "ytdlpDownloader"
THUMBNAIL_AUDIO_EXTENSIONS = {"mp3", "mkv", "mka", "ogg", "opus", "flac", "m4a", "mp4", "m4v", "mov"}
METADATA_AUDIO_EXTENSIONS = THUMBNAIL_AUDIO_EXTENSIONS | {"wav"}


def registerConfigSpec():
	"""Register persistent settings with NVDA's configuration manager."""
	config.conf.spec[CONFIG_SECTION] = {
		"outputDirectory": "string(default='')",
	}


def getSavedOutputDirectory():
	try:
		return config.conf[CONFIG_SECTION]["outputDirectory"]
	except (KeyError, TypeError):
		return ""


def saveOutputDirectory(path):
	config.conf[CONFIG_SECTION]["outputDirectory"] = path


class DownloadDialog(wx.Dialog):
	def __init__(self, parent, onDestroyed=None):
		super().__init__(parent, title=_("Video ve Ses İndirici"), size=(660, 520))
		self.process = None
		self.worker = None
		self.closed = False
		self.promptEvent = None
		self._onDestroyed = onDestroyed

		panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)

		mainSizer.Add(wx.StaticText(panel, label=_("Video veya oynatma listesi adresi:")), 0, wx.ALL, 8)
		self.urlCtrl = wx.TextCtrl(panel)
		mainSizer.Add(self.urlCtrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

		typeBox = wx.StaticBoxSizer(wx.StaticBox(panel, label=_("İndirme türü")), wx.VERTICAL)
		self.videoRadio = wx.RadioButton(panel, label=_("Video olarak indir"), style=wx.RB_GROUP)
		self.audioRadio = wx.RadioButton(panel, label=_("Ses olarak indir"))
		typeBox.Add(self.videoRadio, 0, wx.ALL, 6)
		typeBox.Add(self.audioRadio, 0, wx.ALL, 6)
		mainSizer.Add(typeBox, 0, wx.EXPAND | wx.ALL, 8)

		formatSizer = wx.FlexGridSizer(2, 2, 8, 8)
		formatSizer.AddGrowableCol(1, 1)
		formatSizer.Add(wx.StaticText(panel, label=_("Video biçimi:")), 0, wx.ALIGN_CENTER_VERTICAL)
		self.videoFormat = wx.Choice(
			panel,
			choices=[
				_("En iyi video (mp4 tercih et)"),
				_("En iyi video (orijinal)"),
				"mp4",
				"mkv",
				"webm",
			],
		)
		self.videoFormat.SetSelection(0)
		formatSizer.Add(self.videoFormat, 1, wx.EXPAND)
		formatSizer.Add(wx.StaticText(panel, label=_("Ses biçimi:")), 0, wx.ALIGN_CENTER_VERTICAL)
		self.audioFormat = wx.Choice(
			panel,
			choices=[
				_("En iyi ses (webm hariç)"),
				_("En iyi ses (orijinal)"),
				"mp3",
				"m4a",
				"flac",
				"wav",
			],
		)
		self.audioFormat.SetSelection(0)
		formatSizer.Add(self.audioFormat, 1, wx.EXPAND)
		mainSizer.Add(formatSizer, 0, wx.EXPAND | wx.ALL, 8)

		self.audioOptionsBox = wx.StaticBoxSizer(
			wx.StaticBox(panel, label=_("Ses dosyası seçenekleri")), wx.VERTICAL
		)
		self.metadataCheck = wx.CheckBox(
			panel, label=_("Başlık, sanatçı ve benzeri medya bilgilerini dosyaya ekle")
		)
		self.thumbnailCheck = wx.CheckBox(
			panel, label=_("Video küçük resmini ses dosyasına kapak görseli olarak ekle")
		)
		self.audioOptionsBox.Add(self.metadataCheck, 0, wx.ALL, 6)
		self.audioOptionsBox.Add(self.thumbnailCheck, 0, wx.ALL, 6)
		mainSizer.Add(self.audioOptionsBox, 0, wx.EXPAND | wx.ALL, 8)

		pathSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.outputCtrl = wx.TextCtrl(panel, value=getSavedOutputDirectory())
		self.browseButton = wx.Button(panel, label=_("Klasör seç..."))
		pathSizer.Add(self.outputCtrl, 1, wx.EXPAND | wx.RIGHT, 8)
		pathSizer.Add(self.browseButton, 0)
		mainSizer.Add(wx.StaticText(panel, label=_("İndirilecek klasör:")), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		mainSizer.Add(pathSizer, 0, wx.EXPAND | wx.ALL, 8)

		self.logCtrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
		mainSizer.Add(self.logCtrl, 1, wx.EXPAND | wx.ALL, 8)

		buttonSizer = wx.StdDialogButtonSizer()
		self.startButton = wx.Button(panel, wx.ID_OK, label=_("İndirmeyi başlat"))
		self.updateButton = wx.Button(panel, label=_("yt-dlp güncelle"))
		self.closeButton = wx.Button(panel, wx.ID_CANCEL, label=_("Kapat"))
		buttonSizer.AddButton(self.updateButton)
		buttonSizer.AddButton(self.startButton)
		buttonSizer.AddButton(self.closeButton)
		buttonSizer.Realize()
		mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, 8)

		panel.SetSizer(mainSizer)
		self.Bind(wx.EVT_RADIOBUTTON, self.onTypeChanged, self.videoRadio)
		self.Bind(wx.EVT_RADIOBUTTON, self.onTypeChanged, self.audioRadio)
		self.Bind(wx.EVT_CHOICE, self.onAudioFormatChanged, self.audioFormat)
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
		self.updateThumbnailOption()

	def onAudioFormatChanged(self, event):
		self.updateThumbnailOption()

	def updateThumbnailOption(self):
		# yt-dlp cannot embed thumbnails in WAV and does not support every
		# container that may be returned by the two automatic/original choices.
		isSupported = self.audioRadio.GetValue() and self.audioFormat.GetSelection() in (0, 2, 3, 4)
		if not isSupported:
			self.thumbnailCheck.SetValue(False)
		self.thumbnailCheck.Enable(isSupported)

	def onBrowse(self, event):
		currentPath = self.outputCtrl.GetValue().strip()
		dialogArgs = {
			"message": _("İndirilecek klasörü seç"),
			"style": wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
		}
		if os.path.isdir(currentPath):
			dialogArgs["defaultPath"] = currentPath
		with wx.DirDialog(self, **dialogArgs) as dialog:
			if dialog.ShowModal() == wx.ID_OK:
				selectedPath = dialog.GetPath()
				self.outputCtrl.SetValue(selectedPath)
				saveOutputDirectory(selectedPath)

	def setBusy(self, busy):
		if self.closed:
			return
		self.startButton.Enable(not busy)
		self.updateButton.Enable(not busy)
		self.browseButton.Enable(not busy)
		self.urlCtrl.Enable(not busy)
		self.outputCtrl.Enable(not busy)
		self.videoRadio.Enable(not busy)
		self.audioRadio.Enable(not busy)
		self.videoFormat.Enable(not busy)
		self.audioFormat.Enable(not busy)
		self.metadataCheck.Enable(not busy)
		self.thumbnailCheck.Enable(not busy)
		if not busy:
			self.onTypeChanged(None)

	def buildProcessEnv(self):
		env = os.environ.copy()
		env["PATH"] = BIN_DIR + os.pathsep + env.get("PATH", "")
		return env

	def startUpdater(self, event=None):
		if self.isWorkerActive():
			wx.MessageBox(_("Başka bir işlem devam ediyor."), _("İşlem sürüyor"), wx.OK | wx.ICON_WARNING, self)
			return
		if not os.path.isfile(YTDLP_EXE):
			self.appendLog(_("yt-dlp.exe bulunamadı; güncelleme kontrolü atlandı.\r\n"))
			return
		answer = wx.MessageBox(
			_("yt-dlp güncellenecek ve bu işlem internet bağlantısı kullanacaktır. Devam etmek istiyor musunuz?"),
			_("yt-dlp güncelle"),
			wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
			self,
		)
		if answer != wx.YES:
			return
		self.setBusy(True)
		self.appendLog(_("yt-dlp güncellemesi kontrol ediliyor...\r\n"))
		self.worker = threading.Thread(target=self.runProcess, args=([YTDLP_EXE, "-U"], True), daemon=True)
		self.worker.start()

	def appendLog(self, text):
		if not self.closed:
			self.logCtrl.AppendText(text)

	def onStart(self, event):
		if self.isWorkerActive():
			return
		url = self.urlCtrl.GetValue().strip()
		outputDir = self.outputCtrl.GetValue().strip()
		if not url:
			wx.MessageBox(_("Lütfen indirilecek video veya oynatma listesi adresini yazın."), _("Eksik bilgi"), wx.OK | wx.ICON_WARNING, self)
			return
		if not outputDir:
			wx.MessageBox(_("Lütfen Klasör seç düğmesiyle hedef klasörü seçin."), _("Eksik bilgi"), wx.OK | wx.ICON_WARNING, self)
			return
		if not os.path.isdir(outputDir):
			wx.MessageBox(_("Seçilen hedef klasör bulunamadı."), _("Eksik bilgi"), wx.OK | wx.ICON_WARNING, self)
			return
		missing = [name for name, path in (("yt-dlp.exe", YTDLP_EXE), ("ffmpeg.exe", FFMPEG_EXE), ("deno.exe", DENO_EXE)) if not os.path.isfile(path)]
		if missing:
			wx.MessageBox(_("Eksik bağımlılık: %s") % ", ".join(missing), _("Eksik bağımlılık"), wx.OK | wx.ICON_ERROR, self)
			return

		saveOutputDirectory(outputDir)
		command = self.buildCommand(url, outputDir)
		checkAudioOptions = (
			self.audioRadio.GetValue()
			and self.audioFormat.GetSelection() == 0
			and (self.thumbnailCheck.GetValue() or self.metadataCheck.GetValue())
		)
		self.setBusy(True)
		self.logCtrl.SetValue(_("İndirme başlatılıyor...\r\n"))
		workerTarget = self.prepareDownload if checkAudioOptions else self.runProcess
		workerArgs = (command, url) if checkAudioOptions else (command, False)
		self.worker = threading.Thread(target=workerTarget, args=workerArgs, daemon=True)
		self.worker.start()

	def buildCommand(self, url, outputDir):
		command = [
			YTDLP_EXE,
			"--ffmpeg-location", BIN_DIR,
			"--windows-filenames",
			"-P", outputDir,
			"-o", "%(playlist_index&{} - |)s%(title)s.%(ext)s",
		]
		if self.audioRadio.GetValue():
			audioSelection = self.audioFormat.GetSelection()
			if audioSelection == 1:
				command.extend(["-f", "ba"])
			elif audioSelection == 0:
				# Keep the source audio stream as-is: no WebM fallback and no
				# extraction/conversion postprocessor for this automatic choice.
				command.extend(["-f", "ba[ext!=webm]"])
			else:
				command.extend(["-f", "ba[ext!=webm]/ba", "-x"])
				command.extend(["--audio-format", self.audioFormat.GetStringSelection()])
			if self.metadataCheck.GetValue():
				command.append("--add-metadata")
			if self.thumbnailCheck.GetValue():
				command.append("--embed-thumbnail")
		else:
			videoSelection = self.videoFormat.GetSelection()
			if videoSelection == 1:
				command.extend(["-f", "bv*+ba/b"])
			elif videoSelection == 0:
				command.extend(["-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b", "--merge-output-format", "mp4/mkv"])
			elif videoSelection == 2:
				command.extend(["-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]", "--merge-output-format", "mp4"])
			elif videoSelection == 4:
				command.extend(["-f", "bv*[ext=webm]+ba[ext=webm]/b[ext=webm]", "--merge-output-format", "webm"])
			else:
				command.extend(["-f", "bv*+ba/b", "--merge-output-format", self.videoFormat.GetStringSelection()])
		# End option parsing before the user-supplied URL. This prevents a value
		# beginning with a dash from being interpreted as a yt-dlp option.
		command.extend(["--", url])
		return command

	def prepareDownload(self, command, url):
		"""Check thumbnail support and reuse the fetched metadata for downloading."""
		wx.CallAfter(self.appendLog, _("Kapak görseli uyumluluğu kontrol ediliyor...\r\n"))
		probeCommand = [
			YTDLP_EXE,
			"--ffmpeg-location", BIN_DIR,
			"--no-warnings",
			"--dump-single-json",
			"-f", "ba[ext!=webm]",
			"--",
			url,
		]
		try:
			self.process = subprocess.Popen(
				probeCommand,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				shell=False,
				text=True,
				encoding="utf-8",
				errors="replace",
				creationflags=PROCESS_FLAGS,
				env=self.buildProcessEnv(),
			)
			stdout, stderr = self.process.communicate()
			returnCode = self.process.returncode
		except Exception as exc:
			stdout, stderr, returnCode = "", str(exc), -1
		finally:
			self.process = None

		if self.closed:
			return
		try:
			info = json.loads(stdout) if returnCode == 0 else None
		except (TypeError, ValueError):
			info = None
		extensions, missingEntries = self.collectSelectedExtensions(info) if info else (set(), 0)
		if returnCode != 0:
			if "requested format is not available" in stderr.lower():
				wx.CallAfter(self.showNoNonWebmAudioWarning, stderr)
			else:
				wx.CallAfter(self.showInspectionError, stderr)
			wx.CallAfter(self.setBusy, False)
			return
		if not extensions:
			wx.CallAfter(self.showNoNonWebmAudioWarning, stderr)
			wx.CallAfter(self.setBusy, False)
			return
		if missingEntries:
			wx.CallAfter(self.showIncompletePlaylistWarning, missingEntries)
			wx.CallAfter(self.setBusy, False)
			return

		infoPath = None
		try:
			with tempfile.NamedTemporaryFile(
				mode="w", suffix=".info.json", encoding="utf-8", delete=False
			) as infoFile:
				infoFile.write(stdout)
				infoPath = infoFile.name
		except OSError as exc:
			wx.CallAfter(self.showNoNonWebmAudioWarning, str(exc))
			wx.CallAfter(self.setBusy, False)
			return
		unsupportedThumbnail = sorted(
			extension for extension in extensions if extension not in THUMBNAIL_AUDIO_EXTENSIONS
		) if "--embed-thumbnail" in command else []
		unsupportedMetadata = sorted(
			extension for extension in extensions if extension not in METADATA_AUDIO_EXTENSIONS
		) if "--add-metadata" in command else []
		if unsupportedThumbnail or unsupportedMetadata:
			if not self.confirmDownloadWithoutOptions(unsupportedThumbnail, unsupportedMetadata):
				self.removeTemporaryFile(infoPath)
				wx.CallAfter(self.appendLog, _("İndirme iptal edildi.\r\n"))
				wx.CallAfter(self.setBusy, False)
				return
			if unsupportedThumbnail:
				command = [argument for argument in command if argument != "--embed-thumbnail"]
			if unsupportedMetadata:
				command = [argument for argument in command if argument != "--add-metadata"]
		command = command[:-2] + ["--load-info-json", infoPath]
		self.runProcess(command, False, infoPath)

	def collectSelectedExtensions(self, info):
		extensions = set()
		missingEntries = 0
		entries = info.get("entries") if isinstance(info, dict) else None
		if entries is not None:
			for entry in entries:
				if not entry:
					missingEntries += 1
					continue
				entryExtensions, entryMissing = self.collectSelectedExtensions(entry)
				extensions.update(entryExtensions)
				missingEntries += entryMissing
			return extensions, missingEntries
		if not isinstance(info, dict):
			return extensions, 1
		selected = info.get("requested_downloads") or [info]
		for item in selected:
			extension = item.get("ext") if isinstance(item, dict) else None
			if extension:
				extensions.add(extension.lower().lstrip("."))
		if not extensions:
			missingEntries += 1
		return extensions, missingEntries

	def removeTemporaryFile(self, path):
		if not path:
			return
		try:
			os.remove(path)
		except OSError:
			pass

	def showNoNonWebmAudioWarning(self, probeError):
		if self.closed:
			return
		self.appendLog(_("WebM dışı bir ses biçimi bulunamadı veya biçim bilgisi alınamadı.\r\n"))
		if probeError.strip():
			self.appendLog(probeError.strip() + "\r\n")
		wx.MessageBox(
			_("Bu içerikte WebM dışı bir ses biçimi bulunamadı veya biçim bilgisi alınamadı. İndirme başlatılmadı."),
			_("Uygun ses biçimi bulunamadı"),
			wx.OK | wx.ICON_WARNING,
			self,
		)

	def showInspectionError(self, probeError):
		if self.closed:
			return
		self.appendLog(_("Ses biçimi kontrol edilemedi.\r\n"))
		if probeError.strip():
			self.appendLog(probeError.strip() + "\r\n")
		wx.MessageBox(
			_("Adres veya site kontrol edilirken bir hata oluştu. İnternet bağlantısını, adresi ve yukarıdaki hata ayrıntılarını kontrol edin."),
			_("Biçim kontrolü başarısız"),
			wx.OK | wx.ICON_ERROR,
			self,
		)

	def showIncompletePlaylistWarning(self, missingEntries):
		if self.closed:
			return
		wx.MessageBox(
			_("Oynatma listesindeki %d öğenin ses biçimi belirlenemedi. Eksik veya hatalı öğelerin sessizce atlanmaması için indirme başlatılmadı.") % missingEntries,
			_("Oynatma listesi eksik çözümlendi"),
			wx.OK | wx.ICON_WARNING,
			self,
		)

	def confirmDownloadWithoutOptions(self, unsupportedThumbnail, unsupportedMetadata):
		result = {"continue": False}
		self.promptEvent = threading.Event()

		def showWarning():
			if self.closed:
				self.promptEvent.set()
				return
			warnings = []
			if unsupportedThumbnail:
				warnings.append(_("Kapak görseli desteklenmiyor: %s.") % ", ".join(ext.upper() for ext in unsupportedThumbnail))
			if unsupportedMetadata:
				warnings.append(_("Medya bilgisi ekleme desteklenmiyor: %s.") % ", ".join(ext.upper() for ext in unsupportedMetadata))
			message = " ".join(warnings) + " " + _(
				"Ses başka bir biçime kodlanmayacak. Desteklenmeyen seçenekler kapatılarak indirmeye devam edilsin mi?"
			)
			result["continue"] = wx.MessageBox(
				message,
				_("Ses dosyası seçenekleri desteklenmiyor"),
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
				self,
			) == wx.YES
			self.promptEvent.set()

		wx.CallAfter(showWarning)
		self.promptEvent.wait()
		self.promptEvent = None
		return result["continue"] and not self.closed

	def runProcess(self, command, isUpdate, cleanupPath=None):
		try:
			if self.closed:
				return
			self.process = subprocess.Popen(
				command,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				shell=False,
				text=True,
				encoding="utf-8",
				errors="replace",
				creationflags=PROCESS_FLAGS,
				env=self.buildProcessEnv(),
			)
			# The dialog may have been closed in the brief interval while Popen
			# was creating the process. Do not leave that process orphaned.
			if self.closed:
				self.terminateProcessTree()
				return
			for line in self.process.stdout:
				wx.CallAfter(self.appendLog, line)
			returnCode = self.process.wait()
			if self.closed:
				return
			if returnCode == 0 and not isUpdate:
				wx.CallAfter(self.finishDownload)
			elif returnCode == 0:
				wx.CallAfter(self.appendLog, _("Güncelleme kontrolü tamamlandı.\r\n\r\n"))
			else:
				message = _("Güncelleme tamamlanamadı.\r\n\r\n") if isUpdate else _("\r\nİndirme başarısız oldu. Ayrıntılar yukarıdaki çıktıda.\r\n")
				wx.CallAfter(self.appendLog, message)
		except Exception as exc:
			if not self.closed:
				wx.CallAfter(self.appendLog, _("\r\nHata: %s\r\n") % exc)
		finally:
			self.process = None
			self.removeTemporaryFile(cleanupPath)
			if not self.closed:
				wx.CallAfter(self.setBusy, False)

	def finishDownload(self):
		if self.closed:
			return
		self.appendLog(_("\r\nTamamlandı.\r\n"))
		wx.MessageBox(_("İndirme tamamlandı."), _("Tamamlandı"), wx.OK | wx.ICON_INFORMATION, self)
		self.closeDialog()

	def isProcessRunning(self):
		return self.process is not None and self.process.poll() is None

	def isWorkerActive(self):
		return self.worker is not None and self.worker.is_alive()

	def terminateProcessTree(self):
		if not self.isProcessRunning():
			return
		try:
			subprocess.run(
				["taskkill", "/PID", str(self.process.pid), "/T", "/F"],
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL,
				creationflags=CREATE_NO_WINDOW,
				check=False,
			)
		except OSError:
			self.process.terminate()

	def closeDialog(self):
		if self.closed:
			return
		self.closed = True
		if self.promptEvent:
			self.promptEvent.set()
		callback = self._onDestroyed
		self._onDestroyed = None
		self.Destroy()
		if callback:
			callback(self)

	def onClose(self, event):
		if self.isWorkerActive():
			answer = wx.MessageBox(
				_("Bir işlem devam ediyor. İşlemi durdurup pencereyi kapatmak istiyor musunuz?"),
				_("İşlem sürüyor"),
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
				self,
			)
			if answer != wx.YES:
				return
			self.terminateProcessTree()
		self.closeDialog()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Video ve Ses İndirici")

	def __init__(self):
		super().__init__()
		registerConfigSpec()
		self.menuItem = None
		self.dialog = None
		self._terminated = False
		wx.CallAfter(self.addMenuItem)

	def addMenuItem(self):
		if self._terminated:
			return
		toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.menuItem = toolsMenu.Append(wx.ID_ANY, _("Video veya ses indir..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onMenuItem, self.menuItem)

	def terminate(self):
		self._terminated = True
		if self.dialog and not self.dialog.closed:
			self.dialog.terminateProcessTree()
			self.dialog.closeDialog()
		if self.menuItem:
			try:
				gui.mainFrame.sysTrayIcon.toolsMenu.Remove(self.menuItem)
			except (RuntimeError, wx.PyDeadObjectError):
				pass
			self.menuItem = None
		super().terminate()

	def onMenuItem(self, event):
		self.showDialog()

	def onDialogDestroyed(self, dialog):
		if self.dialog is dialog:
			self.dialog = None

	def showDialog(self):
		if self.dialog and not self.dialog.closed:
			self.dialog.Raise()
			self.dialog.SetFocus()
			return
		self.dialog = DownloadDialog(gui.mainFrame, self.onDialogDestroyed)
		self.dialog.Show()

	@scriptHandler.script(
		description=_("Video ve Ses İndirici penceresini açar"),
		gesture="kb:NVDA+shift+y",
	)
	def script_openDownloader(self, gesture):
		wx.CallAfter(self.showDialog)
