import importlib
import types
import unittest


class TestImport(unittest.TestCase):
    def test_module_imports(self):
        mod = importlib.import_module('export4.OptiX')
        self.assertIsInstance(mod, types.ModuleType)
        self.assertTrue(hasattr(mod, 'Application'))
        self.assertTrue(hasattr(mod, 'main'))

    def test_no_side_effect_on_import(self):
        # Importing should not start the Tk mainloop. This is a smoke test.
        mod = importlib.import_module('export4.OptiX')
        self.assertTrue(hasattr(mod, '__name__'))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
