from aws_cdk import (
    # Duration,
    Stack,
    aws_ecs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
)


from constructs import Construct

from s3_cloudfront import S3Deploy
from ecs import ECRBuildAndPushFromS3, ECSDeployWithLoadBalancer


class StreamlitServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.create_ecs_streamlit_app()
        #self.create_ecs_CICD()


    def create_ecs_streamlit_app(self):
        s3_deploy = S3Deploy(self, "streamlit", "streamlit", "streamlit")
        source_bucket = s3_deploy.bucket

        self.ecr_build = ECRBuildAndPushFromS3(
            self,
            "Build",
            source_bucket=source_bucket,
            source_key="streamlit/zipped_folder.zip",
            buildspec_location="streamlit/buildspec.yml",
        )
        self.ecs_cluster = aws_ecs.Cluster(self, "C", cluster_name="StreamlitServices")
        self.ecs_service = ECSDeployWithLoadBalancer(self, "ServiceALB", repo=self.ecr_build.repo, cluster= self.ecs_cluster)
    
    def create_ecs_CICD(self):
        self.ecr_build.add_deploy(self.ecs_service.service)