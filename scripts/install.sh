#!/usr/bin/env bash
set -euo pipefail

WS="${HOME}/autonomous_serving_robot_ws"
SRC="${WS}/src/serving_robot"
REPO_URL="https://github.com/ram-streetbell/autonomous-serving-robot.git"

if [[ "${EUID}" -eq 0 ]]; then echo "Run this installer as the normal user, not root."; exit 1; fi
source /etc/os-release
if [[ "${ID}" != "ubuntu" ]]; then echo "Ubuntu is required for the automated installer."; exit 1; fi

sudo apt-get update
sudo apt-get install -y git python3-pip python3-yaml python3-numpy python3-tk

if [[ ! -f /opt/ros/jazzy/setup.bash && ! -f /opt/ros/humble/setup.bash ]]; then
  echo "ROS 2 is not installed. Recommended: Jazzy on Ubuntu 24.04 or Humble on Ubuntu 22.04."; exit 2
fi
if [[ -f /opt/ros/jazzy/setup.bash ]]; then ROS_DISTRO=jazzy; else ROS_DISTRO=humble; fi
source "/opt/ros/${ROS_DISTRO}/setup.bash"
sudo apt-get install -y \
  ros-${ROS_DISTRO}-robot-state-publisher ros-${ROS_DISTRO}-tf2-ros \
  ros-${ROS_DISTRO}-geometry-msgs ros-${ROS_DISTRO}-nav-msgs ros-${ROS_DISTRO}-sensor-msgs \
  ros-${ROS_DISTRO}-std-msgs ros-${ROS_DISTRO}-nav2-msgs ros-${ROS_DISTRO}-slam-toolbox \
  ros-${ROS_DISTRO}-nav2-bringup ros-${ROS_DISTRO}-rosbridge-server

mkdir -p "${WS}/src"
rm -rf "${SRC}"
git clone --depth 1 "${REPO_URL}" "${SRC}"
cd "${WS}"
rosdep update || true
rosdep install --from-paths src --ignore-src -r -y || true
colcon build --symlink-install

cat > "${HOME}/.robot_env" <<EOF
source /opt/ros/${ROS_DISTRO}/setup.bash
source ${WS}/install/setup.bash
EOF
grep -qxF 'source ~/.robot_env' "${HOME}/.bashrc" || echo 'source ~/.robot_env' >> "${HOME}/.bashrc"

echo "Installation complete. Run: ros2 launch serving_robot bringup.launch.py"
echo "For tablet control also run: ros2 launch rosbridge_server rosbridge_websocket_launch.xml"
