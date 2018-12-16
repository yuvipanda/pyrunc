import os
import sys
import tempfile
import subprocess
import argparse

GOPATH = '/usr/local/go'

def build_skopeo(version, target_dir):
    skopeo_path = os.path.join(GOPATH, 'src/github.com/containers/skopeo')
    subprocess.check_call([
        'git', 'clone',
        'https://github.com/containers/skopeo',
        skopeo_path
    ])
    subprocess.check_call([
        'git', 'checkout', version
    ], cwd=skopeo_path)
    subprocess.check_call([
        'git', 'checkout', '-b', version
    ], cwd=skopeo_path)

    subprocess.check_call([
        'make',
        'binary-local',
        'DISABLE_CGO=1'
    ], cwd=skopeo_path)

    os.rename(os.path.join(skopeo_path, 'skopeo'), os.path.join(target_dir, 'skopeo'))


def build_umoci(version, target_dir):
    umoci_path = os.path.join(GOPATH, 'src/github.com/openSUSE/umoci')
    subprocess.run([
        'git', 'clone',
        'https://github.com/openSUSE/umoci',
        umoci_path
    ], check=True)

    subprocess.check_call([
        'git', 'checkout', version
    ], cwd=umoci_path)

    subprocess.check_call([
        'git', 'checkout', '-b', version
    ], cwd=umoci_path)

    subprocess.check_call([
        'make',
    ], cwd=umoci_path)

    os.rename(os.path.join(umoci_path, 'umoci'), os.path.join(target_dir, 'umoci'))


def build_runc():
    """
    runc doesn't build in manylinux1, since tht glibc is too old.

    We just download it instead.
    """
    env = os.environ.copy()
    with tempfile.TemporaryDirectory() as d:
        umoci_path = os.path.join(d, 'src/github.com/opencontainers/runc')
        env['GOPATH'] = d
        subprocess.run([
            'git', 'clone',
            '--depth', '1',
            'https://github.com/opencontainers/runc',
            umoci_path
        ], check=True)

        subprocess.run([
            'make',
            'BUILDTAGS=""'
        ], check=True, cwd=umoci_path, env=env)


def build_wheel(tool_name, tool_version):
    env = os.environ.copy()
    env['TOOL_NAME'] = tool_name
    env['TOOL_VERSION'] = tool_version
    subprocess.check_call([
        sys.executable,
        'setup.py',
        'bdist_wheel'
    ], env=env)

# OH MY GAWD!
# This is unconditional include in the containers/storage project for XFS quotas
# which we don't need, but there seems to be a bug in quota.h provided with
# manylinux1 that prevents it from even compiling
# We, uh, hack our way out of this. This is most likely ok!
# Don't run this outside docker.
with open('/proc/1/cgroup') as f:
    if 'docker' not in f.read():
        print("Running outside a docker container is not supported", file=sys.stderr)
        sys.exit(1)

with open('/usr/include/linux/quota.h', 'r+') as f:
    r = f.read().replace('extern spinlock_t dq_data_lock;', '')
    f.seek(0)
    f.truncate(0)
    f.write(r)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'program',
        help='Program to build',
        choices={'skopeo', 'umoci', 'runc'}
    )
    argparser.add_argument(
        'version',
        help='Version of program to build'
    )

    args = argparser.parse_args()

    if args.program == 'skopeo':
        build_skopeo(args.version, os.getcwd())
    elif args.program == 'umoci':
        build_umoci(args.version, os.getcwd())
    build_wheel(args.program, args.version)


if __name__ == '__main__':
    main()