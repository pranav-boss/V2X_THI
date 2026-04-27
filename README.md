# Detection Filter

A ROS 2 node that filters false-positive detections from a Cooperative Perception pipeline.  
It subscribes to `vision_msgs/Detection2DArray` messages on `fused/detections`, removes any detection whose `class_id` contains `"bed"`, and republishes the cleaned array on `filtered/fused/detections`.

## Repository Structure

```
.
├── detection_filter/               # ROS 2 Python package
│   ├── detection_filter/
│   │   └── filter_node.py          # Node implementation
│   ├── package.xml
│   ├── setup.py
│   └── setup.cfg
└── rosbag2_2026_03_30-17_51_06/    # Test bag file (MCAP, ~22 s, 220 messages)
```

## Topics

| Direction | Topic | Message Type |
|---|---|---|
| Subscribe | `fused/detections` | `vision_msgs/Detection2DArray` |
| Publish | `filtered/fused/detections` | `vision_msgs/Detection2DArray` |

The original message header and all fields of surviving detections are preserved.

---

## Prerequisites

| Option | Requirements |
|---|---|
| **A — Docker** (Windows / Mac / Linux, no ROS 2 install needed) | [Docker Desktop](https://www.docker.com/products/docker-desktop/) running |
| **B — Native ROS 2** (Linux only) | ROS 2 Jazzy + `ros-jazzy-vision-msgs` |

---

## Option A: Docker (Recommended for Windows)

Docker pulls the `ros:jazzy` image automatically on first run. Run all commands below from the **repository root**.

### Step 1 — Start an interactive container

**Git Bash / MINGW on Windows:**
```bash
MSYS_NO_PATHCONV=1 docker run --rm -it \
  -v "$(pwd):/v2x_thi" \
  ros:jazzy bash
```

**PowerShell on Windows:**
```powershell
docker run --rm -it `
  -v "${PWD}:/v2x_thi" `
  ros:jazzy bash
```

**Linux / macOS:**
```bash
docker run --rm -it \
  -v "$(pwd):/v2x_thi" \
  ros:jazzy bash
```

### Step 2 — Inside the container: install, build, run

```bash
# Install vision_msgs (mcap storage and colcon are pre-installed in ros:jazzy)
apt-get update -q && apt-get install -y ros-jazzy-vision-msgs

# Source ROS 2 and build the package
. /opt/ros/jazzy/setup.bash
mkdir -p /ros2_ws/src
cp -r /v2x_thi/detection_filter /ros2_ws/src/
cd /ros2_ws
colcon build --packages-select detection_filter
. /ros2_ws/install/setup.bash

# Start the filter node in the background
ros2 run detection_filter filter_node &

# Give the node 3 seconds to initialise
sleep 3

# Play the bag file in the background
ros2 bag play /v2x_thi/rosbag2_2026_03_30-17_51_06 &

# Echo the filtered topic for the duration of the bag (~22 s)
timeout 25 ros2 topic echo /filtered/fused/detections
```

Expected log line when the node starts:
```
[INFO] [detection_filter_node]: Detection Filter Node has been started.
```

### Step 3 — Verify the output

Every detection printed by `ros2 topic echo` should have `class_id: traffic light`. No `class_id: bed` should appear.

To capture and check automatically:
```bash
timeout 28 ros2 topic echo /filtered/fused/detections > /tmp/filtered_out.txt &
ros2 bag play /v2x_thi/rosbag2_2026_03_30-17_51_06
sleep 3
grep -qi "class_id: bed" /tmp/filtered_out.txt \
  && echo "FAIL — bed detections found" \
  || echo "PASS — no bed detections"
head -60 /tmp/filtered_out.txt
```

---

## Option B: Native ROS 2 (Linux)

### Install dependencies

```bash
sudo apt update
sudo apt install ros-jazzy-vision-msgs
```

### Build

```bash
mkdir -p ~/ros2_ws/src
cp -r detection_filter ~/ros2_ws/src/
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select detection_filter
source install/setup.bash
```

### Run and test (three terminals)

**Terminal 1 — start the filter node:**
```bash
source ~/ros2_ws/install/setup.bash
ros2 run detection_filter filter_node
```

**Terminal 2 — play the bag file:**
```bash
source ~/ros2_ws/install/setup.bash
ros2 bag play path/to/rosbag2_2026_03_30-17_51_06
```

**Terminal 3 — verify filtered output:**
```bash
source ~/ros2_ws/install/setup.bash
ros2 topic echo /filtered/fused/detections
```

---

## Expected Results

Verified with the provided bag file (`rosbag2_2026_03_30-17_51_06`, MCAP format, ROS 2 Jazzy):

| Metric | Value |
|---|---|
| Total messages in bag (`/fused/detections`) | 220 |
| Messages published to `/filtered/fused/detections` | 217 |
| Messages filtered out (`bed` class) | 3 |
| `bed` detections in filtered output | **0** |

Sample output from `/filtered/fused/detections`:
```yaml
header:
  stamp:
    sec: 1774885867
    nanosec: 17270155
  frame_id: fused
detections:
- results:
  - hypothesis:
      class_id: traffic light
      score: 0.7904731035232544
  ...
---
```

> **Note:** The `class_id` in the bag data is `"traffic light"` (with a space), not `"traffic_light"` (with an underscore).
