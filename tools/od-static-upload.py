#!/usr/bin/pypy3
import os
import argparse

PARSER_ = argparse.ArgumentParser(description="OD content static uploader.")

def parseArgs():
    PARSER_.add_argument("-e",
                         "--external-host",
                         action="store_true",
                         default=False,
                         help="Upload content to the external host")
    PARSER_.add_argument("-t", "--test-host", action="store_true", default=False, help="Upload content to the test host")
    PARSER_.add_argument("-n", "--new-host", action="store_true", default=False, help="Upload content to the new host")
    PARSER_.add_argument("--input-dir", action="store", dest="input_dir", required=True, help="Input directory")
    PARSER_.add_argument("--dest-dir", action="store", dest="dest_dir", required=True, help="Destination directory (in /usr/share/nginx/)")

    args, _ = PARSER_.parse_known_args()
    return args

def remove(docker_host, dest_dir):
    if dest_dir.endswith("/"):
        dest_dir = dest_dir[:-1]

    cmd = []
    if docker_host:
        cmd += [f"DOCKER_HOST={docker_host}"]

    cmd += ["docker ", "exec", "-i", "nginx-proxy", "bash", "-c", f"\"rm -f /usr/share/nginx/{dest_dir}/*\""]
    cmd = " ".join(cmd)

    print(f"Executing '{cmd}'...")
    os.system(cmd)

def upload(docker_host, input_dir, dest_dir):
    if dest_dir.endswith("/"):
        dest_dir = dest_dir[:-1]

    cmd = []
    if docker_host:
        cmd += [f"DOCKER_HOST={docker_host}"]

    cmd += ["docker", "cp", f"{input_dir}/.", f"nginx-proxy:/usr/share/nginx/{dest_dir}"]
    cmd = " ".join(cmd)

    print(f"Executing '{cmd}'...")
    os.system(cmd)

def main():
    args = parseArgs()

    docker_host = None
    if args.external_host:
        docker_host = "ssh://ubuntu@comori-od.ro"
    elif args.test_host:
        docker_host = "ssh://ubuntu-dev"
    elif args.new_host:
        docker_host = "ssh://ubuntu-prod"

    if not docker_host:
        raise Exception(f"Docker host {docker_host} is not valid!")

    remove(docker_host, args.dest_dir)
    upload(docker_host, args.input_dir, args.dest_dir)

if "__main__" == __name__:
    main()