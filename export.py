#!/bin/env python3
import os

from lib.viv import export_viv, import_viv

configs = [
	{
		"iso":						"files/Battlefield 2 - Modern Combat (USA).iso",
		"output_directory":			"output/US/",
	},
]

def main():
	for config in configs:
		for root, dirs, files in os.walk("{}/iso/".format(config["output_directory"])):
			for file in files:
				if file.endswith('.viv') or file.endswith('.VIV'):
					input_file_path = os.path.join(root, file)
					output_files_path = f"{input_file_path}_FILES/"
					
					print("Export \"{}\"".format(input_file_path))
					export_viv(input_file_path, output_files_path)
					print("Done!")

main()