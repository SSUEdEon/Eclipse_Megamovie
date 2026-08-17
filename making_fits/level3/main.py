from astropy.io import fits
from PIL import Image
from datetime import datetime, timezone
import os
import numpy as np

ALL_OBS = [
    {
        "OBS_ID": "R_1yVFawatWSRzbIR",
        "START_IMAGE": "Reid_Piercey__DSC1568.fits",
        "START_TIME": "2024:04:08 18:26:53Z",
        "CENTER_IMAGE": "Reid_Piercey__DSC1750.fits",
        "CENTER_TIME": "2024:04:08 19:36:38Z",
        "HDR_PNG": "R_1yVFawatWSRzbIR_hdr_cropped_rotated.png"
    },
    {
        "OBS_ID": "R_2eJ8rlmbu9gZfGx",
        "START_IMAGE": "_DSF3919.fits",
        "START_TIME": "2024:04:08 18:12:11Z",
        "CENTER_IMAGE": "_DSF4011.fits",
        "CENTER_TIME": "2024:04:08 18:12:42Z",
        "HDR_PNG": "R_2eJ8rlmbu9gZfGx_hdr_cropped_rotated.png",
        "NUM_EXPOSURES": 27,
        "EXPOSURES": [0.0025, 0.004, 0.005, 0.00625, 0.008, 0.01, 0.0125, 0.016666666666666666, 0.02, 0.025, 0.03333333333333333, 0.04, 0.05, 0.06666666666666667, 0.07692307692307693, 0.1, 0.125, 0.16666666666666666, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5]
    },
    {
        "OBS_ID": "R_2eJITUgec9aZ3tT",
        "START_IMAGE": "Joseph_Lau__T5A5858.fits",
        "START_TIME": "2024:04:08 19:27:33Z",
        "CENTER_IMAGE": "Joseph_Lau__T5A5945.fits",
        "CENTER_TIME": "2024:04:08 19:28:27Z",
        "HDR_PNG": "R_2eJITUgec9aZ3tT_hdr_cropped_rotated.png",
        "NUM_EXPOSURES": 20,
        "EXPOSURES": [0.016666666666666666, 0.02, 0.025, 0.03333333333333333, 0.04, 0.05, 0.06666666666666667, 0.07692307692307693, 0.1, 0.125, 0.16666666666666666, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.3]
    },
    {
        "OBS_ID": "R_2N567ByNPmVeYlX",
    },
    {
        "OBS_ID": "R_2VI0MMRi64Nt7Vh",
    },
    {
        "OBS_ID": "R_3Bx2CUNjLFgm5Fk",
    },
    {
        "OBS_ID": "R_3hMaRJbigfcYCCS",
    },
    {
        "OBS_ID": "R_3QJppz1FmWGTrJV",
    },
    {
        "OBS_ID": "R_5fxKz4IrfpW3rJw",
    },
    {
        "OBS_ID": "R_5ktbk8cP73VRz0J",
    },
    {
        "OBS_ID": "R_5Lu33m0h2JlplZo",
    },
    {
        "OBS_ID": "R_5Ys7VVhYIjOGiZ3",
    },
    {
        "OBS_ID": "R_7CJbmiOaesRpo3u",
    },
    {        
        "OBS_ID": "R_7dmguWB4lzqoXo1",
    },
    {
        "OBS_ID": "R_7MlFvQlgFdmd7bE",
    },
    {
        "OBS_ID": "R_7MNxv0mAWexTPrj",
    },
    {
        "OBS_ID": "R_7Pc9Yj1CmydXAMu",
    },
    {
        "OBS_ID": "R_7qyw1YGEp1M4Lbf",
    },
    {
        "OBS_ID": "R_7widf3tT2X7GMe5",
    },
    {
        "OBS_ID": "R_7YLjOvnxB165utH",
    },
    {
        "OBS_ID": "R_8JeYUdjgdPLVK5k",
    },
    {
        "OBS_ID": "R_2SGDjrnCR5aeM81",
    },
    {
        "OBS_ID": "R_3pbbnI2n1DrxktA",
    },
    {
        "OBS_ID": "R_3YSotCMKmKXgOJ9",
    },
    {
        "OBS_ID": "R_5nml1TKUyGSQLfz",
    },
    {
        "OBS_ID": "R_6l6RontJBmArhV7",
    },
    {
        "OBS_ID": "R_7KsfdIvQjwlJeGn",
    },
]

def open_fits_file(filename):
    """Open a FITS file and return the HDU list."""
    hdu_list = fits.open(filename)
    hdu_list_copy = hdu_list.copy()
    hdu_list.close()
    return hdu_list_copy

