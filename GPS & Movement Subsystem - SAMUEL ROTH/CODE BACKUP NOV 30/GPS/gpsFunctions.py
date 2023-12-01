# ECEN 403
# Samuel Roth, Sep 25, 2023
# Functions file

#Read GPS file
def gpsFileRead():
    gpsData = []
    file_path = 'straightWalkEdit.txt'  # text file with GPS input data

    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Process each line of the file
                line = line.strip()  # Remove leading and trailing whitespaces

                lineElements = line.split(',')  # split each line into list

                if lineElements[0] == "$GPGGA":  # find essential data line

                    # get latitude and longitude data
                    latitude = float(lineElements[2][:2]) + float(lineElements[2][2:]) / 60
                    if lineElements[3] == 'S':
                        latitude = -latitude

                    longitude = float(lineElements[4][:3]) + float(lineElements[4][3:]) / 60
                    if lineElements[5] == 'W':
                        longitude = -longitude

                    gpsData.append([latitude, longitude])

    # file error handling
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print("An error occurred:", e)

    return gpsData

# Plot GPS coords
def gpsPlot(gpsData):
    import matplotlib.pyplot as plt

    x = []  # latitude
    y = []  # longitude

    for i in gpsData:
        x.append(i[0])
        y.append(i[1])

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot the data
    ax.plot(x, y, label='Example Line')

    # Add labels and a title
    ax.set_xlabel('X-axis Label')
    ax.set_ylabel('Y-axis Label')
    ax.set_title('Simple Line Plot')

    # Add a legend
    ax.legend()

    # Show the plot (you can also save it to a file with plt.savefig())
    plt.show()

#Plot function for all data
def gpsPlotALL(slope,intercept,gpsData,out_x,out_y):

    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np

    # Extract latitude and longitude values from the list of coordinates
    lats = []
    lons = []
    for i in gpsData:
        lats.append(i[0])
        lons.append(i[1])

    # Create a scatter plot of the points
    plt.scatter(lats, lons, label='Data Points', color='blue')
    #add best fit line
    plt.plot(lats, slope * np.array(lats) + intercept, color='red', label='Regression Line')
    #add output point
    plt.scatter(out_x, out_y, label='OUTPUT', color='green')

    # Set axis labels
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')

    #format axis data
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.6f'))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.6f'))

    # Add a legend
    plt.legend()

    # Display the plot
    plt.show()

# calculate bounding box
def gpsBox(gpsData):
    min_lat, max_lat = gpsData[0][0], gpsData[0][0]
    min_lon, max_lon = gpsData[0][1], gpsData[0][1]

    for i in gpsData:
        lat, lon = i
        min_lat = min(min_lat, lat)
        max_lat = max(max_lat, lat)
        min_lon = min(min_lon, lon)
        max_lon = max(max_lon, lon)

    return [min_lat, max_lat, min_lon, max_lon]

#regression fit line
def errorCorrection(gpsData):
    import numpy as np
    from scipy import stats

    lats = []
    lons = []
    for i in gpsData:
        lats.append(i[0])
        lons.append(i[1])

    slope, intercept, r_value, p_value, std_err = stats.linregress(lats,lons)

    return [slope, intercept, r_value, p_value, std_err]

#Returning a point on regression line closest to last GPS point
def sampleToPoint(x_in,y_in,r_slope,r_intersect):
    newSlope = (-1/r_slope)
    newB = y_in - (newSlope * x_in)
    r_goal_x = (r_intersect-newB) / (newSlope-r_slope)
    r_goal_y = (r_slope * r_goal_x) + r_intersect
    return [r_goal_x,r_goal_y] #the point on the regression line (output point)