import numpy
import matplotlib.pyplot as plt
import sys
 
g = 9.81 # m/s^2
time_step = 0.01 # s
peaked = False
burnout = False

motor_thrust = []
motor_times = []

class flight_path:
 
    def __init__(self):
        self.time = []
        self.altitude = []
        self.velocity = []
        self.drag = []
        self.thrust = []
        self.burnout_time = 0.
        self.estimated_time = []
        self.burnout_alt = 0.
 
    def add_rocket_position(self, time, altitude, velocity, drag, thrust, burnout_time, estimated_time, burnout_alt):
        self.time.append(time)
        self.altitude.append(altitude)
        self.velocity.append(velocity)
        self.drag.append(drag)
        self.thrust.append(thrust)
        self.burnout_time = burnout_time
        self.estimated_time.append(estimated_time)
        self.burnout_alt = burnout_alt


def configure_motor(path, cluster):
    motor_file = open(path, "r")

    for line in motor_file:
        line = line.lstrip()
        split_line = line.split(" ")
        current_time = split_line[0]
        current_thrust = split_line[1]
        current_time = current_time.strip()
        current_thrust = current_thrust.strip()
        current_thrust = float(current_thrust)
        current_thrust = float(current_thrust * cluster)
        motor_times.append(float(current_time))
        motor_thrust.append(current_thrust)

    motor_file.close()

def find_motor(motor, cluster):

    found = False

    motors_list = open("C:/Python27/motors_list.txt", "r")
    for line in motors_list:
        line = line.lstrip()
        split_line = line.split(" ")
        current_motor = split_line[0]
        motor_path = split_line[1]
        current_motor = current_motor.strip()
        motor_path = motor_path.rstrip('\n')
        
        if current_motor == motor:
            found = True
            break
        
    motors_list.close()

    if found == True:
        configure_motor(motor_path, cluster)
        return True
    else:
        return False
        
 
def estimate_thrust(current_time):
    
    for i in range(0, len(motor_times)):
        if motor_times[i] >= current_time:
            if i == 0:
                min_time = 0.
            else:
                min_time = motor_times[i-1]
            min_thrust = motor_thrust[i-1]
            max_thrust = motor_thrust[i]
            max_time = motor_times[i]
            estimated_thrust = (max_thrust + min_thrust) / 2.
            estimated_time = (min_time + max_time) / 2
            break
        else:
            estimated_thrust = 0.
            estimated_time = current_time #no need to estimate as motor burnout reached

    return estimated_thrust, estimated_time
 
 
 
def calculate(mass, frontal_area, drag_coefficient):

    global burnout

    min_thrust = 0.
    max_thrust = 0.
 
    peak_altitude = 0.
    current_altitude = 0.
    current_time = 0.
    current_velocity = 0.
    current_drag = 0.
    peak_time = 0.
    burnout_time = 0.
    burnout_alt = 0.
 
    # used for pressure model calculations
    temperature = 0.
    pressure = 0.
    air_density = 0.
 
 
    current_flightpath = flight_path() # create flightpath object
 
    counter = 0
 
    while current_altitude > 0 or counter == 0:

        estimated_thrust, estimated_time = estimate_thrust(current_time)

        if estimated_thrust == 0 and burnout == False:
            burnout_time = current_time
            burnout_alt = current_altitude
            burnout = True
            
        # apply the appropriate pressure model calculations
        if current_altitude > 25000.:
            temperature = -131.21 + (.00299 * current_altitude)
            pressure = 2.488 * (((temperature + 273.1) / 216.6) ** -11.388)
            air_density = pressure / (.2869 * (temperature + 273.1))
        elif current_altitude >= 11000.:
            temperature = -56.46
            pressure = 22.65 * (10 ** (1.73 - (.000157 * current_altitude)))
            air_density = pressure / (.2869 * (temperature + 273.1))
        else:
            temperature = 15.04 - (.00649 * current_altitude)
            pressure = 101.29 * (((temperature + 273.1) / 288.08) ** 5.256)
            air_density = pressure / (.2869 * (temperature + 273.1))

        current_drag = (air_density / 2) * (current_velocity*abs(current_velocity)) * drag_coefficient * frontal_area
        current_velocity = current_velocity + (time_step * (-g + (float(-current_drag) + estimated_thrust) / mass))
        current_altitude = float(current_altitude + (current_velocity * time_step))

        if current_altitude < 0: # to prevent negative altitude
            current_altitude = 0
        
        if current_altitude > peak_altitude and not peaked:
            peak_altitude = current_altitude
            peak_time = current_time
            
        if current_altitude > 0.:
            current_flightpath.add_rocket_position(current_time, current_altitude, current_velocity, current_drag, estimated_thrust, burnout_time, estimated_time, burnout_alt)
 
        counter += 1
        current_time = current_time + time_step
 
    return peak_altitude, peak_time, current_flightpath
 
