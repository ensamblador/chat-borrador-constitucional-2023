import aws_cdk as core
import aws_cdk.assertions as assertions

from super_duper_demo.super_duper_demo_stack import SuperDuperDemoStack

# example tests. To run these tests, uncomment this file along with the example
# resource in super_duper_demo/super_duper_demo_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SuperDuperDemoStack(app, "super-duper-demo")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
