import os
import subprocess
import tkinter as tk
from tkinter import filedialog

if __name__ == '__main__':
	root=tk.Tk()
	root.withdraw()

	filename=filedialog.askopenfilename()

	of=filename.split(".")[0]+"_new."+filename.split(".")[1]
	of=filedialog.asksaveasfilename(initialfile=of)
	cmdStr=f"ffmpeg -y -i \"{filename}\" \"{of}\""
	print(cmdStr)
	subprocess.call(cmdStr, shell=True)
