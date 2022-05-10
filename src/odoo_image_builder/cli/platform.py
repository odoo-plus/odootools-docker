import platform


def get_arch():
    arch = platform.processor()

    if arch == "x86_64":
        docker_arch = "amd64"
    elif arch == "aarch64":
        docker_arch = "arm64"
    else:
        docker_arch = arch

    return docker_arch


def main():
    arch = get_arch()
    print(arch, end='')
