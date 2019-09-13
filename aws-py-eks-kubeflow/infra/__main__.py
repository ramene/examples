# import sys
import pulumi
# from ruamel.yaml import YAML
from pulumi_kubernetes import Provider
from pulumi_random import RandomPassword
from pulumi import Config, export, Output, ResourceOptions
from pulumi_aws import ec2, eks, iam, cloudformation as cfn
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import ConfigMap, Pod, Service, Namespace

# Read in configurable settings for our cluster:
config = pulumi.Config(None)

# PREFIX = config.require("prefix") or ''

# nodeCount is the number of cluster nodes to provision.
KUBEFLOW_VERSION = config.get('kubeflow_version') or '0.6'
#
AMI = config.get('ami') or 'ami-08739803f18dcc019'
#
KEYPAIR = config.get('keypair') or 'kfp'
#
PASSWORD = config.get_secret('password') or  RandomPassword("password", length=16, override_special= "/@\" ",special=True).result
#
TEMPLATE_URL = config.get('template_url') or 'https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2019-02-11/amazon-eks-nodegroup.yaml'
# Instance type(s) of the AMI
INSTANCE_TYPE = config.get('instance_type') or 't3.medium'

# https://learn.hashicorp.com/terraform/aws/eks-intro#worker-node-autoscaling-group
# https://github.com/terraform-providers/terraform-provider-aws/blob/master/website/docs/r/launch_configuration.html.markdown
# https://github.com/terraform-providers/terraform-provider-aws/blob/master/website/docs/r/iam_instance_profile.html.markdown

eks_role = iam.Role('eks-role',
    assume_role_policy='{\"Version\":\"2012-10-17\",\"Statement\":[{\"Action\":[\"sts:AssumeRole\"],\"Effect\":\"Allow\",\"Principal\":{\"Service\":[\"eks.amazonaws.com\"]}}]}',
    description='Allows EKS to manage clusters on your behalf.',
    max_session_duration='3600',
    path='/',
    force_detach_policies=False,
)

ec2_role = iam.Role('ec2-role',
    assume_role_policy='{\"Version\":\"2012-10-17\",\"Statement\":[{\"Action\":[\"sts:AssumeRole\"],\"Effect\":\"Allow\",\"Principal\":{\"Service\":[\"ec2.amazonaws.com\"]}}]}',
    max_session_duration='3600',
    path='/',
    force_detach_policies=False,
)

eks_role_policy_0 = iam.RolePolicyAttachment('eks-role-policy-0', 
    policy_arn='arn:aws:iam::aws:policy/AmazonEKSClusterPolicy', 
    role=eks_role.name
)

eks_role_policy_1 = iam.RolePolicyAttachment('eks-role-policy-1', 
    policy_arn='arn:aws:iam::aws:policy/AmazonEKSServicePolicy', 
    role=eks_role.name
)

instance_role_policy_0 = iam.RolePolicyAttachment('instance-role-policy-0', 
    policy_arn='arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly', 
    role=ec2_role.name
)

instance_role_policy_1 = iam.RolePolicyAttachment('instance-role-policy-1', 
    policy_arn='arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy', 
    role=ec2_role.name
)

instance_role_policy_2 = iam.RolePolicyAttachment('instance-role-policy-2', 
    policy_arn='arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy', 
    role=ec2_role.name
)

vpc = ec2.Vpc('eks-vpc', 
    cidr_block='10.100.0.0/16',
    instance_tenancy='default',
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        'Name' : 'vpc',
        'kubernetes.io/cluster/pulumi-kubeflow-ml' : 'shared'
    }
)

# https://github.com/terraform-providers/terraform-provider-aws/blob/master/website/docs/r/security_group.html.markdown
eks_cluster_sg = ec2.SecurityGroup('eks-cluster-sg', 
    vpc_id=vpc.id,
    description='Allow all traffic and associate with our vpc',
    tags={
        'Name' : 'eks-cluster-sg'
    },
    egress=[{
            'cidr_blocks' : ["0.0.0.0/0"],
            'from_port' : '0',
            'to_port' : '0',
            'self' : False,
            'protocol' : '-1',
            'description' : 'Allow internet access.'
        }
    ],
    ingress=[{
            'cidr_blocks' : ["0.0.0.0/0"],
            'from_port' : '443',
            'to_port' : '443',
            'protocol' : 'tcp',
            'description' : 'Allow pods to communicate with the cluster API Server.'
        },
        {
            'cidr_blocks' : ["0.0.0.0/0"],
            'from_port' : '80',
            'to_port' : '80',
            'protocol' : 'tcp',
            'description' : 'Allow internet access to pods'
        }
    ]
)

# https://aws.amazon.com/lambda/edge/
edge = ec2.InternetGateway('edge',
    vpc_id=vpc.id,
    tags={
        'Name' : 'vpc'
    }
)

vpc_0_subnet = ec2.Subnet('vpc-0-subnet', 
    assign_ipv6_address_on_creation=False,
    vpc_id=vpc.id,
    map_public_ip_on_launch=True,
    cidr_block='10.100.1.0/24',
    availability_zone='us-east-1b',
    tags={
        'Name' : 'vpc-0-subnet',
        'kubernetes.io/cluster/pulumi-kubeflow-ml' : 'shared'
    }
)

vpc_1_subnet = ec2.Subnet('vpc-1-subnet', 
    assign_ipv6_address_on_creation=False,
    vpc_id=vpc.id,
    map_public_ip_on_launch=True,
    cidr_block='10.100.0.0/24',
    availability_zone='us-east-1a',
    tags={
        'Name' : 'vpc-1-subnet',
        'kubernetes.io/cluster/pulumi-kubeflow-ml' : 'shared'
    }
)

