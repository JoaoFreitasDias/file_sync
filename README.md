# File Sync

A Python script to synchronize two folders by copying new and modified files from a source folder to a replica folder. It also removes files that no longer exist in the source folder.

## Features
- Synchronizes files between two directories.
- Supports continuous syncing with adjustable intervals.
- Handles new, modified, and deleted files.
- Logs synchronization details to a log file.

## Installation

1. Ensure you have Python 3.x installed on your machine.
2. Clone or download the repository containing the `file_sync.py` script.

## Usage

To sync two folders, run the following command in your terminal:

```bash
python path\to\file_sync.py path\to\original path\to\replica 60

