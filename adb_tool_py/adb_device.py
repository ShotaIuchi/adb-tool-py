class AdbDevice:
    """
    A class to represent an Android device with a specific serial number.
    """

    def __init__(self, serial: str = None):
        """
        Initializes the AdbDevice class.

        :param serial: The serial number of the Android device, defaults to None.
        """
        self.serial: str = serial
