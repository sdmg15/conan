import os
import unittest
import six

from conans.errors import ConanException
from conans.test.utils.tools import TestClient
from conans.util.files import load
from conans.test.utils.test_files import temp_folder
from conans.client.tools import environment_append


class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.client = TestClient()

    def basic_test(self):
        # show the full file
        self.client.run("config get")
        self.assertIn("default_profile = default", self.client.out)
        self.assertIn("path = ./data", self.client.out)

    def storage_test(self):
        # show the full file
        self.client.run("config get storage")
        self.assertIn("path = ./data", self.client.out)

        self.client.run("config get storage.path")
        full_path = os.path.join(self.client.cache_folder, "data")
        self.assertIn(full_path, self.client.out)
        self.assertNotIn("path:", self.client.out)

    def errors_test(self):
        self.client.run("config get whatever", assert_error=True)
        self.assertIn("'whatever' is not a section of conan.conf", self.client.out)
        self.client.run("config get whatever.what", assert_error=True)
        self.assertIn("'whatever' is not a section of conan.conf", self.client.out)
        self.client.run("config get storage.what", assert_error=True)
        self.assertIn("'what' doesn't exist in [storage]", self.client.out)
        self.client.run('config set proxies=https:', assert_error=True)
        self.assertIn("You can't set a full section, please specify a key=value",
                      self.client.out)

        self.client.run('config set proxies.http:Value', assert_error=True)
        self.assertIn("Please specify 'key=value'", self.client.out)

    def define_test(self):
        self.client.run("config set general.fakeos=Linux")
        conf_file = load(self.client.cache.conan_conf_path)
        self.assertIn("fakeos = Linux", conf_file)

        self.client.run('config set general.compiler="Other compiler"')
        conf_file = load(self.client.cache.conan_conf_path)
        self.assertIn('compiler = Other compiler', conf_file)

        self.client.run('config set general.compiler.version=123.4.5')
        conf_file = load(self.client.cache.conan_conf_path)
        self.assertIn('compiler.version = 123.4.5', conf_file)
        self.assertNotIn("14", conf_file)

        self.client.run('config set general.new_setting=mysetting ')
        conf_file = load(self.client.cache.conan_conf_path)
        self.assertIn('new_setting = mysetting', conf_file)

        self.client.run('config set proxies.https=myurl')
        conf_file = load(self.client.cache.conan_conf_path)
        self.assertIn("https = myurl", conf_file.splitlines())

    def set_with_weird_path_test(self):
        # https://github.com/conan-io/conan/issues/4110
        self.client.run("config set log.trace_file=/recipe-release%2F0.6.1")
        self.client.run("config get log.trace_file")
        self.assertIn("/recipe-release%2F0.6.1", self.client.out)

    def remove_test(self):
        self.client.run('config set proxies.https=myurl')
        self.client.run('config rm proxies.https')
        conf_file = load(self.client.cache.conan_conf_path)
        self.assertNotIn('myurl', conf_file)

    def remove_section_test(self):
        self.client.run('config rm proxies')
        conf_file = load(self.client.cache.conan_conf_path)
        self.assertNotIn('[proxies]', conf_file)

    def remove_envvar_test(self):
        self.client.run('config set env.MY_VAR=MY_VALUE')
        conf_file = load(self.client.cache.conan_conf_path)
        self.assertIn('MY_VAR = MY_VALUE', conf_file)
        self.client.run('config rm env.MY_VAR')
        conf_file = load(self.client.cache.conan_conf_path)
        self.assertNotIn('MY_VAR', conf_file)

    def missing_subarguments_test(self):
        self.client.run("config", assert_error=True)
        self.assertIn("ERROR: Exiting with code: 2", self.client.out)

    def test_config_home_default(self):
        self.client.run("config home")
        self.assertIn(self.client.cache.cache_folder, self.client.out)

    def test_config_home_custom_home_dir(self):
        cache_folder = os.path.join(temp_folder(), "custom")
        with environment_append({"CONAN_USER_HOME": cache_folder}):
            client = TestClient(cache_folder=cache_folder)
            client.run("config home")
            self.assertIn(cache_folder, client.out)

    def test_config_home_short_home_dir(self):
        cache_folder = os.path.join(temp_folder(), "custom")
        with environment_append({"CONAN_USER_HOME_SHORT": cache_folder}):
            with six.assertRaisesRegex(self, ConanException, "cannot be a subdirectory of the conan cache"):
                TestClient(cache_folder=cache_folder)
