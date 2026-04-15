cmake_minimum_required(VERSION 3.8)
project(amr_safety_guard)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(DIRECTORY
  urdf
  worlds
  launch
  rviz
  config
  maps
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  amr_safety_guard/zone_monitor.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME zone_monitor
)

install(PROGRAMS
  amr_safety_guard/patrol_node.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME patrol_node
)

install(PROGRAMS
  amr_safety_guard/emergency_stop.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME emergency_stop
)
install(PROGRAMS
  amr_safety_guard/webcam_publisher.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME webcam_publisher
)
install(PROGRAMS
amr_safety_guard/person_detector.py
DESTINATION lib/${PROJECT_NAME}
RENAME person_detector
)
install(PROGRAMS
  amr_safety_guard/mission_monitor.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME mission_monitor
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  
endif()

ament_package()
