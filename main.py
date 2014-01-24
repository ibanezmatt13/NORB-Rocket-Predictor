import numpy
import matplotlib.pyplot
 
g = 9.81 # m/s^2
time_step = 0.1 # s
peaked = False
burnout = False
 
motor_thrust = [2.569,9.369,17.275,24.285,29.73,27.01,22.58,17.99,14.126,12.099,10.808,9.876,9.306,9.105,8.901,8.698,8.31,8.294,4.613]
motor_times = [0.049,0.116,0.184,0.237,0.282,0.297,0.311,0.322,0.348,0.386,0.442,0.546,0.718,0.879,1.066,1.257,1.436,1.59,1.612]

class flight_path:
 
    def __init__(self):
        self.time = []
        self.altitude = []
        self.velocity = []
        self.drag = []
 
    def add_rocket_position(self, time, altitude, velocity, drag):
        self.time.append(time)
        self.altitude.append(altitude)
        self.velocity.append(velocity)
        self.drag.append(drag)
 
 
def estimate_thrust(current_time):
    global burnout
    
    for i in range(0, len(motor_times)):
        if motor_times[i] >= current_time:
            min_thrust = motor_thrust[i-1]
            max_thrust = motor_thrust[i]
            estimated_thrust = (max_thrust + min_thrust) / 2.

            break
        else:
            if burnout == False:
                burnout = True
                print "Motor burnout"
            estimated_thrust = 0.

 
    return estimated_thrust
 
 
 
def calculate(mass, frontal_area, drag_coefficient):

    min_thrust = 0.
    max_thrust = 0.
 
    peak_altitude = 0.
    current_altitude = 0.
    current_time = 0.
    current_velocity = 0.
    current_drag = 0.
    peak_time = 0.
 
    # used for pressure model calculations
    temperature = 0.
    pressure = 0.
    air_density = 0.
 
 
    current_flightpath = flight_path() # create flightpath object
 
    counter = 0
 
    while current_altitude > 0 or counter == 0:

        estimated_thrust = estimate_thrust(current_time)
            
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
        
        if current_altitude > peak_altitude and not peaked:
            peak_altitude = current_altitude
            peak_time = current_time
            
        if current_altitude > 0.:
            current_flightpath.add_rocket_position(current_time, current_altitude, current_velocity, current_drag)
 
        counter += 1
        current_time = current_time + time_step
 
    return peak_altitude, peak_time, current_flightpath
 
def plot(peak_alt, peak_time, flightpath):

    print "Apogee: " + str(peak_alt)
    
    time = numpy.asarray(flightpath.time)
    altitude = numpy.asarray(flightpath.altitude)
    drag = numpy.asarray(flightpath.drag)
 
    axes_drag = matplotlib.pyplot.subplot(212)
    matplotlib.pyplot.plot(time, drag, linewidth=2)
 
    axes_height = matplotlib.pyplot.subplot(211)
    matplotlib.pyplot.plot(time, altitude,'r-',linewidth=2)
 
    axes_height.set_ylabel('Height in m')
    axes_height.set_title("Apogee: " + str(peak_alt) + "m at time: " + str(peak_time) + " seconds")
 
    axes_drag.set_xlabel('Time in s')
    axes_drag.set_ylabel('Drag')
    #matplotlib.pyplot.axvline(x=peak_time, ymin=0, ymax=peak_alt / max(axes_height), linewidth=4)
    matplotlib.pyplot.show()
 
 
def query_user():
    mass = float(raw_input("Rocket mass: "))
    frontal_area = float(raw_input("Frontal area of rocket: "))
    drag_coefficient = float(raw_input("Coefficient of drag: "))
    
    run(mass, frontal_area, drag_coefficient)
 
def run(mass, frontal_area, drag_coefficient):
 
    peak_alt, peak_time, flightpath = calculate(mass, frontal_area, drag_coefficient)
    peak_alt = round(peak_alt, 2)
    plot(peak_alt, peak_time, flightpath)
 
 
query_user()
