import unittest
import tempfile
from pathlib import Path

import pandas as pd

from app.model.lib.r_script import RScript


class TestRScriptRunner(unittest.TestCase):
    def setUp(self):
        self.root_dir  = tempfile.TemporaryDirectory()
        self.root_path = Path(self.root_dir.name)

    def tearDown(self):
        self.root_dir.cleanup()

    def test_run_simple_script(self):
        script_path = self._create_script('simple.R', """
            print(c(1, 2) + c(2, 1))
        """)
        script = RScript(self.root_path)
        output = script.run(script_path)

        self.assertEqual(output.strip(), '[1] 3 3')

    def test_run_with_input_df(self):
        input_file = pd.DataFrame({'time': [1, 2, 3], 'value': [10.0, 20.0, 30.0]})
        input_file.to_csv(self.root_path / 'input.csv', index=False)

        script_path = self._create_script('simple.R', """
            args <- commandArgs(TRUE)
            data <- read.table(args[1], header=T, sep=',', row.names=NULL)

            print(data$time)
            print(data$value)
        """)
        script = RScript(self.root_path)
        output = script.run(script_path, 'input.csv')

        self.assertEqual(output.strip(), "[1] 1 2 3\n[1] 10 20 30")

    def _create_script(self, name, contents):
        script_path = self.root_path / name

        with open(script_path, 'w') as f:
            for line in contents.strip().split("\n"):
                f.write(line.rstrip())
                f.write("\n")

        return script_path


if __name__ == '__main__':
    unittest.main()
