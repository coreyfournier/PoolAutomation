import DependencyContainer
logger = DependencyContainer.get_logger(__name__)

#Class stub of Pi GPIO for doing testing.
class GpioStub():
	BOARD = 'board'
	OUT = 'out'
	LOW = 'low'
	HIGH = 'high'

	def __init__(self) -> None:
		self.pinState:"dict[int,bool]" = {}	

	def setmode(self, input):
		logger.debug(f'setmode={input}')

	def setup(self, pins:"int|list[int]", io_direction, initial = 0):
		self.initial = initial

		if(isinstance(pins, int)):
			self.pinState[pins] = initial
		else:
			#Initalize all of the pins
			for pin in pins:
				self.pinState[pin] = initial
		
		logger.debug(f'pins={pins} io_direction={io_direction} initial={initial}')

	def output(self, pin, output) :
		self.pinState[pin] = output
		logger.debug(f'pin={pin} output={output}')

	def cleanup(self):
		logger.debug('cleanup')

	def setwarnings(self, showWarning):
		logger.debug(f'Show warnings {showWarning}')

	def input(self, pin):
		if(pin in self.pinState):
			return self.pinState[pin]
		else:
			raise Exception(f"Pin {pin} isn't being tracked")

	