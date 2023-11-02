from aws_cdk import (
    # Duration,
    Stack,
    aws_ecs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
)


from constructs import Construct
from aws_cdk.aws_s3_assets import Asset

from cognito_stack import UserPool

from ecs import ECRBuildAndPushFromS3, ECSDeployWithLoadBalancer


class StreamlitServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.asset = Asset(self, "Zipped",path="streamlit")
        self.create_user_pool()
        self.create_ecs_streamlit_app()
        # self.create_ecs_CICD()


    def create_ecs_streamlit_app(self):
        source_bucket = self.asset.bucket
        self.ecr_build = ECRBuildAndPushFromS3(
            self,
            "Build",
            source_bucket=source_bucket,
            source_key=self.asset.s3_object_key,
            buildspec_location="streamlit/buildspec.yml",
        )

        self.asset.grant_read(self.ecr_build.build_role)

        task_environment = {
            "POOL_ID": self.users.pool_id,
            "APP_CLIENT_ID": self.users.app_client_id,
            "APP_CLIENT_SECRET": self.users.app_client_secret
        }

        self.ecs_cluster = aws_ecs.Cluster(self, "C", cluster_name="StreamlitServices")
        env = self.task_environment if self.task_environment else None
        self.ecs_service = ECSDeployWithLoadBalancer(
            self, "L", repo=self.ecr_build.repo, cluster= self.ecs_cluster, env=env)
        task_image = self.ecs_service.task_image_opts


    
    def create_ecs_CICD(self):
        self.ecr_build.add_deploy(self.ecs_service.service)

    def create_user_pool(self):
        self.users = UserPool(self, "Users")
        self.task_environment = {
            "POOL_ID": self.users.pool_id,
            "APP_CLIENT_ID": self.users.app_client_id,
            "APP_CLIENT_SECRET": self.users.app_client_secret
        }
