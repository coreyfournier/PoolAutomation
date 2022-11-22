#Class stub of Pi GPIO for doing testing.
class GpioStub():
	BOARD = 'board'
	OUT = 'out'
	LOW = 'low'
	HIGH = 'high'

	def __init__(self) -> None:
		self.pinState:"dict[int,bool]" = {}	

	def setmode(self, input):
		print(f'setmode={input}')

	def setup(self, pins:"int|list[int]", io_direction, initial = 0):
		self.initial = initial

		if(isinstance(pins, int)):
			self.pinState[pins] = initial
		else:
			#Initalize all of the pins
			for pin in pins:
				self.pinState[pin] = initial
		
		print(f'pins={pins} io_direction={io_direction} initial={initial}')

	def output(self, pin, output) :
		self.pinState[pin] = self.initial == output
		print(f'pin={pin} output={output}')

	def cleanup(self):
		print('cleanup')

	def setwarnings(self, showWarning):
		print(f'Show warnings {showWarning}')

	def input(self, pin):
		if(pin in self.pinState):
			return self.pinState[pin] == self.initial
		else:
			raise Exception(f"Pin {pin} isn't being tracked")

	