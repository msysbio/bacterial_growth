import simplejson as json
import subprocess
import shutil
import logging
from pathlib import Path

LOGGER = logging.getLogger()


class RScript:
    """
    This object provides a generic interface to executing an R script using an
    `Rscript` executable found in the PATH. It expects to be given a root
    directory (likely a temporary one) where it'll look for its input files and
    produce its outputs.
    """

    def __init__(self, root_path):
        self.root_path   = Path(root_path)
        self.rscript_exe = shutil.which('Rscript')

        if self.rscript_exe is None:
            raise ValueError("Could not find `Rscript` executable in PATH")

    def run(self, script_path, *args):
        script_path = Path(script_path).absolute()

        result = subprocess.run(
            [self.rscript_exe, script_path, *args],
            cwd=self.root_path,
            capture_output=True,
        )

        if result.returncode != 0:
            LOGGER.error("STDOUT:")
            for line in result.stdout.decode('utf-8').split("\n"):
                LOGGER.error(line)

            LOGGER.error("STDERR:")
            for line in result.stderr.decode('utf-8').split("\n"):
                LOGGER.error(line)

            raise ValueError(f"Failed RScript call: {script_path}")

        for line in result.stderr.decode('utf-8').split("\n"):
            LOGGER.warning(line)

        return result.stdout.decode('utf-8')

    def write_csv(self, filename, df):
        df.to_csv(self.root_path / filename, index=False)

    def read_json(self, filename):
        path = self.root_path / filename

        if not path.exists():
            return None

        text = path.read_text()
        LOGGER.info(f"{filename}: {text}")

        return json.loads(text, use_decimal=True)