def plot(peak_alt, peak_time, flightpath):

    print "Apogee: " + str(peak_alt) + " metres at time: " + str(peak_time) + " seconds"
    print "Motor burnout at time: " + str(flightpath.burnout_time) + " seconds"
    time = numpy.asarray(flightpath.time)
    altitude = numpy.asarray(flightpath.altitude)
    drag = numpy.asarray(flightpath.drag)
    thrust = numpy.asarray(flightpath.thrust)

    figure = plt.figure()
    
    axes_drag = figure.add_subplot(3,1,2)
    plt.plot(time, drag, linewidth=2)
 
    axes_height = figure.add_subplot(3,1,1)
    plt.plot(time, altitude,'r-',linewidth=2)
    plt.vlines(x=peak_time, ymin=0, ymax=peak_alt, linewidth=2)
    plt.text(peak_time, peak_alt/2, "Apogee", horizontalalignment='center', fontsize=9)
    plt.vlines(x=flightpath.burnout_time, ymin=0, ymax=flightpath.burnout_alt,linewidth=2)
    plt.text(flightpath.burnout_time, peak_alt/2, "Motor\nburnout", horizontalalignment='center', fontsize=9)
    axes_thrust = figure.add_subplot(3,1,0)
    plt.plot(flightpath.estimated_time, thrust,'g-',linewidth=2)
 
    axes_height.set_ylabel('Altitude M')
    axes_height.set_title("Apogee: " + str(peak_alt) + "m at time: " + str(peak_time) + " seconds")
 
    axes_thrust.set_xlabel('Time S')
    axes_thrust.set_ylabel('Thrust N')
    axes_drag.set_ylabel('Drag N')
    
    plt.show()


def query_user():

    print """Available motor types:

             - Cesaroni F36 (F36)
             - Cesaroni G88 (G88)
             - Estes C11 (C11)
             - Estes D12 (D12)

When prompted, enter the engine identifier located in brackets
next to the engine type above

If you're clustering motors, you can only cluster motors of the same type\n\n"""
    
    mass = float(raw_input("Rocket mass: "))
    frontal_area = float(raw_input("Frontal area of rocket: "))
    drag_coefficient = float(raw_input("Coefficient of drag: "))
    motor = str(raw_input("Motor: "))
    cluster = int(raw_input("Num of motors: "))

    result = find_motor(motor, cluster)

    if result == True:
        run(mass, frontal_area, drag_coefficient)
    else:
        print "\n\nInvalid motor details...\n"
        response = raw_input("Enter R to retry or any other letter to exit: ")
        print "\n\n"
        if response == "R" or response == "r":
            query_user()
        else:
            sys.exit()
 
def run(mass, frontal_area, drag_coefficient):
 
    peak_alt, peak_time, flightpath = calculate(mass, frontal_area, drag_coefficient)
    peak_alt = round(peak_alt, 2)
    flight_duration = max(flightpath.time)
    print "Flight duration: " + str(flight_duration) + " seconds"
    plot(peak_alt, peak_time, flightpath)
    print motor_thrust[0]
 

query_user()
