import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class Package(unittest.TestCase):
    def test_complete_installable_archive_without_development_or_omarchy_files(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = build.build(Path(temp) / 'extension.zip')
            with zipfile.ZipFile(archive) as package:
                names = set(package.namelist())
                self.assertEqual(names, set(build.FILES) | {
                    'schemas/gschemas.compiled',
                    'schemas/org.gnome.shell.extensions.surface-pen.gschema.xml'})
                self.assertGreater(len(package.read('schemas/gschemas.compiled')), 0)
                self.assertIsNone(package.testzip())

if __name__ == '__main__': unittest.main()
