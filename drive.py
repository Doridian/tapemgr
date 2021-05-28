from subprocess import call, check_output

class Drive():
    def __init__(self, dev):
        self.dev = '/dev/%s' % dev
        self.mountpoint = None

        fh = open('/sys/class/scsi_tape/%s/device/generic/dev' % dev, 'r')
        fd = fh.read().strip()
        fh.close()
        self.sgid = fd.split(':')[1]

    def set_encryption(self, on):
        call(['stenc', '-f', self.dev, '-e', 'on' if on else 'off', '-k', '/mnt/keydisk/tape.key', '-a', '1', '--ckod'])

    def eject(self):
        self.unmount()
        call(['/opt/tape/TapeTool.sh', 'eject', self.sgid])

    def load(self):
        self.unmount()
        call(['/opt/tape/TapeTool.sh', 'load', self.sgid])

    def read_label(self):
        return check_output(['lto-cm', '-f', self.dev, '-r', '2051']).strip()

    def init(self, label):
        self.unmount()
        self.set_encryption(True)
        call(['mkltfs', '--device=%s' % self.dev, '-n', label, '-f'])

    def mount(self, mountpoint='/mnt/tape'):
        self.unmount()
        self.set_encryption(True)
        self.mountpoint = mountpoint
        call(['ltfs', '-o', 'eject', '-o', 'sync_type=unmount', mountpoint])

    def unmount(self):
        if self.mountpoint is None:
            return
        call(['umount', self.mountpoint])
        self.set_encryption(False)
        self.mountpoint = None
