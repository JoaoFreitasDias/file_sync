import argparse # to parse command line arguments
import shutil
import time
import logging
from pathlib import Path
import hashlib # to compute MD5 hash

def setup_log(log_file):
    """Set up logging to file and console."""
    log_file.parent.mkdir(parents=True, exist_ok=True) # making sure log folder exists BEFORE setting up logging
    logging.basicConfig(
        level=logging.INFO, # records general info about the program (saves or deletions)
        format="%(asctime)s - %(levelname)s - %(message)s", # defines log message format: date and time, log level, and message
        handlers=[
            logging.FileHandler(log_file), # saves log messages to log_file
            logging.StreamHandler() # prints log messages to console
        ]
    )

def get_md5(file_path):
    """Compute MD5 hash of a file to check for changes."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""): # reads file in binary mode 4KB chunks at a time
            hash_md5.update(chunk)
    return hash_md5.hexdigest() # returns MD5 hash as a hexadecimal string

def sync_folders(og_folder, cp_folder):
    """Synchronize original folder with replica."""
    og_folder = Path(og_folder)
    cp_folder = Path(cp_folder) 


    if not og_folder.exists(): # ensure source folder exists
        logging.error(f"Source folder does not exist: {og_folder}")
        return 
    
    if not cp_folder.exists(): # create a replica file if one does not exist yet
        Path(cp_folder).mkdir(parents=True, exist_ok=True)
        logging.info(f"Created replica folder: {cp_folder}")

    # Copy new and modified files
    for og_file in og_folder.rglob("*"):  # Recursively iterates through all files & folders
        cp_file = cp_folder / og_file.relative_to(og_folder)  # Finds relative path in og_file and adds to the cp

        if og_file.is_dir(): # ensures we are looking at folders
            cp_file.mkdir(parents=True, exist_ok=True) # creates cp_folder if it doesn't exist yet
        elif not cp_file.exists() or get_md5(og_file) != get_md5(cp_file): # Creates cp_file if it doesn't exist or if has been changed
            shutil.copy2(og_file, cp_file) # copies file
            logging.info(f"Copied: {og_file} -> {cp_file}") # writes log of the procedure

    # Remove extra files from replica
    for cp_file in cp_folder.rglob("*"): # goes through cp files and folders
        og_file = og_folder / cp_file.relative_to(cp_folder) # finds relative path in cp_folder and reconstructs it in og

        if cp_file.name == "log.txt": # Do not delete log file (to keep it saved in the replica folder)
            continue  

        if not og_file.exists(): # check if it exists in og
            if cp_file.is_file():
                cp_file.unlink()  # if not, delete file
                logging.info(f"Deleted: {cp_file}")
            elif cp_file.is_dir():
                shutil.rmtree(cp_file)  # Delete folder and its contents
                logging.info(f"Deleted folder: {cp_file}")

def main():
    """
    example:
    python filename.py /path/to/original /path/to/where_you_want_the_replica 60 

    """
    parser = argparse.ArgumentParser(description="Folder Synchronization Tool") # Creates a command-line parser for handling user input
    parser.add_argument("source", help="Path to source folder")
    parser.add_argument("replica", help="Path to replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")

    args = parser.parse_args()

    source_folder = Path(args.source)
    parent_folder = Path(args.replica)  

    replica_folder = parent_folder / f"{source_folder.name}_copy"

    log_file = replica_folder / "log.txt"

    replica_folder.mkdir(parents=True, exist_ok=True) # Ensure the replica folder exists
  
    setup_log(log_file)  # Initialize logging inside the correct directory
    logging.info("Starting folder synchronization...")
    while True:
        sync_folders(source_folder, replica_folder)
        logging.info("Synchronization completed. Waiting for next cycle...")
        time.sleep(args.interval) # repeating sync every *interval* seconds

if __name__ == "__main__": # making sure script only runs when executed.
    main()
