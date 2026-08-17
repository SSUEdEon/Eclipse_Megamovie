from astropy.io import fits
import numpy as np
import rawpy
import csv
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

'''
    ~Outline~
    - a csv is created with makeSheet.ps1 that contains metadata for each tier 2 observatory's images
    - this script reads that csv, opens each image, and updates the FITS header with the metadata
    - the updated FITS files are saved to a new directory
'''

obs = 'R_5Ys7VVhYIjOGiZ3'

csvFile = f"{obs}_tier2.csv"

def calculate_date_beg(date_utc_str, exposure_time_str):
    date_utc = datetime.strptime(date_utc_str, '%Y:%m:%d %H:%M:%SZ')
    exp_sec = eval(exposure_time_str) if '/' in exposure_time_str else float(exposure_time_str)
    date_beg = date_utc - timedelta(seconds=exp_sec / 2)
    return date_beg.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def getHeaderInfo(observatoryName, imageName):
    lighcsvFile = 'data/lights_data.csv'
    obscsvFile = 'data/observatory_data.csv'
    with open(lighcsvFile, mode='r') as file:
        csvReader = csv.DictReader(file)
        for row in csvReader:
            if row['ImageName'] == imageName:
                data = {
                    'SIMPLE': True,
                    'BITPIX': getBITPIX(os.path.join(obs, imageName)),
                    'NAXIS': 2,
                    'NAXIS1': row['ImageWidth'],
                    'NAXIS2': row['ImageHeight'],
                    'LONGSTRN': 'OGIP 1.0',
                    'EXTEND': True,
                    'PROJECT': 'Eclipse Megamovie',
                    'TITLE': 'Eclipse Megamovie Level 2 image data',
                    'KEYVOCAB': 'astrothesaurus.org/thesaurus/',
                    'KEYWORDS': 'Solar corona, Eclipse, Astronomy, Sun',
                    'LICENSE': 'CC BY-SA 4.0',
                    'FILE_RAW': imageName,
                    'FILENAME': Path(imageName).with_suffix('.fits').name,
                    'LEVEL': 2,
                    'OBSTYPE': 'Ground-based Volunteer-Photographer Observatory',
                    'PIPEVRSN': '1.0.0',
                    'ORIGIN': 'Sonoma State University',
                    'TIMESYS': 'UTC',
                    'DATE-BEG': calculate_date_beg(row['DateTimeUTC'], row['ExifExposureTime']),
                    'DATE-OBS': row['DateTimeUTC'],
                    'DATE-FILE': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    'TELESCOP': row['CameraMake'] + ' ' + row['CameraModel'],
                    'OBJECT': 'White-light Corona',
                    'WCSAXES': 2,
                    'TELAPSE': row['ExifExposureTime'],
                    'INSTRUME': row['LensDiameter'] + ' ' + row['FocalLength'] + ' ' + row['FNumber'],
                    'XFBYTES': row['FileSize'],
                    'COMPRESS': row['CompressionType'],
                    #this is going to have to be done after cause this information is from observatory data
                    'COMMENT': '',
                    'OBSGEO-L': row['Longitude'],
                    'OBSGEO-B': row['Latitude'],
                    'FOCALLEN': row['FocalLength'],
                    'FNUMBER': row['FNumber'],
                    'APTDIA': row['LensDiameter'], #this might be wrong
                    'EXPTIME': row['ExifExposureTime'],
                    'ISOSPEED': row['ExifISO'],
                    'SENSWID': row['SensorSize'].split(' x ')[0],
                    'SENSHGT': row['SensorSize'].split(' x ')[1],
                    'WHTBAL': row['WhiteBalance'],
                    'AMBTEMP': row['AmbientTemperature'],
                    'IMAGEW': row['ImageWidth'],
                    'IMAGEH': row['ImageHeight'],
                    'RAWBITS': getRawBits(os.path.join(obs, imageName)),
                    #END
                }
                file.close()
                break

    with open(obscsvFile, mode='r') as file:
        csvReader = csv.DictReader(file)
        for row in csvReader:
            if row['ResponseID'] == observatoryName:
                data['COMMENT'] = 'Flats Notes: ' + row['FlatsProcess'] + ' Darks Notes: '  + row['DarksProcess'] + ' Issues: ' + row['IssueNotes'] + ' ISO Notes: ' + row['GS_ISO_Notes'] + ' Exposure Notes: ' + row['GS_Exposure_Notes'] + ' Tracking Notes: ' + row['GS_Tracking_Notes'] + ' Equipment Notes: ' + row['EquipmentUsed_Notes']
                file.close()
                break
    return data


def readCSV(csvFile, imageName):
    data = {}
    with open(csvFile, mode='r') as file:
        csvReader = csv.DictReader(file)
        for row in csvReader:
            if row['FILE_RAW'] == imageName:
                return row
    return None


