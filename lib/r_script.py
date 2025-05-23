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

    def write_json(self, filename, data):
        with open(self.root_path / filename, 'w') as f:
            json.dump(data, f)

    def read_key_value_json(self, filename, key_name, value_name):
        raw_data = self._read_raw_json(filename)

        if raw_data is None:
            return None

        return { entry[key_name]: entry[value_name] for entry in raw_data }

    def read_flat_json(self, filename, discard_keys=[]):
        raw_data = self._read_raw_json(filename)
        if raw_data is None:
            return None

        if len(raw_data) == 0:
            return None
        else:
            return {k: v for k, v in raw_data[0].items() if k not in discard_keys}

    def _read_raw_json(self, filename):
        path = self.root_path / filename

        if not path.exists():
            return None

        text = path.read_text()
        LOGGER.info(f"{filename}: {text}")

        return json.loads(text, use_decimal=True)
