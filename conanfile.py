from conans import ConanFile, CMake, tools
import os
import shutil


class LMDBConan(ConanFile):
    name = "lmdb"
    description = "A light implementation of BerkeleyDB (BDB) API"
    url = "https://git.openldap.org/openldap/openldap/tree/mdb.master"
    homepage = "https://symas.com/lmdb/"
    topics = ("conan", "lmdb", "database")
    license = "OpenLDAP-Public-License"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_copy": [True, False],
        "with_stat": [True, False],
        "with_dump": [True, False],
        "with_load": [True, False]}
    default_options = {
        "shared": False, 
        "fPIC": True,
        "with_copy": False,
        "with_stat": False,
        "with_dump": False,
        "with_load": False}
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.build_requires("getopt-for-visual-studio/20200201")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "openldap-LMDB_" + self.version
        source_directory = os.path.join(extracted_dir, "libraries", "liblmdb")
        os.rename(source_directory, self._source_subfolder)
        shutil.rmtree(extracted_dir)
    
    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LMDB_BUILD_COPY"] = self.options.with_copy
        self._cmake.definitions["LMDB_BUILD_STAT"] = self.options.with_stat
        self._cmake.definitions["LMDB_BUILD_DUMP"] = self.options.with_dump
        self._cmake.definitions["LMDB_BUILD_LOAD"] = self.options.with_load
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("*/lmdb.h", dst="include", keep_path=False)
        self.copy("*.lib", dst="lib", src="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", src="lib", keep_path=False)
        self.copy("*.so", dst="bin", keep_path=False)
        self.copy("*.exe", dst="bin", src="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
