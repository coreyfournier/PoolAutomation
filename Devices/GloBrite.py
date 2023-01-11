
import threading
import DependencyContainer
from Devices.DeviceController import DeviceController
logger = DependencyContainer.get_logger(__name__)

class GloBrite:
	def __init__(self, controller:DeviceController):	
		self.controller = controller
		self.lock = threading.Lock()

	@staticmethod
	def lightScenes() :		
		#[{Numer of times it needs to turn on and off}, {Name of the color},{Description}]
		return [
			[1, 'SAm Mode','Cycles through white, magenta, blue and green colors'],
			[2, 'Party Mode','Rapid color changing bulding energy and excitment'],
			[3, 'Romance Mode','Slow color transitions creating a mesmerizing and calming effect'],
			[4, 'Caribbean Mode','Transitions between a variety of blues and greens'],
			[5, 'American Mode','Patriotic red, white and blue transitions'],
			[6, 'California Sunset Mode','Dramatic transitions of orange, red and magenta tones'],
			[7, 'Royal Mode','Richer, deeper color tones'],
			[8, 'Blue','Fixed color Blue'],
			[9, 'Green','Fixed color Green'],
			[10,'Red','Fixed color Red'],
			[11,'White','Fixed color White'],
			[12,'Magenta','Fixed color Magenta'],
			[13,'Hold','Saved the current color effect during a color light show'],
			[14,'Recall', 'Activate the last saved color effect']
		]
		
	@staticmethod
	def sceneDescriptions():
		globrite_light_scenes = GloBrite.lightScenes()

		scene_description = ''
		for item in range(len(globrite_light_scenes)):
			scene_description += f'"{globrite_light_scenes[item][0]}" - {globrite_light_scenes[item][2]}'
			if(item + 1 < len(globrite_light_scenes)):
				scene_description += '; '

		return scene_description	

	def change(self, scene_index):
		globrite_light_scenes = GloBrite.lightScenes()
		selected_scene = globrite_light_scenes[scene_index]

		#ensure only one person can change the scene at a time
		with self.lock:
			logger.debug(f'switching {selected_scene[0]} times for scene "{selected_scene[1]}"')

			iterations = range(0,selected_scene[0])
			#If it's just one, it will turn on below
			if(len(iterations) > 1):
				for switch_flip in iterations:
					logger.debug(f'on') 
					self.controller.on()			
					logger.debug(f'off')
					self.controller.off()			

			#Always end with on
			logger.debug(f'on')
			self.controller.on()	
	

	#turns the pin off
	def off(self):		
		with self.lock:
			self.controller.off()