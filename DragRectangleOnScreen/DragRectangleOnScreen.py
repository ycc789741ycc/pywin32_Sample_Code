import win32gui,win32con,win32api
from win32api import GetSystemMetrics
from pynput import mouse
import threading

def DrawRectangle(rect,invalidate = False):
    PyGdiHANDLE = win32gui.CreatePen(win32con.PS_SOLID, 10 , win32api.RGB(0,255,0))
    dc = win32gui.GetWindowDC(None)
    hwnd = win32gui.WindowFromPoint((0,0))
    monitor = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))
    
    
    if invalidate:
        win32gui.InvalidateRect(hwnd, monitor, True) # Refresh the entire monitor
   
    win32gui.FrameRect(dc,(rect[0],rect[1],rect[2],rect[3]),PyGdiHANDLE)
    win32gui.ReleaseDC(hwnd,dc)

class DragLocation():
    __DragFlag = 0
    _listen = True
    _NForbidFlag = True
    def __init__(self):
        self.ix = 0
        self.iy = 0
        self.fx = 1
        self.fy = 1
        self.current_x = 0
        self.current_y = 0

    def getRegion(self):
        r_ix,r_iy,r_fx,r_fy = self.ix,self.iy,self.fx,self.fy
        if self.ix > self.fx:
            r_ix,r_fx = r_fx,r_ix
        if self.iy > self.fy:
            r_iy,r_fy = r_fy,r_iy
        if self.fx == self.ix:
            r_fx = r_ix+1
        if self.fy == self.iy:
            r_fy = r_iy+1
        return [r_ix,r_iy,r_fx,r_fy]
        
    def _on_move(self,x,y):
        self.current_x = x
        self.current_y = y
        if self.__DragFlag == 1:
            self.fx = x
            self.fy = y

    def _on_click(self,x,y,button,pressed):
        if button == mouse.Button.left:
            if pressed and self._NForbidFlag:
                self.ix = x
                self.iy = y
                self.fx = x
                self.fy = y
                self.__DragFlag = 1
            elif self.__DragFlag == 1:
                self.fx = x
                self.fy = y
                self.__DragFlag = 0
        
        if not pressed:
            return False        

    def _MouseListener(self):
        while self._listen:
            with mouse.Listener( on_move = self._on_move,on_click = self._on_click) as listener:
                listener.join()
    
class DragRectangle(DragLocation):
    def __init__(self):
        DragLocation.__init__(self)
    
    def __DrawRect(self):
        rect_record = (0,0,1,1)
        invalidate = False
        while self._listen:
            rect = self.getRegion()
            if rect != rect_record:
                rect_record = rect
                invalidate = True
            else:
                invalidate = False
            DrawRectangle(rect,invalidate)
        self._listen = True

    def start(self):
        threading.Thread(target=self._MouseListener,daemon=True).start()
        threading.Thread(target=self.__DrawRect,daemon=True).start()

    def end(self):
        self._listen = False

if __name__ == "__main__":
    import time
    OBJ = DragRectangle()
    OBJ.start()
    time.sleep(50)
    OBJ.end()