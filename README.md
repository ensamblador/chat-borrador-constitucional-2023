### Prerequisites

- Install AWS Cli
- Create AWS user and AWS profile
- Install CDK
- Create a Bootstrap Stack if this is your first cdk project in this account / region

- In order to call Amazon Bedrock Models for the first time, you'll need to enable model access in Bedrock Console.

```sh
cdk bootstrap aws://{your_aws_account}/{region}
```

### Setup

Clone this repo:


```sh
git clone https://github.com/ensamblador/chat-borrador-constitucional-2023.git
cd chat-borrador-constitucional-2023.git
```

Activate virtual environment:

```sh
python3 -m venv .venv
```


Install the required packages:

```sh
pip install -r requirements.txt
```

After installing try `cdk synth` or `cdk diff`. If you are free of errors, your can go to ***Step 1***

### Step 1: Build Container Image 

execute `cdk deploy` to automatically create (with infraestructure as code):

- ECR Repo
- S3 Bucket (for container assets)
- Code Build project to build and push the container image (and necessary permissions)
- Code Pipeline with S3 Source Action and Build Action
- ECS Cluster to deploy services in next step

Go to the [AWS Codepipeline console](https://us-east-1.console.aws.amazon.com/codesuite/codepipeline/pipelines) and review that BuildAndPush Stage is succeeded. If not, take a look at the logs (view logs button) if it says "Too many requests" just hit retry failed actions button in the stage.

Go to [Amazon Elastic Container Registry console](https://us-east-1.console.aws.amazon.com/ecr/repositories) and take a look at the new created container image (the one that starts with ***constitucionchat-build***)

### Step 2: Launch the Load Balanced Fargate Service

just go to the file `streamlit_service/streamlit_service_stack.py`and uncomment the following line (near line 36):

```python
self.ecs_service = ECSDeployWithLoadBalancer(self, "ServiceALB", repo=self.ecr_build.repo, cluster= self.ecs_cluster)
```

save the file and again in the terminal do a `cdk deploy`. That will deploy an ECS Service in the cluster using the container image that you just created.

After the deployment you'll se in outputs the following:

```sh
 ✅  ConstitucionChat

✨  Deployment time: 288.27s

Outputs:
ConstitucionChat.ServiceALBServiceServiceURLF1DA47DB = http://Consti-Servi-XXXXXX-XXXXX.us-east-1.elb.amazonaws.com
```

Navigate to the url an enjoy your chatbot.

