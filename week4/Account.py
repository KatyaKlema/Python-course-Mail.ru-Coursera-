class Value:
	def __init__(self):
		self.value = None

	def prepare_value(value, comission):
		return value - value * comission

	def __get__(self, obj, obj_type):
		return self.value

	def __set__(self, obj, value):
		self.value = self.prepare_value(value, obj.comission) 

class Account:
	amount = Value()
	def __init__(self, comission):
		self.comission = comission

new_account = Account(0.1)
new_account.amount = 100

print(new_account.amount)