def getBITPIX(imagePath):
    with rawpy.imread(imagePath) as raw:
        # Get the bit depth from the raw image data type
        imgData = raw.raw_image
        bitDepth = imgData.dtype.itemsize * 8  # Convert bytes to bits
    if bitDepth <= 8:
        return 8
    elif bitDepth <= 16:
        return 16
    elif bitDepth <= 32:
        return 32
    else:
        return 64

def getRawBits(imagePath):
    with rawpy.imread(imagePath) as raw:
        # Get the bit depth from the raw image data type
        imgData = raw.raw_image
        return imgData.dtype.itemsize * 8  # Convert bytes to bits

def createFITS(imagePath, headerData, savePath):
    with rawpy.imread(imagePath) as raw:
        imgData = raw.raw_image.copy()

    # Ensure the data is in the correct format for FITS
    if imgData.dtype == np.uint8:
        bitpix = 8
    elif imgData.dtype == np.uint16:
        bitpix = 16
    elif imgData.dtype == np.uint32:
        bitpix = 32
    elif imgData.dtype == np.int16:
        bitpix = 16
    elif imgData.dtype == np.int32:
        bitpix = 32
    else:
        # Convert to uint16 if it's an unexpected type
        imgData = imgData.astype(np.uint16)
        bitpix = 16

    # Create a FITS header and populate it with metadata
    header = fits.Header()
    header['SIMPLE'] = headerData['SIMPLE']
    header['BITPIX'] = bitpix
    header['NAXIS'] = imgData.ndim
    header['NAXIS1'] = imgData.shape[1]
    header['NAXIS2'] = imgData.shape[0]
    header['LONGSTRN'] = headerData['LONGSTRN']
    header['EXTEND'] = headerData['EXTEND']
    header['PROJECT'] = headerData['PROJECT']
    header['TITLE'] = headerData['TITLE']
    header['KEYVOCAB'] = headerData['KEYVOCAB']
    header['KEYWORDS'] = headerData['KEYWORDS']
    header['LICENSE'] = headerData['LICENSE']
    header['FILENAME'] = headerData['FILENAME']
    header['LEVEL'] = headerData['LEVEL']
    header['OBSTYPE'] = headerData['OBSTYPE']
    header['PIPEVRSN'] = headerData['PIPEVRSN']
    header['ORIGIN'] = headerData['ORIGIN']
    header['TIMESYS'] = headerData['TIMESYS']
    header['DATE-BEG'] = headerData['DATE-BEG']
    header['DATE-OBS'] = headerData['DATE-OBS']
    header['DATE-FILE'] = headerData['DATE-FILE']
    header['TELESCOP'] = headerData['TELESCOP']
    header['OBJECT'] = headerData['OBJECT']
    header['WCSAXES'] = headerData['WCSAXES']
    header['TELAPSE'] = headerData['TELAPSE']
    header['INSTRUME'] = headerData['INSTRUME']
    header['XFBYTES'] = headerData['XFBYTES']
    header['COMPRESS'] = headerData['COMPRESS']
    header['COMMENT'] = headerData['COMMENT']
    header['OBSGEO-L'] = headerData['OBSGEO-L']
    header['OBSGEO-B'] = headerData['OBSGEO-B']
    header['FOCALLEN'] = headerData['FOCALLEN']
    header['FNUMBER'] = headerData['FNUMBER']
    header['APTDIA'] = headerData['APTDIA']
    header['EXPTIME'] = headerData['EXPTIME']
    header['ISOSPEED'] = headerData['ISOSPEED']
    header['SENSWID'] = headerData['SENSWID']
    header['SENSHGT'] = headerData['SENSHGT']
    header['WHTBAL'] = headerData['WHTBAL']
    header['AMBTEMP'] = headerData['AMBTEMP']
    header['IMAGEW'] = headerData['IMAGEW']
    header['IMAGEH'] = headerData['IMAGEH']
    header['FILE_RAW'] = headerData['FILE_RAW']
    header['RAWBITS'] = imgData.dtype.itemsize * 8 

    # Create a PrimaryHDU object
    hdu = fits.PrimaryHDU(data=imgData, header=header)
    # Write the FITS file to disk
    hdu.writeto(savePath, overwrite=True)
    print(f"FITS file saved to {savePath}")

    #read the FITS file back to verify
    with fits.open(savePath) as hdul:
        hdul.info()
        print(repr(hdul[0].header))

if __name__ == "__main__":
    
    #Would need to route to ../images/<observatory>/Light/<image>
    #and also write to ../images/<observatory>/level2/<image>.fits
    
    imageNames = os.listdir(obs)

    for image in imageNames:
        print(image)
        print(os.path.join(obs, image))
        # data = readCSV(csvFile, image)
        data = getHeaderInfo(obs, image)
        print(data)
        savePath = os.path.join(f"{obs}_fits", f"{os.path.splitext(image)[0]}.fits")
        createFITS(os.path.join(obs, image), data, savePath)
        print('----------------------------------------')