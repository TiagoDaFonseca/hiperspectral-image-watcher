from distutils.log import INFO
import sys
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import hsi
import os
import shutil
from mongo import DB, test_connection
import shutil
from joblib import Parallel, delayed
from typing import Dict, Any
import os

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S' )

MONITOR_PATH = "C:/hsi_data/ToProcess"
RESULTS_PATH = "C:/hsi_data/Results"

CACHE: Dict[str, Any] = {}


def process_vegetation(path: str, filename: str, altitude_ref=None):
    global CACHE
    
    output: dict = {}
    
    
    info = path.split("\\")
    crop = info[-3]

    
    cube, metadata = hsi.load_image(path, filename)
    pred = CACHE['ml_model'].classify(cube)
    
    # Coordinates
    
    tiff_file = filename.split(".")[0] + ".tiff"
    coord: dict = {}
    try:
        coord = hsi.extract_coordinates(os.path.join(path, tiff_file))
    except FileNotFoundError:
        return None

    if altitude_ref is not None:
        coord["altitude"] = coord["altitude"] - altitude_ref
    coord["altitude units"] = "m"
    
    
    output["filename"] = filename.split(".")[0]
    output["crop"] = crop
    output["location"] = coord
    
    # vigour
    result = hsi.estimate_severity_level(cube)
    avg, std = hsi.estimate_average(result, mask=pred)
    output["severity avg"] = avg
    output["severity std"] = std
    
    # NDVI705
    result = hsi.VIndexer(cube).get_index('ndvi705')
    avg, std = hsi.estimate_average(result, mask=pred)
    output["ndvi705 avg"] = avg
    output["ndvi705 std"] = std
    
    # MSR705
    result = hsi.VIndexer(cube).get_index('msr705')
    avg, std = hsi.estimate_average(result, mask=pred)
    output["msr705 avg"] = avg
    output["msr705 std"] = std
    
    # PSRI
    result = hsi.VIndexer(cube).get_index('psri')
    avg, std = hsi.estimate_average(result, mask=pred)
    output["psri avg"] = avg
    output["psri std"] = std
    
    # SIPI
    result = hsi.VIndexer(cube).get_index('sipi')
    avg, std = hsi.estimate_average(result, mask=pred)
    output["sipi avg"] = avg
    output["sipi std"] = std
    
    # REP
    result = hsi.VIndexer(cube).get_index('rep')
    avg, std = hsi.estimate_average(result, mask=pred)
    output["rep avg"] = avg
    output["rep std"] = std
    
    info = metadata["description"].split(",\n")
    output["date"] = info[0].split("Date: ")[-1]
    output["time"] = info[1].split("Time: ")[-1]
    
    return output


def on_created(event):
    logging.info("Image detected.")
    if "calibration" in event.src_path and "preview" not in event.src_path:
        base_dir = event.src_path.split("calibration")[0]
        envi_files = tiff_files = []
        try:
            envi_files = [f for f in os.listdir(base_dir) if ".cue" in f and "._" not in f]
            tiff_files = [f for f in os.listdir(base_dir) if ".tiff" in f and "preview" not in f and "._" not in f]
        except FileNotFoundError:
            return 

        ground_ref = hsi.extract_coordinates(event.src_path)

        if 'ml_model' not in CACHE:
            ml_model = hsi.load_model("vegetation-clf.joblib")
            CACHE['ml_model'] = ml_model
        
        logging.info("Start processing...")

        results = Parallel(n_jobs=-2)(delayed(process_vegetation)(base_dir, envi_file, altitude_ref=ground_ref["altitude"]) for envi_file in envi_files)

        # Do whatever with results
        db = DB()
        connected = test_connection()
        if connected == True:
            logging.info("Save to DB")
            db.insert_many([result for result in results])
        else:
            logging.warning("Save to disk")
            Parallel(n_jobs=4)(delayed(hsi.save_json)(result, RESULTS_PATH) for result in results)

        # remove folder
        try:
            shutil.rmtree(event.src_path.split("calibration")[0])
            logging.info("Folder deleted.")
        except FileNotFoundError:
            return
    #print(f"hey, {event.src_path} has been created!")

def start_service():
    logging.info("Initiating filesystem monitoring.")
    patterns = ["*.cue", "*.tiff"]
    ignore_patterns = None
    ignore_directories = True
    case_sensitive = True
    event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    event_handler.on_created = on_created

    observer = Observer()
    observer.schedule(event_handler, MONITOR_PATH, recursive=True)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    start_service()