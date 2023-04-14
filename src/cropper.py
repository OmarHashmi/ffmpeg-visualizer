import os
import re
import subprocess
import cv2
import tkinter as tk
from tkinter import filedialog

class Cropper:
	crops=[0,0,0,0]
	cap=None
	filename=""
	w,h=0,0

	def __init__(self,filename):
		self.filename=os.path.relpath(filename)
		self.cap=cv2.VideoCapture(self.filename)
		ret,frame=self.cap.read()
		self.h,self.w=frame.shape[:2]
		l=max(self.w, self.h)

		cv2.namedWindow("Params")
		cv2.resizeWindow("Params", 480, 480)
		cv2.createTrackbar("Crop", "Params", 0, l, lambda x:None)
		cv2.createTrackbar("Crop Fine", "Params", 0, 15, lambda x:None)
		cv2.createTrackbar("Zoom", "Params", 0, 100, lambda x:None)
		cv2.createTrackbar("Time", "Params", 0, 100, lambda x:None)
		cv2.createTrackbar("TBLR", "Params", 0, 3, lambda x:self.tblrUpdate())

	def process(self):
		cv2.destroyAllWindows()
		w,h,crops=self.w,self.h,self.crops
		of=self.filename.split(".")[0]+"_cropped."+self.filename.split(".")[1]
		of=filedialog.asksaveasfilename(initialfile=of)
		cmdStr=f"ffmpeg -y -i \"{self.filename}\" -vf crop={w-(crops[2]+crops[3])}:{h-(crops[0]+crops[1])}:{crops[2]}:{crops[0]} \"{of}\""
		print(cmdStr)
		subprocess.call(cmdStr,shell=True)

	def run(self):
		while(1):
			try:
				crop=cv2.getTrackbarPos("Crop", "Params")+cv2.getTrackbarPos("Crop Fine", "Params")
				zoom=cv2.getTrackbarPos("Zoom", "Params")/10+1
				time=cv2.getTrackbarPos("Time", "Params")/100
				tblr=cv2.getTrackbarPos("TBLR", "Params")
			except cv2.error:
				break

			frame=self.timeFrame(time)
			frame=self.cropFrame(frame,crop,tblr)
			frame=self.zoomFrame(frame,zoom,tblr)

			cv2.imshow("Cropper",frame)

			if cv2.waitKey(1)&0xFF==ord('q'):
				break

		self.process()

	def timeFrame(self, framePercent=0.5):
		cap=cv2.VideoCapture(self.filename)

		total_frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		frame_index=((total_frames*framePercent)//1)-1
		cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
		ret, frame=cap.read()

		return frame

	def cropFrame(self,frame,crop,tblr):
		self.crops[tblr]=crop
		h,w=frame.shape[:2]

		x1, y1 =   self.crops[2],   self.crops[0]
		x2, y2 = w-self.crops[3], h-self.crops[1]
		x1,y1,x2,y2=int(x1),int(y1),int(x2),int(y2)

		return frame[y1:y2, x1:x2]

	def zoomFrame(self,frame,zoom,tblr):
		h,w=frame.shape[:2]

		cx, cy = w//2, h//2
		zx, zy = w//zoom, h//zoom
		hzx,hzy= zx//2, zy//2
		x1,y1,x2,y2=0,0,w,h

		if tblr==0:
			x1, y1=cx-hzx, 0
			x2, y2=cx+hzx, zy
		elif tblr==1:
			x1, y1=cx-hzx, h-zy
			x2, y2=cx+hzx, h
		elif tblr==2:
			x1,y1 =  0,      cy-hzy
			x2,y2 =  zx,     cy+hzy
		elif tblr==4:
			x1,y1 =  w-zx,   cy-hzy
			x2,y2 =  w,      cy+hzy
		x1,y1,x2,y2=int(x1),int(y1),int(x2),int(y2)

		croppedFrame=frame[y1:y2, x1:x2]

		return cv2.resize(croppedFrame,(w,h),interpolation=cv2.INTER_NEAREST)

	def tblrUpdate(self):
		tblr=cv2.getTrackbarPos("TBLR", "Params")

		cv2.setTrackbarPos("Crop","Params",self.crops[tblr])
		cv2.setTrackbarPos("Crop Fine","Params",self.crops[tblr])
		cv2.setTrackbarPos("Zoom","Params",0)

if __name__ == '__main__':
	root=tk.Tk()
	root.withdraw()

	filePath=filedialog.askopenfilename()

	Cropper(filePath).run()