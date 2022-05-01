#Class stub of Pi GPIO for doing testing.
class GpioStub:
	BOARD = 'board'
	OUT = 'out'
	LOW = 'low'
	HIGH = 'high'
	def setmode(self, input):
		print(f'setmode={input}')
	def setup(self, pins, io_direction,initial):
		print(f'pins={pins} io_direction={io_direction} initial={initial}')
	def output(self, pin, output) :
		print(f'pin={pin} output={output}')
	def cleanup(self):
		print('cleanup')
	def setwarnings(self, showWarning):
		print(f'Show warnings {showWarning}')