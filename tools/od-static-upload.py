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
                         help="UPload content to the external host")
    PARSER_.add_argument("-t", "--test-host", action="store_true", default=False, help="Upload content to the test host")
    PARSER_.add_argument("--input-dir", action="store", dest="input_dir", required=True, help="Input directory")

    return PARSER_.parse_args()

def remove(idx_name, is_external, is_test):
    dockerHost = None
    if is_external:
        dockerHost = "ssh://ubuntu@comori-od.ro"
    elif is_test:
        dockerHost = "ssh://ovidiu@ubuntu-home"

    cmd = []
    if dockerHost:
        cmd += [f"DOCKER_HOST={dockerHost}"]

    cmd += ["docker ", "exec", "-i", "nginx-proxy", "bash", "-c", f"\"rm -f /usr/share/nginx/html/{idx_name}/data/*\""]
    cmd = " ".join(cmd)

    print(f"Executing '{cmd}'...")
    os.system(cmd)

def upload(input_dir, idx_name, is_external, is_test):
    dockerHost = None
    if is_external:
        dockerHost = "ssh://ubuntu@comori-od.ro"
    elif is_test:
        dockerHost = "ssh://ovidiu@ubuntu-home"

    cmd = []
    if dockerHost:
        cmd += [f"DOCKER_HOST={dockerHost}"]

    cmd += ["docker", "cp", f"{input_dir}/.", f"nginx-proxy:/usr/share/nginx/html/{idx_name}/data"]
    cmd = " ".join(cmd)

    print(f"Executing '{cmd}'...")
    os.system(cmd)

def main():
    args = parseArgs()
    remove(args.idx_name, args.external_host, args.beta_host)
    upload(args.input_dir, args.idx_name, args.external_host, args.beta_host)

if "__main__" == __name__:
    main()