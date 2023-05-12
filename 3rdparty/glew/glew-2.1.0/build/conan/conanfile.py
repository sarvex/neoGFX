import os
from conans import ConanFile, CMake
from conans.tools import os_info, SystemPackageTool, ConanException
from conans import tools, VisualStudioBuildEnvironment
from conans.tools import build_sln_command, vcvars_command, replace_in_file, download, unzip

class GlewConan(ConanFile):
    name = "glew"
    version = "master"
    source_directory = "%s-%s" % (name, version) if version != "master" else "."
    description = "The GLEW library"
    generators = "cmake", "txt"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    url="http://github.com/nigels-com/glew"
    license="https://github.com/nigels-com/glew#copyright-and-licensing"
    if version == "master":
        if os.path.isfile("Makefile"):
            exports_sources = "*"
        else:
            exports_sources = os.sep.join(["..", "..", "*"])
    else:
        exports = "FindGLEW.cmake"
        
    def system_requirements(self):
        if not os_info.is_linux:
            return
        if os_info.with_apt:
            installer = SystemPackageTool()
            if self.version == "master":
                installer.install("build-essential")
                installer.install("libxmu-dev")
                installer.install("libxi-dev")
                installer.install("libgl-dev")
                installer.install("libosmesa-dev")
            installer.install("libglu1-mesa-dev")
        elif os_info.with_yum:
            installer = SystemPackageTool()
            if self.version == "master":
                installer.install("libXmu-devel")
                installer.install("libXi-devel")
                installer.install("libGL-devel")
            installer.install("mesa-libGLU-devel")
        else:
            self.output.warn("Could not determine Linux package manager, skipping system requirements installation.")

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        if self.version != "master":
            zip_name = f"{self.source_directory}.tgz"
            download(
                f"https://sourceforge.net/projects/glew/files/glew/{self.version}/{zip_name}/download",
                zip_name,
            )
            unzip(zip_name)
            os.unlink(zip_name)

    def build(self):
        if self.settings.os == "Windows" and self.version == "master":
            raise ConanException("Trunk builds are not supported on Windows (cannot build directly from master git repository).")

        if self.settings.compiler == "Visual Studio":
            env = VisualStudioBuildEnvironment(self)
            with tools.environment_append(env.vars):
                version = min(12, int(self.settings.compiler.version.value))
                version = 10 if version == 11 else version
                cd_build = "cd %s\\%s\\build\\vc%s" % (self.conanfile_directory, self.source_directory, version)
                build_command = build_sln_command(self.settings, "glew.sln")
                vcvars = vcvars_command(self.settings)
                self.run(f'{vcvars} && {cd_build} && {build_command.replace("x86", "Win32")}')
        else:
            if self.settings.os == "Windows":
                replace_in_file(
                    f"{self.source_directory}/build/cmake/CMakeLists.txt",
                    "if(WIN32 AND (NOT MSVC_VERSION LESS 1600)",
                    "if(WIN32 AND MSVC AND (NOT MSVC_VERSION LESS 1600)",
                )

            if self.version == "master":
                self.run("make extensions")

            cmake = CMake(self)
            cmake.configure(
                source_dir=f"{self.source_directory}/build/cmake",
                defs={"BUILD_UTILS": "OFF"},
            )
            cmake.build()

    def package(self):
        find_glew_dir = (
            f"{self.conanfile_directory}/build/conan"
            if self.version == "master"
            else "."
        )
        self.copy("FindGLEW.cmake", ".", find_glew_dir, keep_path=False)
        self.copy("include/*", ".", f"{self.source_directory}", keep_path=True)
        self.copy(
            f"{self.source_directory}/license*",
            dst="licenses",
            ignore_case=True,
            keep_path=False,
        )

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                self.copy(pattern="*.pdb", dst="bin", keep_path=False)
                if self.options.shared:
                    self.copy(pattern="*32.lib", dst="lib", keep_path=False)
                    self.copy(pattern="*32d.lib", dst="lib", keep_path=False)
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                else:
                    self.copy(pattern="*32s.lib", dst="lib", keep_path=False)
                    self.copy(pattern="*32sd.lib", dst="lib", keep_path=False)
            elif self.options.shared:
                self.copy(pattern="*32.dll.a", dst="lib", keep_path=False)
                self.copy(pattern="*32d.dll.a", dst="lib", keep_path=False)
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
            else:
                self.copy(pattern="*32.a", dst="lib", keep_path=False)
                self.copy(pattern="*32d.a", dst="lib", keep_path=False)
        elif self.settings.os == "Macos":
            if self.options.shared:
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)
        elif self.options.shared:
            self.copy(pattern="*.so", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['glew32']

            if not self.options.shared:
                self.cpp_info.defines.append("GLEW_STATIC")

            if self.settings.compiler == "Visual Studio":
                if not self.options.shared:
                    self.cpp_info.libs[0] += "s"
                    self.cpp_info.libs.append("OpenGL32.lib")
                    if self.settings.compiler.runtime != "MT":
                        self.cpp_info.exelinkflags.append('-NODEFAULTLIB:LIBCMTD')
                        self.cpp_info.exelinkflags.append('-NODEFAULTLIB:LIBCMT')
            else:
                self.cpp_info.libs.append("opengl32")
                
        else:
            self.cpp_info.libs = ['GLEW']
            if self.settings.os == "Macos":
                self.cpp_info.exelinkflags.append("-framework OpenGL")
            elif not self.options.shared:
                self.cpp_info.libs.append("GL")

        if self.settings.build_type == "Debug":
            self.cpp_info.libs[0] += "d"
