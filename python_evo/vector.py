import random
import math
class Vector:
	x = 0
	y = 0
	z = 0

	def __init__(self,x=0,y=0,z=0 ):
		self.x = x
		self.y = y
		self.z = z

	def add(self,vector):
		x = self.x + vector.x
		y = self.y + vector.y
		z = self.z + vector.z
		ret = Vector(x,y,z)
		return ret

	def sub(self,vector):
		x = self.x - vector.x
		y = self.y - vector.y
		z = self.z - vector.z
		ret = Vector(x,y,z)
		return ret

	@staticmethod
	def random_vec(min,max):
		x = random.randint(min,max)
		y = random.randint(min,max)

		return Vector(x,y,0)

	def equal(self,vec):
		if self.x == vec.x and self.y == vec.y and self.z == vec.z:
			return True
		else:
			return False

	def tostring(self):
		return " x :" + str(math.floor(self.x * 10000)/10000) +" , y :" + str(math.floor(self.y * 10000)/10000)

	def copy(self):
    		return Vector(self.x,self.y,self.z)
