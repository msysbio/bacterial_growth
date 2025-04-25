import subprocess
import shutil
import json
import logging
from pathlib import Path

LOGGER = logging.getLogger()


class RScript:
    def __init__(self, root_path):
        self.root_path   = Path(root_path)
        self.rscript_exe = shutil.which('Rscript')

    def run(self, script_path, *args):
        script_path = Path(script_path).absolute()

        result = subprocess.run(
            [self.rscript_exe, script_path, *args],
            cwd=self.root_path,
            capture_output=True,
        )

        if result.returncode != 0:
            raise ValueError(f"Failed RScript call,\n> STDOUT:\n{result.stdout}\n> STDERR:\n{result.stderr}")

        for line in result.stderr.decode('utf-8').split("\n"):
            LOGGER.warning(line)

        return result.stdout.decode('utf-8')

    def write_csv(self, filename, df):
        df.to_csv(self.root_path / filename, index=False)

    def read_json(self, filename):
        print((self.root_path / filename).read_text())

        with open(self.root_path / filename) as f:
            return json.load(f)
