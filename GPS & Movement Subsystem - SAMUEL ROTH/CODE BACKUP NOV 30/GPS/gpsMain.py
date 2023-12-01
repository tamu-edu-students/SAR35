#ECEN 403
#Samuel Roth, Sep 25, 2023
#Function to take in GPS data and output coordinates

#imports
import gpsFunctions

def mainGPS():

    # get data from file
    gpsData = gpsFunctions.gpsFileRead()

    # get error data, output below
    errorData = gpsFunctions.errorCorrection(gpsData)
    #slope, intercept, r_value, p_value, std_err


    #get output coordinates to return
    x_in = gpsData[len(gpsData)-1][0]
    y_in = gpsData[len(gpsData)-1][1]
    return (gpsFunctions.sampleToPoint(x_in,y_in,errorData[0],errorData[1]))

def plotGPS():

    # get data from file
    gpsData = gpsFunctions.gpsFileRead()

    # get error data, output below
    errorData = gpsFunctions.errorCorrection(gpsData)
    #slope, intercept, r_value, p_value, std_err


    #get output coordinates to return
    x_in = gpsData[len(gpsData)-1][0]
    y_in = gpsData[len(gpsData)-1][1]
    output = (gpsFunctions.sampleToPoint(x_in,y_in,errorData[0],errorData[1]))

    #plot the data
    gpsFunctions.gpsPlotALL(errorData[0],errorData[1],gpsData,output[0],output[1]) #plot all
