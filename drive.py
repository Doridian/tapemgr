from subprocess import Popen
from os.path import ismount, basename
from time import sleep
from os import readlink
from util import logged_check_call

class Drive:
    mountpoint: str | None
    ltfs_process: Popen[bytes] | None
    def __init__(self, dev: str, key_file: str):
        super().__init__()
        self.dev = dev
        self.key_file = key_file
        self.mountpoint = None
        self.ltfs_process = None

    def set_encryption(self, on: bool):
        if (not on) or (not self.key_file):
            logged_check_call(['stenc', '-f', self.dev, '-e', 'off', '-a', '1', '--ckod'])
            return
        logged_check_call(['stenc', '-f', self.dev, '-e', 'on', '-k', self.key_file, '-a', '1', '--ckod'])

    def load(self):
        self.unmount()
        logged_check_call(['sg_start', '--load', self.dev])

    def format(self, label: str, serial: str):
        self.unmount()
        self.load()
        self.set_encryption(True)
        logged_check_call(['mkltfs', '--device=%s' % self.dev, '-n', label, '-s', serial, '-f'])

    def make_sg(self):
        linkdest = readlink('/sys/class/scsi_tape/%s/device/generic' % self.dev.replace('/dev/', ''))
        return '/dev/%s' % basename(linkdest)

    def mount(self, mountpoint: str):
        if self.mountpoint == mountpoint:
            return False
        self.unmount()
        self.load()
        self.set_encryption(True)
        self.mountpoint = mountpoint
        self.ltfs_process = Popen(['ltfs', '-o', 'devname=%s' % self.make_sg(), '-f', '-o', 'umask=077', '-o', 'eject', '-o', 'sync_type=unmount', mountpoint])
        while self.ltfs_process.returncode is None:
            if ismount(mountpoint):
                break
            sleep(0.1)
        if not ismount(mountpoint):
            raise SystemError('Could not mount LTFS tape!')
        return True

    def unmount(self) -> None:
        if self.ltfs_process is None:
            return
        if self.mountpoint is None:
            return
        logged_check_call(['umount', self.mountpoint])
        _ = self.ltfs_process.wait()
        self.ltfs_process = None
        self.mountpoint = None
