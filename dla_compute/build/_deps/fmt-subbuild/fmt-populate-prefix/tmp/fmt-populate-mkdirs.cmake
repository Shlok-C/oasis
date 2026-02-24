# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/mnt/c/Users/shlok/Desktop/oasis/dla_compute/build/_deps/fmt-src"
  "/mnt/c/Users/shlok/Desktop/oasis/dla_compute/build/_deps/fmt-build"
  "/mnt/c/Users/shlok/Desktop/oasis/dla_compute/build/_deps/fmt-subbuild/fmt-populate-prefix"
  "/mnt/c/Users/shlok/Desktop/oasis/dla_compute/build/_deps/fmt-subbuild/fmt-populate-prefix/tmp"
  "/mnt/c/Users/shlok/Desktop/oasis/dla_compute/build/_deps/fmt-subbuild/fmt-populate-prefix/src/fmt-populate-stamp"
  "/mnt/c/Users/shlok/Desktop/oasis/dla_compute/build/_deps/fmt-subbuild/fmt-populate-prefix/src"
  "/mnt/c/Users/shlok/Desktop/oasis/dla_compute/build/_deps/fmt-subbuild/fmt-populate-prefix/src/fmt-populate-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/mnt/c/Users/shlok/Desktop/oasis/dla_compute/build/_deps/fmt-subbuild/fmt-populate-prefix/src/fmt-populate-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/mnt/c/Users/shlok/Desktop/oasis/dla_compute/build/_deps/fmt-subbuild/fmt-populate-prefix/src/fmt-populate-stamp${cfgdir}") # cfgdir has leading slash
endif()