# https://github.com/terraform-providers/terraform-provider-aws/blob/master/website/docs/r/route_table.html.markdown
eks_route_table = ec2.RouteTable('eks-route-table',
    vpc_id=vpc.id,
    routes=[{
            'cidr_block' : '0.0.0.0/0',
            'gateway_id' : edge.id
        }
    ],
    tags={
        'Name' : 'vpc'
    }
)

vpc_0_route_table_assoc = ec2.RouteTableAssociation('vpc-0-route-table-assoc',
    route_table_id=eks_route_table.id,
    subnet_id=vpc_0_subnet.id
)

vpc_1_route_table_assoc = ec2.RouteTableAssociation('vpc-1-route-table-assoc',
    route_table_id=eks_route_table.id,
    subnet_id=vpc_1_subnet.id
)

kfp_cluster = eks.Cluster (
    'pulumi-kubeflow-ml',
    name='pulumi-kubeflow-ml',
    role_arn=eks_role.arn,
    vpc_config={
        'subnet_ids' : [vpc_0_subnet.id, vpc_1_subnet.id],
        'security_group_ids': [eks_cluster_sg.id]
    }, 
    enabled_cluster_log_types=['api']
)

k8s_info = Output.all(kfp_cluster.certificate_authority, kfp_cluster.endpoint, kfp_cluster.name, kfp_cluster.id, kfp_cluster.role_arn)

k8s_config = k8s_info.apply(
    lambda info: """apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {0}
    server: {1}
  name: {2} 
contexts:
- context:
    cluster: {2}
    user: aws
  name: {2}
current-context: {2}
kind: Config
preferences: {{}}
users:
- name: aws
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws
      args:
        - "eks"
        - "get-token"
        - "--cluster-name"
        - {2}
""".format(info[0]['data'], info[1], info[2], '{0}_{1}_{2}')
)

k8s_provider = Provider(
    'pulumi-kubernetes', kubeconfig=k8s_config, cluster=kfp_cluster, __opts__=ResourceOptions(parent=kfp_cluster)
)

subnet_info = Output.all(vpc_0_subnet.id, vpc_1_subnet.id)

subnet_list = subnet_info.apply(
    lambda subnets: """{0}, {1}""".format(subnets[0], subnets[1], '{0}_{1}')
)

# https://github.com/terraform-providers/terraform-provider-aws/blob/master/website/docs/r/cloudformation_stack.html.markdown
kfp_worker_nodes = cfn.Stack('kfp-worker-nodes', 
    template_url=TEMPLATE_URL,
    name='kfp-worker-nodes',
    capabilities= 
    [
          ['CAPABILITY_IAM'][0]
    ],
    parameters={
        'VpcId' : vpc.id, 
        'Subnets' : subnet_list,
        'ClusterName' : kfp_cluster.name,
        'ClusterControlPlaneSecurityGroup' : eks_cluster_sg.id,
        'NodeGroupName' : 'kfp-worker-nodes',
        'NodeAutoScalingGroupMinSize' : 1,
        'NodeAutoScalingGroupDesiredCapacity' : 3,
        'NodeAutoScalingGroupMaxSize' : 4,
        'NodeInstanceType' : INSTANCE_TYPE,
        'NodeImageId' : AMI,
        'KeyName' : KEYPAIR
    },
    # on_failure='ROLLBACK',
    disable_rollback=True
)

# yaml_str = """\
#   mapRoles: |
#       username: system:node:{{EC2PrivateDNSName}}
#       groups:
#         - system:bootstrappers
#         - system:nodes
# """

# yaml = YAML()
# arn_data = yaml.load(yaml_str)
# arn_data.insert(1, '- rolearn', kfp_worker_nodes.outputs.__getitem__('NodeInstanceRole'), comment="new key")
# # yaml.dump(f"arn_data", sys.stdout)

# configMap = ConfigMap('configMap', 
#     data=arn_data,
#     metadata={
#         'name' : 'aws-auth',
#         'namespace' : 'kube-system'
#     },
#     opts=ResourceOptions(parent=kfp_cluster, depends_on=[kfp_cluster])
# )

labels = {"app": "nginx"}

# Create a canary deployment to test that this cluster works.
# nginx = Deployment(
#     "k8s-nginx",
#     spec={
#         "selector": {"matchLabels": labels},
#         "replicas": 1,
#         "template": {
#             "metadata": {"labels": labels},
#             "spec": {"containers": [{"name": "nginx", "image": "nginx"}]},
#         },
#     },
#     __opts__=ResourceOptions(parent=k8s_provider, provider=k8s_provider),
# )

# ingress = Service(
#     "k8s-nginx",
#     spec={"type": "LoadBalancer", "selector": labels, "ports": [{"port": 80}]},
#     __opts__=ResourceOptions(parent=k8s_provider, provider=k8s_provider),
# )

pulumi.export('kubeconfig', k8s_config)
pulumi.export('cluster_id', kfp_cluster.id)
pulumi.export('endpoint', kfp_cluster.endpoint)
pulumi.export('role_arn', kfp_cluster.role_arn)
# pulumi.export('hostname', Output.all(ingress.status['load_balancer']['ingress'][0]['hostname']))
pulumi.export('NodeInstanceRole', kfp_worker_nodes.outputs.__getitem__('NodeInstanceRole'))
pulumi.export('NodeSecurityGroup', kfp_worker_nodes.outputs.__getitem__('NodeSecurityGroup'))