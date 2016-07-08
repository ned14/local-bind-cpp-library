# Add generator expressions to appendvar expanding at build time any remaining parameters
# if the build configuration is config
function(expand_at_build_if_config config appendvar)
  set(ret ${${appendvar}})
  set(items ${ARGV})
  list(REMOVE_AT items 0 1)
  separate_arguments(items)
  foreach(item ${items})
    list(APPEND ret $<$<CONFIG:${config}>:${item}>)
  endforeach()
  set(${appendvar} ${ret} PARENT_SCOPE)
endfunction()

# Adds a custom command which generates a precompiled header
function(target_precompiled_header target headerpath)
  if(MSVC)
    add_custom_command(TARGET ${target} PRE_LINK
      COMMAND <CMAKE_CXX_COMPILER> <FLAGS> /Fp"${CMAKE_CURRENT_BINARY_DIR}/${target}.pch" /Yc"${headerpath}"
      COMMENT "Precompiling header ${headerpath} ..."
    )
  else()
  endif()
endfunction()

# Adds a custom target which generates a precompiled header
function(add_precompiled_header outvar headerpath)
  get_filename_component(header "${headerpath}" NAME)
  set(pchpath ${CMAKE_CURRENT_BINARY_DIR}/${header}.dir/${CMAKE_CFG_INTDIR}/${header}.pch)
  set(flags ${CMAKE_CXX_FLAGS})
  separate_arguments(flags)
  expand_at_build_if_config(Debug flags ${CMAKE_CXX_FLAGS_DEBUG})
  expand_at_build_if_config(Release flags ${CMAKE_CXX_FLAGS_RELEASE})
  expand_at_build_if_config(RelWithDebInfo flags ${CMAKE_CXX_FLAGS_RELWITHDEBINFO})
  expand_at_build_if_config(MinSizeRel flags ${CMAKE_CXX_FLAGS_MINSIZEREL})
  MESSAGE(STATUS "${flags}")
  if(MSVC)
    add_custom_target(${outvar}
      COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_BINARY_DIR}/${header}.dir/${CMAKE_CFG_INTDIR}"
      COMMAND ${CMAKE_CXX_COMPILER} /c ${flags} /Fp"${pchpath}" /Yc"${header}" /Tp"${CMAKE_CURRENT_SOURCE_DIR}/${headerpath}"
      COMMENT "Precompiling header ${headerpath} ..."
      SOURCES "${headerpath}"
    )
  else()
  endif()
endfunction()