def build_new_header(base_header, hdr, hdr_np, obs):
    """Build a new FITS header based on the base header."""
    new_header = fits.Header()
   
    HDR_PNG = f"{obs['OBS_ID']}/{obs['HDR_PNG']}"

    if "COMMENT" in base_header:
        for c in base_header['COMMENT']:
            text = str(c)
            text = text.replace('\n', ' ').replace('\r', ' ')
            text = text.encode('ascii', 'ignore').decode('ascii')
            text = text.strip()

            if text:
                new_header['COMMENT'] = text
            else:
                new_header['COMMENT'] = " "
   
    new_header['SIMPLE'] = base_header['SIMPLE']
    new_header['BITPIX'] = 16  # 16-bit unsigned integer
    new_header['NAXIS'] = 2
    new_header['NAXIS1'] = hdr_np.shape[1]  # width
    new_header['NAXIS2'] = hdr_np.shape[0]  # height
    new_header['LONGSTRN'] = base_header['LONGSTRN']
    new_header['PROJECT'] = base_header['PROJECT']
    new_header['TITLE'] = "Eclipse Megamovie Level 3 image data"
    new_header['KEYVOCAB'] = base_header['KEYVOCAB']
    new_header['KEYWORDS'] = base_header['KEYWORDS']
    new_header['LICENSE'] = base_header['LICENSE']
    new_header['FILENAME'] = "R_7CJbmiOaesRpo3u_1_level3.fits" #obs_id_level.fits
    new_header['LEVEL'] = 3
    new_header['OBSTYPE'] = base_header['OBSTYPE']
    new_header['PIPEVRSN'] = base_header['PIPEVRSN']
    new_header['ORIGIN'] = base_header['ORIGIN']
    new_header['TIMESYS'] = base_header['TIMESYS']
    new_header['DATE-BEG'] = obs["START_TIME"] #start time of observation
    new_header['DATE-OBS'] = obs["CENTER_TIME"] #center time of observation
    new_header['DATE-FILE'] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ") #now
    new_header['TELESCOP'] = base_header['TELESCOP']
    new_header['OBJECT'] = base_header['OBJECT']
    new_header['WCSAXES'] = base_header['WCSAXES']
    new_header['EXPTIME'] = 0.0
    new_header['INSTRUME'] = base_header['INSTRUME']
    new_header['XFBYTES'] = os.path.getsize(HDR_PNG) #size of file in bytes
    new_header['OBSGEO-L'] = base_header['OBSGEO-L']
    new_header['OBSGEO-B'] = base_header['OBSGEO-B']
    new_header['FOCALLEN'] = base_header['FOCALLEN']
    new_header['FNUMBER'] = base_header['FNUMBER']
    new_header['APTDIA'] = base_header['APTDIA'] #focal lenth / F number, Aperture diameter
    new_header['SENSWID'] = base_header['SENSWID']
    new_header['SENSHGT'] = base_header['SENSHGT']
    new_header['WHTBAL'] = base_header['WHTBAL']
    new_header['AMBTEMP'] = base_header['AMBTEMP']
    new_header['IMAGEW'] = hdr.width
    new_header['IMAGEH'] = hdr.height
    new_header['RAWBITS'] = base_header['RAWBITS']
    new_header['EXPTIME'] = 0

    # Calculate TELAPSE if START_TIME and END_TIME are available
    new_header['TELAPSE'] = obs["END_TIME"] - obs["START_TIME"]


    if "NUM_EXPOSURES" in obs:
        new_header['NCOMBINE'] = obs['NUM_EXPOSURES']
        for i, exp in enumerate(obs['EXPOSURES']):
            key = f'HDR{i+1:02d}_EXPT'
            new_header[key] = exp

    #END
    return new_header

def create_hdr_fits(output_filename, header, hdr):
    """Create a new FITS file with the given header and image data."""
    hdu = fits.PrimaryHDU(data=hdr, header=header)
    hdu.writeto(output_filename, overwrite=True)


def process_observation(obs):
    CURRENT_OBS = obs["OBS_ID"]
    FITSFILEIN = f"{CURRENT_OBS}/{obs['START_IMAGE']}"
    HDR_PNG = f"{CURRENT_OBS}/{obs['HDR_PNG']}"
    TIMESTART = obs["START_TIME"]
    TIMECENTER = obs["CENTER_TIME"]

    hdr = Image.open(HDR_PNG)
    
    if hdr.mode != 'L': #greyscale check
        hdr = hdr.convert('L')
    
    hdr_np = np.array(hdr)
    
    hdr_np = hdr_np.astype(np.uint16)

    hdu_list = open_fits_file(FITSFILEIN)

    base_header = hdu_list[0].header
    
    new_header = build_new_header(base_header, hdr, hdr_np, obs)

    output_filename = f"{CURRENT_OBS}/{CURRENT_OBS}_1_level3.fits"
    create_hdr_fits(output_filename, new_header, hdr_np)

if __name__ == "__main__":
    for obs in ALL_OBS:
        print(f"Processing observation {obs['OBS_ID']}...")
        process_observation(obs)