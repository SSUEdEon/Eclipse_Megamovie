# Read csv data from lights_data.csv and observatory_data.csv

$lights = Import-Csv -Path "data/lights_data.csv"
$observatories = Import-Csv -Path "data/observatory_data.csv"


<# -- Below is a list of observatories we've determined are good for tier 2 processing --
    [] R_1Jbdw0E8TUxdKWM ~
    [] R_1k82YexipD6hgbh
    [] R_1zdrnQVQUkXDHOV
    [] R_2eJ8rlmbu9gZfGx
    [] R_2eJITUgec9aZ3tT
    [] R_2rVr5UeXwodCGdR
    [] R_2VI0MMRi64Nt7Vh
    [] R_3Bx2CUNjLFgm5Fk
    [] R_3hMaRJbigfcYCCS
    [] R_3QJppz1FmWGTrJV
    [] R_5Lu33m0h2JlplZo
    [] R_7CJbmiOaesRpo3u
    [] R_7dmguWB4lzqoXo1
    [] R_7MlFvQlgFdmd7bE
    [] R_7RxE45DrFsGSyVx
    [] R_7widf3tT2X7GMe5
    [] R_5Ys7VVhYIjOGiZ3 ~
#> 

$obs = 'R_5Ys7VVhYIjOGiZ3'

$filteredLights = $lights | Where-Object { $_.ResponseID -eq $obs }
$ObservatoryLevelInfo = $observatories | Where-Object { $_.ResponseID -eq $obs }

Write-Output "Filtered Lights for Observatory ${obs}: $($filteredLights.Count) entries found."

$AllRows = @()

$filteredLights | ForEach-Object {

    $obsInfo = $ObservatoryLevelInfo | Where-Object { $_.ResponseID -eq $_.ResponseID }

    if ($_.FileSize.ToUpper() -match 'MB') {
        $sizeInMB = [double]($_.FileSize -replace '[^\d.]', '')
        $sizeInBytes = [int]($sizeInMB * 1MB)
        $_.FileSize = $sizeInBytes.ToString()
    }
    elseif ($_.FileSize.ToUpper() -match 'KB') {
        $sizeInKB = [double]($_.FileSize -replace '[^\d.]', '')
        $sizeInBytes = [int]($sizeInKB * 1KB)
        $_.FileSize = $sizeInBytes.ToString()
    }

    Write-Output $([System.IO.Path]::ChangeExtension($_.ImageName, '.fits'))
    Write-Output $_.ImageName

    # Write-Output "Light Entry: $_"
    $LightObject = New-Object PSObject -Property @{
        SIMPLE = $true
        BITPIX = 16 #This may need to be adjusted when processing the actual image data
        NAXIS = 2
        NAXIS1 = $_.ImageWidth
        NAXIS2 = $_.ImageHeight
        LONGSTRN = 'OGIP 1.0'
        EXTEND = $true
        PROJECT = 'Eclipse Megamovie'
        TITLE = 'Eclipse Megamovie Level 2 image data'
        KEYVOCAB = 'astrothesaurus.org/thesaurus/'
        KEYWORDS = 'Solar corona, Eclipse, Astronomy, Sun'
        LICENSE = 'CC BY-SA 4.0'
        FILENAME = [System.IO.Path]::ChangeExtension($_.ImageName, '.fits')
        FILE_RAW = $_.ImageName
        LEVEL = 2
        OBSTYPE = 'Ground-based Volunteer-Photographer Observatory'
        PIPEVRSN = '1.0.0'
        ORIGIN = 'Sonoma State University'
        TIMESYS = 'UTC'
        DATEBEG = ([DateTime]::ParseExact($_.DateTimeUTC, 'yyyy:MM:dd HH:mm:ssZ', $null)).AddSeconds(-([double](Invoke-Expression $_.ExifExposureTime)/2)).ToString('yyyy-MM-ddTHH:mm:ss.fffZ') #DATE-BEG
        DATEOBS = ([DateTime]::ParseExact($_.DateTimeUTC, 'yyyy:MM:dd HH:mm:ssZ', $null)).ToString('yyyy-MM-ddTHH:mm:ss.fffZ') #DATE-OBS
        DATEFILE = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ') #DATE-FILE
        TELESCOP = "$($_.CameraMake)" + ' ' + "$($_.CameraModel)"
        OBJECT = 'White-light Corona'
        WCSAXES = 2
        TELAPSE = $_.ExifExposureTime
        INSTRUME = "$($_.LensDiameter)" + ' ' + "$($_.FocalLength)" + ' ' + "$($_.FNumber)"
        XFBYTES = "$($_.FileSize)"
        COMPRESS = $_.CompressionType
        COMMENT = 'Flats Notes: ' + $obsInfo.FlatsProcess + ' Darks Notes: '  + $obsInfo.DarksProcess + ' Issues: ' + $obsInfo.IssueNotes + ' ISO Notes: ' + $obsInfo.GS_ISO_Notes + ' Exposure Notes: ' + $obsInfo.GS_Exposure_Notes + ' Tracking Notes: ' + $obsInfo.GS_Tracking_Notes + ' Equipment Notes: ' + $obsInfo.EquipmentUsed_Notes
        OBSGEOL = $_.Longitude #OBSGEO-L
        OBSGEOB = $_.Latitude #OBSGEO-B
        FOCALLEN = "$($_.FocalLength)"
        FNUMBER = "$($_.FNumber)"
        APTDIA = ([double]($_.FocalLength -replace '[^\d.]', '')) / ([double]($_.FNumber -replace '[^\d.]', ''))
        EXPTIME = $_.ExifExposureTime
        ISOSPEED = $_.ExifISO
        SENSWID = ($_.SensorSize -split ' x ')[0]
        SENSHGT = ($_.SensorSize -split ' x ')[1]
        WHTBAL = $_.WhiteBalance
        AMBTEMP = $_.AmbientTemperature
        IMAGEW = $_.ImageWidth
        IMAGEH = $_.ImageHeight
        RAWBITS = "$($_.BitsPerPixel)"
        #END
    }

    $AllRows += $LightObject
}

$AllRows | Export-Csv -Path "./${obs}_tier2.csv" -NoTypeInformation -Append