#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped, PoseArray
from math import sin, cos
import time

class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')
        self._action_client = ActionClient(self, FollowWaypoints, 'follow_waypoints')
        self.waypoints = [[-5.0, 8.0, 0.0], [5.0,2.0,-1.57],[2.0,-8.0,3.14],[-5.0,-8.0,1.57]]
        self._first_run = True
        self._wp_publisher = self.create_publisher(PoseArray, '/patrol_waypoints', 10)
        # Publish waypoints repeatedly so late-joining nodes receive them
        self.create_timer(2.0, self._publish_waypoints)
    def _publish_waypoints(self):
        msg = PoseArray()
        msg.header.frame_id = 'map'
        msg.poses = [self.create_pose(wp[0], wp[1], wp[2]).pose for wp in self.waypoints]
        self._wp_publisher.publish(msg)

    def create_pose(self, x, y, yaw):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z = sin(yaw/2)
        pose.pose.orientation.w = cos(yaw/2)
        return pose


    def send_points(self):
        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = [
            self.create_pose(wp[0], wp[1], wp[2]) for wp in self.waypoints
        ]
        self._action_client.wait_for_server(5)
        if self._first_run:
            import time
            time.sleep(10.0)
            self._first_run = False
        self.get_logger().info('Sending Patrol waypoints...')
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.result_callback)


    def result_callback(self, future):
        result = future.result()
        missed = result.result.missed_waypoints
        for wp in missed:
            i = wp.index
            self.get_logger().info(f'Missed waypoint object: {wp}')
            x=self.waypoints[i][0]
            y= self.waypoints[i][1]
            if x>=4 and x<=8 and y>=-3 and y<=3:
                self.get_logger().warn(f'Waypoint {i} at ({x:.2f}), ({y:.2f}) failed: Inside danger Zone')
            else:
                self.get_logger().warn(f'Waypoint {i} at ({x:.2f}), ({y:.2f}) failed: Blocked Path')
        self.get_logger().info('Patrol Successful,... Restarting...')
        self.send_points()


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    

    
    node.send_points()

    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()