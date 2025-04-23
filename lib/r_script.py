import subprocess
import shutil

class RScript:
    def __init__(self, root_path):
        self.root_path   = root_path
        self.rscript_exe = shutil.which('Rscript')

    def run(self, script_path, *args):
        result = subprocess.run(
            [self.rscript_exe, script_path, *args],
            cwd=self.root_path,
            capture_output=True,
        )

        if result.returncode != 0:
            raise ValueError(f"Failed RScript call,\n> STDOUT:\n{result.stdout}\n> STDERR:\n{result.stderr}")

        return result.stdout.decode('utf-8')
