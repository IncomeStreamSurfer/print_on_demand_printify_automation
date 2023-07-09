import argparse
from uploadimages import upload_images
from createimages import create_images
from upscaleuploadimages import upscale_upload_images
from upscalecreateimages import upscale_create_images

parser = argparse.ArgumentParser(description="Run scripts for print-on-demand automation")
parser.add_argument("--script", help="The script to run", choices=["uploadimages", "createimages", "upscaleuploadimages", "upscalecreateimages"])
args = parser.parse_args()

if args.script == "uploadimages":
    upload_images()
elif args.script == "createimages":
    create_images()
elif args.script == "upscaleuploadimages":
    upscale_upload_images()
elif args.script == "upscalecreateimages":
    upscale_create_images()
