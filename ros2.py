#https://prometheus.github.io/client_python/exporting/pushgateway/
import rclpy
from rclpy.node import Node
from prometheus_client import generate_latest, Gauge, CollectorRegistry, push_to_gateway
import socket

registry = CollectorRegistry()
nodes_last_run = [ ]
# Define Prometheus metrics
node_state_metric = Gauge('ros2_node_state', 'ROS 2 Node State', ['node_name','host_name'],registry=registry)

class NodeStatusPublisher(Node):
    def __init__(self):
        super().__init__('node_status_publisher')

    def publish_node_status(self):
        global nodes_last_run

        nodes_latest_run = self.get_node_names()

        nodes_expired = list (set(nodes_last_run) - set(nodes_latest_run))
        nodes_new = list(set(nodes_latest_run) - set(nodes_last_run))
        nodes_common = list(set(nodes_last_run) & set(nodes_latest_run))

        for item in nodes_expired:
            if  "ros2cli" not in item and item != '':
                host_name=socket.gethostname()
                node_state_metric.labels(node_name=item, host_name=host_name).set(0)

        for item in nodes_new:
            if  "ros2cli" not in item and item != '':
                host_name=socket.gethostname()
                node_state_metric.labels(node_name=item, host_name=host_name).set(1)

        for item in nodes_common:
            if  "ros2cli" not in item and item != '':
                host_name=socket.gethostname()
                node_state_metric.labels(node_name=item, host_name=host_name).set(1)

        nodes_last_run  = nodes_last_run + nodes_new

def main():
    rclpy.init()
    node = NodeStatusPublisher()

    try:
        while True:
            node.publish_node_status()
            # Generate and print Prometheus metrics
            push_to_gateway('localhost:9091', job='ros2_node_metrics', registry=registry)
            rclpy.spin_once(node, timeout_sec=5)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
