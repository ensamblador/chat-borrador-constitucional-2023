from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ecs as ecs,

    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    aws_codebuild as codebuild,
    aws_ecs_patterns as ecs_patterns,
)
from aws_cdk.aws_ec2 import SecurityGroup, Port, Peer


class ECSDeployWithLoadBalancer(Construct):
    def __init__(self, scope: Construct, id: str, repo,  cluster, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.ecs_role = iam.Role( self,"Role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryPowerUser")],
        )

        task_image_opts = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
            image=ecs.ContainerImage.from_ecr_repository(repo, "latest"),
            container_port=8501,
            container_name="streamlit-chat",
            task_role=self.ecs_role
        )
        self.ecs_role.add_to_policy( iam.PolicyStatement(actions=["bedrock:*"], resources=["*"]))

        ecs_deployment = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "Service",
            cluster=cluster,
            memory_limit_mib=1024,
            cpu=512,
            task_image_options=task_image_opts,
        )
        self.service = ecs_deployment.service


class ECSDeployWithPublicIP(Construct):
    def __init__(self, scope: Construct, id: str, repo,  cluster, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.ecs_role = iam.Role( self,"ECSRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryPowerUser")],
        )

        self.ecs_role.add_to_policy( iam.PolicyStatement(actions=["bedrock:*"], resources=["*"]))

        task_definition = ecs.FargateTaskDefinition(
            self,
            "FTD",
            cpu=1024,
            memory_limit_mib=2048,
            task_role=self.ecs_role
        )

        task_definition.add_container(
            "streamlit",image=ecs.ContainerImage.from_ecr_repository(repo),
            port_mappings=[ ecs.PortMapping(container_port=8501, app_protocol=ecs.AppProtocol.http2, name= "streamlit-8501")])

        security_group = SecurityGroup(self, "SG", vpc=cluster.vpc, allow_all_outbound=True,  security_group_name="ToStreamlit",)
        
        security_group.add_ingress_rule(peer=Peer.any_ipv4(), connection=Port.tcp(8501), description="Allow Streamlit")

        ecs_service =  ecs.FargateService(
            self, "FS", cluster=cluster,
            assign_public_ip=True,
            task_definition=task_definition,
            security_groups=[security_group]
        )    

        self.service = ecs_service
