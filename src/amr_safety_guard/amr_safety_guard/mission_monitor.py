#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseArray
from nav2_msgs.action._follow_waypoints import FollowWaypoints_FeedbackMessage
import cv2
import numpy as np

DANGER_ZONE = {'x_min': 4.0, 'x_max': 8.0, 'y_min': -3.0, 'y_max': 3.0}

GREEN = (60, 200, 60)
RED   = (60, 60, 220)
WHITE = (240, 240, 240)
GRAY  = (160, 160, 160)
BG    = (28, 28, 28)


def in_danger(x, y):
    dz = DANGER_ZONE
    return dz['x_min'] <= x <= dz['x_max'] and dz['y_min'] <= y <= dz['y_max']


class MissionMonitor(Node):
    def __init__(self):
        super().__init__('mission_monitor')
        self.get_logger().set_level(rclpy.logging.LoggingSeverity.FATAL)

        self.waypoints = []      # list of (x, y) received from patrol_node
        self.current_wp = 0
        self.person_detected = False

        self.create_subscription(PoseArray, '/patrol_waypoints', self.wp_callback, 10)
        self.create_subscription(
            FollowWaypoints_FeedbackMessage,
            '/follow_waypoints/_action/feedback',
            self.feedback_callback,
            10
        )
        self.create_subscription(String, '/person_detected', self.person_callback, 10)
        self.create_timer(0.1, self.render)

    def wp_callback(self, msg):
        self.waypoints = [(p.position.x, p.position.y) for p in msg.poses]

    def feedback_callback(self, msg):
        self.current_wp = msg.feedback.current_waypoint

    def person_callback(self, msg):
        self.person_detected = True

    def render(self):
        img = np.full((320, 460, 3), BG, dtype=np.uint8)

        cv2.putText(img, 'AMR MISSION MONITOR', (14, 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (80, 160, 255), 2, cv2.LINE_AA)
        cv2.line(img, (0, 44), (460, 44), (60, 60, 60), 1)

        if not self.waypoints:
            cv2.putText(img, 'Waiting for patrol node...', (14, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, GRAY, 1, cv2.LINE_AA)
        else:
            y = 72
            for i, (wx, wy) in enumerate(self.waypoints):
                danger = in_danger(wx, wy)
                is_current = (i == self.current_wp)

                if is_current:
                    cv2.rectangle(img, (10, y - 18), (450, y + 8), (50, 50, 50), -1)

                prefix = '>> ' if is_current else '   '
                label_color = WHITE if is_current else GRAY
                cv2.putText(img, f'{prefix}WP {i}  ({wx:+.1f}, {wy:+.1f})',
                            (18, y), cv2.FONT_HERSHEY_SIMPLEX, 0.58, label_color, 1, cv2.LINE_AA)

                tag, col = ('DANGER ZONE - SKIP', RED) if danger else ('SAFE', GREEN)
                cv2.putText(img, tag, (300, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.52, col, 1, cv2.LINE_AA)
                y += 34

            cv2.line(img, (0, y), (460, y), (60, 60, 60), 1)
            y += 22
            if self.person_detected:
                cv2.putText(img, 'PERSON DETECTED', (14, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.72, RED, 2, cv2.LINE_AA)
            else:
                cv2.putText(img, 'No person detected', (14, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, GREEN, 1, cv2.LINE_AA)

        cv2.imshow('AMR Mission Monitor', img)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = MissionMonitor()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
