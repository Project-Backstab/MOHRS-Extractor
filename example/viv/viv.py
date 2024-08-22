#!/bin/env python3

import os
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from lib.viv import export_viv, import_viv

def test_viv(input_file_path, output_files_path, output_file_path):
	print(f"export \"{input_file_path}\" -> \"{output_files_path}\"")
	export_viv(input_file_path, output_files_path)
	print("Done!")
	
	print(f"import \"{output_files_path}\" -> \"{output_file_path}\"")
	import_viv(output_files_path, output_file_path)
	print("Done!")
	
	os.system(f"sha256sum {input_file_path}")
	os.system(f"sha256sum {output_file_path}")

def main():
	test_viv("files/LBOARD.VIV", "output/LBOARD.VIV/", "output/LBOARD.new.VIV")
	test_viv("files/ONLINE.VIV", "output/ONLINE.VIV/", "output/ONLINE.new.VIV")
	test_viv("files/PAUSE.VIV", "output/PAUSE.VIV/", "output/PAUSE.new.VIV")
	test_viv("files/LEVEL.VIV", "output/LEVEL.VIV/", "output/LEVEL.new.VIV")

main()