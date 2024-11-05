import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from openai import OpenAI

class APIClientNode(Node):
    def __init__(self):
        super().__init__('api_client_node')
        
        # Initialize the OpenAI client
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key="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"
        )
        
        # Subscription to a topic that will provide input for the API
        self.subscription = self.create_subscription(
            String,
            '/robot_control_command',
            self.api_request_callback,
            10
        )
        self.get_logger().info('API Client Node started, waiting for commands.')

    def api_request_callback(self, msg):
        user_input = msg.data
        self.get_logger().info(f"Received command: {user_input}")
        
        # Make the API call and stream the response
        completion = self.client.chat.completions.create(
            model="meta/llama3-70b-instruct",
            messages=[{"role": "user", "content": user_input}],
            temperature=0.5,
            top_p=1,
            max_tokens=1024,
            stream=True
        )
        
        # Print the response content as it's received
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")

def main(args=None):
    rclpy.init(args=args)
    api_client_node = APIClientNode()
    
    try:
        rclpy.spin(api_client_node)
    except KeyboardInterrupt:
        pass
    finally:
        api_client_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

