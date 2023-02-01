class DeviceController:
    def __init__(self) -> None:
        pass
    def on(self):
        pass
    def off(self):
        pass
    def isOn(self)-> bool:
        pass
    
    @staticmethod
    def getController(type:str, pin:int, address:int = None, i2cBus = None, GPIO = None, useBoardPins:bool = None):
        """_summary_

        Args:
            type (str): _description_
            pin (int, optional): Pin on the board when using GPIO, otherwise it's the position of the relay when using i2c.
            address (int, optional): _description_. Defaults to None.
            i2cBus (_type_, optional): _description_. Defaults to None.
            GPIO (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
            Exception: _description_
            Exception: _description_
            Exception: _description_

        Returns:
            _type_: _description_
        """
        
        from IO.GpioController import GpioController
        from IO.I2cController import I2cController

        if(type == "I2cController"):
            if(pin == None):
                raise Exception(f"pin / relay position is required for type {type}")
            if(i2cBus == None):
                raise Exception(f"i2cBus is required for type {type}")
            if(address == None):
                raise Exception(f"address is required for type {type}")            

            return I2cController(pin, address, i2cBus)

        elif(type == "GpioController"):
            if(pin == None):
                raise Exception(f"pin / relay position is required for type {type}")
            if(useBoardPins == None):
                raise Exception(f"useBoardPins is required for type {type}. This tells me to use the board pin number or GPIO number.")
            if(GPIO == None):
                raise Exception(f"GPIO is required for type {type}")
                
            return GpioController(GPIO, pin, useBoardPins)
        else:
            raise Exception(f"Unknown controller type '{type}'")
