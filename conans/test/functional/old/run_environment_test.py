import unittest

from conans.client.run_environment import RunEnvironment


class CppInfo(object):

    def __init__(self):
        self.bin_paths = []
        self.lib_paths = []
        self.framework_paths = []


class MockDepsCppInfo(dict):

    def __init__(self):
        self["one"] = CppInfo()
        self["two"] = CppInfo()

    @property
    def deps(self):
        return self.keys()


class MockConanfile(object):

    def __init__(self):
        self.deps_cpp_info = MockDepsCppInfo()


class RunEnvironmentTest(unittest.TestCase):

    def run_vars_test(self):
        conanfile = MockConanfile()
        conanfile.deps_cpp_info["one"].bin_paths.append("path/bin")
        conanfile.deps_cpp_info["two"].lib_paths.append("path/libs")
        be = RunEnvironment(conanfile)

        self.assertEqual(be.vars,  {'PATH': ['path/bin'],
                                     'LD_LIBRARY_PATH': ['path/libs'],
                                     'DYLD_LIBRARY_PATH': ['path/libs']})

    def apple_frameworks_test(self):
        conanfile = MockConanfile()
        conanfile.deps_cpp_info["one"].bin_paths.append("path/bin")
        conanfile.deps_cpp_info["two"].lib_paths.append("path/libs")
        conanfile.deps_cpp_info["one"].framework_paths.append("path/Frameworks")
        be = RunEnvironment(conanfile)

        self.assertEqual(be.vars, {'PATH': ['path/bin'],
                                   'LD_LIBRARY_PATH': ['path/libs'],
                                   'DYLD_LIBRARY_PATH': ['path/libs'],
                                   'DYLD_FRAMEWORK_PATH': ['path/Frameworks']})
