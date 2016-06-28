if( NOT EXTERNAL_SOURCE_DIRECTORY )
  set( EXTERNAL_SOURCE_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/ExternalSources )
endif()


# Make sure this file is included only once by creating globally unique varibles
# based on the name of this included file.
get_filename_component(CMAKE_CURRENT_LIST_FILENAME ${CMAKE_CURRENT_LIST_FILE} NAME_WE)
if(${CMAKE_CURRENT_LIST_FILENAME}_FILE_INCLUDED)
  return()
endif()
set(${CMAKE_CURRENT_LIST_FILENAME}_FILE_INCLUDED 1)

# Make sure that the ExtProjName/IntProjName variables are unique globally
# even if other External_${ExtProjName}.cmake files are sourced by
# SlicerMacroCheckExternalProjectDependency
set(extProjName statismo) #The find_package known name
set(proj        statismo) #This local name

# Sanity checks
#if(DEFINED ${extProjName}_DIR AND NOT EXISTS ${${extProjName}_DIR})
#  message(FATAL_ERROR "${extProjName}_DIR variable is defined but corresponds to non-existing directory (${${extProjName}_DIR})")
#endif()

# Set dependency list
set(${proj}_DEPENDENCIES "")

# Include dependent projects if any
SlicerMacroCheckExternalProjectDependency(${proj})

if( ${USE_SYSTEM_HDF5} MATCHES "OFF" )
  set( {proj}_DEPENDENCIES ${{proj}_DEPENDENCIES} HDF5 )
endif()
if( ${USE_SYSTEM_VTK} MATCHES "OFF" )
  set( {proj}_DEPENDENCIES ${{proj}_DEPENDENCIES} VTK )
endif()

set(VTK_DIR ${Slicer_DIR}/../VTKv6-build)
set(HDF5_DIR ${Slicer_DIR}/../HDF5-install/share/cmake/hdf5)

if(NOT ( DEFINED "USE_SYSTEM_${extProjName}" AND "${USE_SYSTEM_${extProjName}}" ) )
  #message(STATUS "${__indent}Adding project ${proj}")

  # Set CMake OSX variable to pass down the external project
  set(CMAKE_OSX_EXTERNAL_PROJECT_ARGS)
  if(APPLE)
    list(APPEND CMAKE_OSX_EXTERNAL_PROJECT_ARGS
      -DCMAKE_OSX_ARCHITECTURES=${CMAKE_OSX_ARCHITECTURES}
      -DCMAKE_OSX_SYSROOT=${CMAKE_OSX_SYSROOT}
      -DCMAKE_OSX_DEPLOYMENT_TARGET=${CMAKE_OSX_DEPLOYMENT_TARGET}
      )
  endif()
  set(${proj}_CMAKE_OPTIONS
      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_CURRENT_BINARY_DIR}/${proj}-install
      -DBUILD_EXAMPLES:BOOL=OFF
      -DBUILD_TESTING:BOOL=OFF
      -DBUILD_SHARED_LIBS:BOOL=OFF
      #-DUSE_SYSTEM_HDF5:BOOL=ON
      #-DHDF5_DIR:PATH=${HDF5_DIR}
      #-DUSE_SYSTEM_VTK:BOOL=ON
      #-DVTK_DIR:PATH=${VTK_DIR}
    )

### --- End Project specific additions
  set(${proj}_REPOSITORY "${git_protocol}://github.com/laurapascal/statismo.git")
  set(${proj}_GIT_TAG 8a30a7dfb62c9dbf12f8a8201bc952891975e334)
  ExternalProject_Add(
    ${proj}
    GIT_REPOSITORY ${${proj}_REPOSITORY}
    GIT_TAG ${${proj}_GIT_TAG}
    SOURCE_DIR ${EXTERNAL_SOURCE_DIRECTORY}/${proj}
    BINARY_DIR ${proj}-build
    LOG_CONFIGURE 0  # Wrap configure in script to ignore log output from dashboards
    LOG_BUILD     0  # Wrap build in script to to ignore log output from dashboards
    LOG_TEST      0  # Wrap test in script to to ignore log output from dashboards
    LOG_INSTALL   0  # Wrap install in script to to ignore log output from dashboards
    ${cmakeversion_external_update} "${cmakeversion_external_update_value}"
    CONFIGURE_COMMAND
      ${CMAKE_COMMAND}
      ${COMMON_EXTERNAL_PROJECT_ARGS}
      ${${proj}_CMAKE_OPTIONS}
      ${EXTERNAL_SOURCE_DIRECTORY}/${proj}/superbuild
    BUILD_COMMAND
      ${CMAKE_COMMAND} --build .
    ## We really do want to install in order to limit # of include paths INSTALL_COMMAND ""
    DEPENDS
      ${${proj}_DEPENDENCIES}
    )
  set(${extProjName}_DIR ${CMAKE_BINARY_DIR}/${proj}-install/lib/cmake/statismo)
else()
  if(${USE_SYSTEM_${extProjName}})
    find_package(${extProjName} REQUIRED)
  endif()
  # The project is provided using ${extProjName}_DIR, nevertheless since other
  # project may depend on ${extProjName}, let's add an 'empty' one
  SlicerMacroEmptyExternalProject(${proj} "${${proj}_DEPENDENCIES}")
endif()

list(APPEND ${CMAKE_PROJECT_NAME}_SUPERBUILD_EP_VARS ${extProjName}_DIR:PATH)
