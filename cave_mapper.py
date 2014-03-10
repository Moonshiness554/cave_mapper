import RPi.GPIO as GPIO
from time import time, sleep

GPIO.setmode(GPIO.BOARD)

# pin names
SRV_SWITCH_PIN = 7
SRV_IN1_PIN = 11
SRV_IN2_PIN = 12
SRV_IN3_PIN = 13
SRV_IN4_PIN = 15
MEASURE_PIN = 16
UNIT_SWITCH_PIN = 18
POWER_PIN = 22

# global variables
VERT_SERVO = 1
HORZ_SERVO = 2
oneDegreeVerticalRotationRatio = 10
oneDegreeHorizontalRotationRatio = 56
pictfilename = "distance_reading.jpg"
datafilename = "3d_map_data"
current_horz_degree = 0
current_vert_degree = 90    # lidar is pointing up at startup

# servo has to go through this sequence to make 1 rotation
stepCount = 4
stepPins = [SRV_IN1_PIN,SRV_IN2_PIN,SRV_IN3_PIN,SRV_IN4_PIN]

# HELPER METHODS used in the main program
#==================================================
def lidarOn():
  GPIO.output(POWER_PIN, False)
  sleep(2)
  GPIO.output(POWER_PIN, True)
  sleep(2)

def lidarOff():
  lidarOn()

def lidarChangeUnits():
  slp = 0.5
  GPIO.output(UNIT_SWITCH_PIN, False)
  sleep(slp)
  GPIO.output(UNIT_SWITCH_PIN, True)
  sleep(slp)

def takePicture():
  #TODO
  return

def picToText():
  #TODO
  return

def extractDistanceFromText():
  #TODO
  return 0

def lidarMeasureDistance():
  slp = 0.24
  GPIO.output(MEASURE_PIN, False)
  sleep(slp)
  GPIO.output(MEASURE_PIN, True)
  sleep(slp+1)
  GPIO.output(MEASURE_PIN, False)
  sleep(slp)
  GPIO.output(MEASURE_PIN, True)
  GPIO.output(MEASURE_PIN, False)
  sleep(slp)
  GPIO.output(MEASURE_PIN, True)
  sleep(slp+1.3)

def readDistance():
  lidarMeasureDistance()
  takePicture()
  picToText()
  distance = extractDistanceFromText()
  return distance

def saveData(hDegree, vDegree, distance):
  with open(datafilename, "a") as myfile:
    data = str(hDegree) + "," + str(vDegree) + "," + str(distance) + "\n"
    myfile.write(data)
    print("\t"+data+"\n")

def prepareLidar():
  print("\tSetup Lidar pins")
  GPIO.setup(POWER_PIN, GPIO.OUT)
  GPIO.setup(UNIT_SWITCH_PIN, GPIO.OUT)
  GPIO.setup(MEASURE_PIN, GPIO.OUT)

  print("\tTurning Lidar ON\n")
  lidarOn()

  print("\tDo test read\n");
  lidarMeasureDistance()

  print("\tSwitching to feet\n")
  lidarChangeUnits()
  print("\tSwitching to meters\n")
  lidarChangeUnits()
  print("\tSwitching to millimeters\n")
  lidarChangeUnits()

def prepareServos():
  global stepPins
  print("\tSetup servo pins")
  GPIO.setup(SRV_SWITCH_PIN, GPIO.OUT)
  for pin in stepPins:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, False)

def rotate(seq, ratio):
  global stepPins
  for rotation in range(0, ratio):
    for step in range(0, 4):

      # reset all 4 servo pins to new settings in a sequence
      for pin in range(0, 4):
        xpin = stepPins[pin]
        if seq[step][pin] != 0:
          GPIO.output(xpin, True)
        else:
          GPIO.output(xpin, False)

      # Wait before moving on. This wait time is needed because
      # if we go too fast the servo will not rotate at all!!
      sleep(0.02)

def rotateVerticallyOneDegreeClockWise():
  global oneDegreeVerticalRotationRatio, current_vert_degree
  print ("\tTurn 1 degree vertically clockwise")
  clockWiseSeq = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
  rotate(clockWiseSeq, oneDegreeVerticalRotationRatio)
  current_vert_degree += 1

def rotateVerticallyOneDegreeCounterClockWise():
  global oneDegreeVerticalRotationRatio, current_vert_degree
  print ("\tTurn 1 degree vertically counter-clockwise")
  counterClockWiseSeq = [[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]]
  #counterClockWiseSeq = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
  rotate(counterClockWiseSeq, oneDegreeVerticalRotationRatio)
  current_vert_degree -= 1

def rotateHorizontallyOneDegree():
  global oneDegreeHorizontalRotationRatio, current_horz_degree
  print ("\tTurn 1 degree horizontally")
  clockWiseSeq = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
  rotate(clockWiseSeq, oneDegreeHorizontalRotationRatio)
  current_horz_degree += 1

def switchServos(servo_type):
  if(servo_type == HORZ_SERVO):
    GPIO.output(SRV_SWITCH_PIN, False)
  else:
    GPIO.output(SRV_SWITCH_PIN, True)



# MAIN PROGRAM
#==================================================
'''
now we're ready to run the program.
 Algorithm:
  - prepare servos
  - prepare lidar
  - do a full circle horizontal rotation (0, 360)
    - for each degree, rotate vertically 1 degree
    - measure
    - save the following data into file:
      - horizontal degree
      - vertical degree
      - distance
    - check if we rotated 90 degrees vertically and switch vertical rotation direction
    - repeat all the steps above
'''
try:
  prepareLidar()
  prepareServos()
  switchServos(VERT_SERVO)
  vertStart = 90
  vertEnd = 0
  vertStep = -1

  for hTurn in range (0, 360):
    switchServos(HORZ_SERVO)
    rotateHorizontallyOneDegree()
    switchServos(VERT_SERVO)

    for vTurn in range(vertStart, vertEnd, vertStep):
      if (vertStart == 0):
        rotateVerticallyOneDegreeClockWise();
      else:
        rotateVerticallyOneDegreeCounterClockWise();
      distance = 0 #readDistance()
      saveData(current_horz_degree, current_vert_degree, distance)

    if (vertStart == 0):
      # change to counter-clock wise direction
      vertStart = 90
      vertEnd = 0
      vertStep = -1
    else:
      # change to clock wise direction
      vertStart = 0
      vertEnd = 90
      vertStep = 1
finally:
  GPIO.cleanup()
