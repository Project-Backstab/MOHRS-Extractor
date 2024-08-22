import os
import json
from dataclasses import dataclass, field, asdict, is_dataclass
from typing import List

from lib.functions import create_file

MAGIC_CODE = b"\xC0\xFB"

@dataclass
class FileInfo:
	file_name: str = ""
	
	## Only used in process
	start_offset: int = 0
	file_size: int = 0
	empty_space: int = 0

@dataclass
class Viv:
	magic_code: str = ""
	header_size: int = 0
	file_infos: List[FileInfo] = field(default_factory=list)

def clean_nan(obj):
    if isinstance(obj, float):
        return None if math.isnan(obj) else obj
    elif isinstance(obj, list):
        return [clean_nan(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif is_dataclass(obj):
        return clean_nan(asdict(obj))
    return obj

class CustomEncoder(json.JSONEncoder):
	def default(self, obj):
		if is_dataclass(obj):
			return clean_nan(asdict(obj))
		return super().default(obj)

def read_string(f_viv, offset):
	data = f_viv.read(1)
	offset += 1
	
	while(data[-1] != 0x00):
		data += f_viv.read(1)
		offset += 1
	
	return data.rstrip(b'\x00').decode("ascii").strip(), offset

def export_viv(input_file_path, output_files_path):
	viv = Viv()
	offset = 0
	
	# Create directories if they don't exist
	os.makedirs(output_files_path, exist_ok=True)
	
	## Read viv file
	with open(input_file_path, "rb") as f_viv:
		viv.magic_code = f_viv.read(2).hex()
		
		if(viv.magic_code != MAGIC_CODE.hex()):
			return
		
		viv.header_size = int.from_bytes(f_viv.read(2), byteorder='big')
		file_infos_total = int.from_bytes(f_viv.read(2), byteorder='big')
		offset += 6
		
		for i in range(file_infos_total):
			file_info = FileInfo()
			
			file_info.start_offset = int.from_bytes(f_viv.read(3), byteorder='big')
			file_info.file_size = int.from_bytes(f_viv.read(3), byteorder='big')
			file_info.file_name, offset = read_string(f_viv, offset)
			offset += 6
			
			viv.file_infos.append(file_info)
		
		for file_info in viv.file_infos:
			if(offset < file_info.start_offset):
				file_info.empty_space = file_info.start_offset - offset
				offset = file_info.start_offset
				f_viv.seek(offset)
			
			file_data = f_viv.read(file_info.file_size)
			offset += file_info.file_size
			
			create_file(f"{output_files_path}/{file_info.file_name}", file_data)
		
		
	with open(f"{output_files_path}/viv.json", "w") as json_file:
		json.dump(viv, json_file, cls=CustomEncoder)

def calc_header_size(file_infos):
	## 2 bytes for files total
	header_size = 2
	
	for file_info in file_infos:
		## start_offset + file_size 
		header_size += 6
		
		## file_name
		header_size += len(file_info["file_name"]) + 1
	
	return header_size

def calc_add_empty_space(offset):
	remainder = offset % 0x40

	if remainder == 0:
		return 0
	else:
		return 0x40 - remainder

def import_viv(input_files_path, output_file_path):
	content = b""
	
	## Read viv json file
	with open(f"{input_files_path}/viv.json", "r") as f_json:
		viv = json.load(f_json)
		
		## Calculate header size
		header_size = calc_header_size(viv["file_infos"])
		
		## Calculate start position for file content
		start_offset = header_size + 4
		
		## Magic code
		content = MAGIC_CODE
		
		## Header size
		content += (header_size).to_bytes(2, byteorder='big')
		
		## Make viv header
		content += len(viv["file_infos"]).to_bytes(2, byteorder='big')
		for file_info in viv["file_infos"]:
			file_path = f"{input_files_path}/{file_info['file_name']}"
			file_size = os.path.getsize(file_path)
			
			## Calculate how much empty space needs to be added.
			file_info["empty_space"] = calc_add_empty_space(start_offset)
			
			## Generate start position for file
			start_offset += file_info["empty_space"]
			
			## Write file info
			content += start_offset.to_bytes(3, byteorder='big')
			content += file_size.to_bytes(3, byteorder='big')
			content += file_info["file_name"].encode("ascii")
			content += b"\x00"
			
			## Add file size to start offset
			start_offset += file_size
			
		## Add Files
		for file_info in viv["file_infos"]:
			file_path = f"{input_files_path}/{file_info['file_name']}"
			
			content += file_info["empty_space"] * b"\x00"
			
			## Read viv json file
			with open(file_path, "rb") as f:
				content += f.read()
	
	## Create new *.cat file
	with open(output_file_path, "wb") as f_viv:
		f_viv.write(content)

