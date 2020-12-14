import random
import math

class Color:
    r = 0
    g = 0 
    b = 0
    a = 0

    def __init__(self,r = 1,g = 1,b = 1,a = 1):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.h = None
        self.s = None
        self.v = None
    
    def random_color(self,max_a = 255):
        self.r = random.randint(0,255)/255
        self.g = random.randint(0,255)/255
        self.b = random.randint(0,255)/255
        self.a = random.randint(0,max_a)/255

    def tostring(self):
        ret = " r : " + str(self.r) + ", g : " + str(self.g) + ", b : " + str(self.b) + ", a : " + str(self.a) 
        return ret

    def get_hsv(self):
        r, g, b = self.r, self.g, self.b
        mx = max(r, g, b)
        mn = min(r, g, b)
        m = mx-mn
        if mx == mn:
            h = 0
        elif mx == r:
            if g >= b:
                h = ((g-b)/m)*60
            else:
                h = ((g-b)/m)*60 + 360
        elif mx == g:
            h = ((b-r)/m)*60 + 120
        elif mx == b:
            h = ((r-g)/m)*60 + 240
        if mx == 0:
            s = 0
        else:
            s = m/mx
        v = mx
        self.h = h / 2
        self.s = s #* 255.0
        self.v = v #* 255.0
        return self.h,self.s,self.v

    def compare(self,color):
        dest_h,dest_s,dest_v = color.get_hsv()
        self_h,self_s,self_v = self.get_hsv()
        a = 1
        b = 200
        c = 200
        return a*abs(dest_v-self_v) + b*(1 - abs(dest_s-self_s))+ c*(1-max(abs(self_h - dest_h),abs(dest_h - self_h))/360)
    
    def compare_with(self,h,s,v):
        dest_h = h
        dest_s = s
        dest_v = v
        self_h,self_s,self_v = self.get_hsv()
        a = 1
        b = 200
        c = 200
        return a*abs(dest_v-self_v) + b*(1 - abs(dest_s-self_s))+ c*(1-max(abs(self_h - dest_h),abs(dest_h - self_h))/360)


    def copy(self):
        return Color(self.r,self.g,self.b,self.a)
