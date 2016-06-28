cmake_minimum_required(VERSION 2.8.9)

project(DiagnosticIndex)
set(LOCAL_PROJECT_NAME DiagnosticIndex)


#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_NAME "DiagnosticIndex")
set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/DiagnosticIndex")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Laura Pascal (DCBIA-OrthoLab, University of Michigan)")
set(EXTENSION_DESCRIPTION "TODO")
set(EXTENSION_ICONURL "TODO")
set(EXTENSION_SCREENSHOTURLS "TODO")
set(EXTENSION_DEPENDS ShapePopulationViewer)
set(EXTENSION_BUILD_SUBDIRECTORY .)

#-----------------------------------------------------------------------------
include(ExternalProject)

#-----------------------------------------------------------------------------
# Extension dependencies
# Statismo
find_package(statismo REQUIRED)

# Slicer
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})
include(SlicerExtensionsConfigureMacros)
#resetForSlicer( NAMES CMAKE_C_COMPILER CMAKE_CXX_COMPILER CMAKE_CXX_FLAGS CMAKE_C_FLAGS )

# Slicer Execution Model
find_package(SlicerExecutionModel REQUIRED)
include(${SlicerExecutionModel_USE_FILE})
include(${GenerateCLP_USE_FILE})

# VTK
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
#-----------------------------------------------------------------------------
add_subdirectory(src)

#-----------------------------------------------------------------------------
set(CPACK_INSTALL_CMAKE_PROJECTS "${CPACK_INSTALL_CMAKE_PROJECTS};${CMAKE_BINARY_DIR};${EXTENSION_NAME};ALL;/")
include(${Slicer_EXTENSION_CPACK})