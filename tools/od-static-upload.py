#!/usr/bin/pypy3
import os
import argparse

PARSER_ = argparse.ArgumentParser(description="OD content static uploader.")

def parseArgs():
    PARSER_.add_argument("-i", "--index", dest="idx_name", action="store", required=True, help="Index name")
    PARSER_.add_argument("-e",
                         "--external-host",
                         action="store_true",
                         default=False,
                         help="Remove content from external host")
    PARSER_.add_argument("--input-dir", action="store", dest="input_dir", required=True, help="Input directory")

    return PARSER_.parse_args()

def remove(idx_name, is_external):
    cmd = ["docker"]
    if is_external:
        cmd += ["--context", "comori-od"]

    cmd += ["exec", "-i", "nginx-proxy", "bash", "-c", f"\"rm -f /usr/share/nginx/html/{idx_name}/data/*\""]
    cmd = " ".join(cmd)

    print(f"Executing '{cmd}'...")
    os.system(cmd)

def upload(input_dir, idx_name, is_external):
    cmd = ["docker"]
    if is_external:
        cmd += ["--context", "comori-od"]

    cmd += ["cp", f"{input_dir}/.", f"nginx-proxy:/usr/share/nginx/html/{idx_name}/data"]
    cmd = " ".join(cmd)

    print(f"Executing '{cmd}'...")
    os.system(cmd)

def main():
    args = parseArgs()
    remove(args.idx_name, args.external_host)
    upload(args.input_dir, args.idx_name, args.external_host)

if "__main__" == __name__:
    main()