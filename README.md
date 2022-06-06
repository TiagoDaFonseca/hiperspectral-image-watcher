# Hiperspectral Image Watcher

Simple app that monitors a specific folder for hyperspectral data to process. This aplication intends to process automatically all hyperspectral data that are present within a specific folder,whose results are meant to be added and presented.

## The solution

The solution comprises two main blocks: the HSI Processor and a NoSQL database (MongoDB). An Observer object is monitoring a folder where the files to be analysed are copied following this structure:

- /FolderToProcess
    - potato
        - put/your/folder/here
            - calibration (this folder must have this exact name. Put inside the white and dark references in multyi-channel tiff format)
            - {All *.cue, *.tiff and *.hdr files}
    - {other crop}
        (... and so on ...)

It is important to remind the .cu3 images must be exported using the Cubert software a priori to the formats mentioned above (with reflectance output). The HSI Processor aims to detect files were created and need to be processed. However, this service will start processing only detects the calibration folder.

## How-To

To run the HSi Processor:

1. Clone this repo to your computer
2. Open folder with terminal
3. Create a virtual environment

```
virtualenv hsi_env
```
4. Activate environment if needed
```
source hsi_env/bin/activate
```
5. Install the required packages
```
pip install -r requirements.txt
```
6. Run service 
```
python watcher.py
```

The output of this process is a list of json files that may now be saved to a database or to disk. Example:

```
{
    "_id": {
        "$oid": "627d163f38e22b2ef03a99fd"
    },
    "filename": "session_40m_000_188_RAW",
    "crop": "potato",
    "location": {
        "latitude": [39, 28, 40.03200175131788],
        "latitude ref": "N",
        "longitude": [9, 9, 52.19400025702247],
        "longitude ref": "W",
        "altitude": 8.599998640341255,
        "altitude units": "m"
    },
    "severity avg": 2.4472296317587676,
    "severity std": 0.7559692509964003,
    "ndvi705 avg": 0.6235305751574678,
    "ndvi705 std": 0.054641662319166076,
    "msr705 avg": 5.143021550293102,
    "msr705 std": 1.234081122643313,
    "psri avg": 0.02764406510208588,
    "psri std": 0.02014878075877713,
    "sipi avg": 1.081992868749058,
    "sipi std": 0.032991760878893064,
    "rep avg": 717.920631282944,
    "rep std": 3.171064355091942,
    "date": "2022-04-28",
    "time": "13:02:10.922GMT Summer Time"
}
```

To easily create a database:

```
docker run --name mydb -p 0.0.0.0:27017:27017 -v "C:/Mongo/data/db":/data/db -d mongo:latest 
```

One can confirm that database is up either checking docker logs:
![docker logs](/resources/docker-1.png)

or using the MongoDB Compass Software:
![compass](/resources/compass.png)


The user must define the folder that should be monitored and the folder to store results in case the database is down:
```
MONITOR_PATH = "C:/hsi_data/ToProcess"
RESULTS_PATH = "C:/hsi_data/Results"

```

