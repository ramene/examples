import pulumi
from pulumi import Config, export, Output, ResourceOptions

from pulumi_aws import ec2, eks, iam
from pulumi_kubernetes import Provider
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Pod, Service, Namespace

# Read in configurable settings for our cluster:
config = Config(None)

# stk = pulumi.StackReference("ramene/kfp/identity")

# kubeAppRoleArn = stk.get_output("kubeAppRoleArn")

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
    cidr_block='10.10.0.0/16',
    # instance_tenancy='default',
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        'Name' : 'vpc'
    }
)

eks_cluster_sg = ec2.SecurityGroup('eks-cluster-sg', 
    vpc_id=vpc.id,
    description='Allow all traffic and associate with our vpc',
    revoke_rules_on_delete=True,
    tags={
        'Name' : 'eksClusterSecurityGroup'
    }
)

eks_cluster_egress_rule = ec2.SecurityGroupRule('eks-cluster-egress-rule',
    security_group_id=eks_cluster_sg.id,
    cidr_blocks=["0.0.0.0/0"],
    from_port='0',
    to_port='0',
    self=False,
    protocol='-1',
    type='egress',
    description='Allow internet access.'
)

eks_cluster_ingress_rule = ec2.SecurityGroupRule('eks-cluster-ingress-rule',
    security_group_id=eks_cluster_sg.id,
    from_port='443',
    to_port='443',
    protocol='tcp',
    type='ingress',
    description='Allow pods to communicate with the cluster API Server.'
)

gateway = ec2.InternetGateway('eks-gateway',
    vpc_id=vpc.id,
    tags={
        'Name' : 'vpc'
    }
)

vpc_0_subnet = ec2.Subnet('vpc-0', 
    assign_ipv6_address_on_creation=False,
    vpc_id=vpc.id,
    map_public_ip_on_launch=True,
    cidr_block='10.10.1.0/24',
    availability_zone='us-east-1b',
    tags={
        'Name' : 'vpc-0'
    }
)

vpc_1_subnet = ec2.Subnet('vpc-1', 
    assign_ipv6_address_on_creation=False,
    vpc_id=vpc.id,
    map_public_ip_on_launch=True,
    cidr_block='10.10.0.0/24',
    availability_zone='us-east-1a',
    tags={
        'Name' : 'vpc-1'
    }
)

eks_route_table = ec2.RouteTable('eks-route-table',
    vpc_id=vpc.id,
    routes={
        'cidr_blocks' : '0.0.0.0/0',
        'gateway_id': gateway.id
    },
    tags={
        'Name' : 'vpc'
    }
)

vpc0_route_table_assoc = ec2.RouteTableAssociation('vpc-0',
    route_table_id=eks_route_table.id,
    subnet_id=vpc_0_subnet.id
)

vpc1_route_table_assoc = ec2.RouteTableAssociation('vpc-1',
    route_table_id=eks_route_table.id,
    subnet_id=vpc_1_subnet.id
)

# vpc_info = Output.all(vpc.default_security_group_id)

kfp_cluster = eks.Cluster (
    'pulumi-kubeflow-ml',
    name='pulumi-kubeflow-ml',
    role_arn=eks_role.arn,
    vpc_config={
        'subnet_ids' : [vpc_0_subnet.id, vpc_1_subnet.id],
        'security_group_ids': [eks_cluster_sg.id]
    },
    enabled_cluster_log_types=['api', 'audit', 'authenticator', 'controllerManager', 'scheduler'],
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
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - {3}
        - "-r"
        - {4}
""".format(info[0]['data'], info[1], info[2], info[3], info[4], '{0}_{1}_{2}_{3}_{4}')
)

k8s_provider = Provider(
    'k8s', kubeconfig=k8s_config, cluster=kfp_cluster, __opts__=ResourceOptions(parent=kfp_cluster)
)

# provider_info = Output.all(k8s_provider)

# pulumi.export('kubeAppRoleArn', kubeAppRoleArn)
# pulumi.export('provider', provider_info)
pulumi.export('kubeconfig', k8s_config)
pulumi.export('cluster_id', kfp_cluster.id)
pulumi.export('endpoint', kfp_cluster.endpoint)