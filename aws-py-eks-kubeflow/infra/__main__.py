import pulumi
from pulumi import Config, export, Output, ResourceOptions
from pulumi_kubernetes import Provider
from pulumi_aws import ec2, eks, iam
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Pod, Service, Namespace

# Read in configurable settings for our cluster:
config = Config(None)

vpc = ec2.Vpc('eks-kfp', 
    cidr_block='10.0.0.0/24', 
    tags={
        'name' : 'value',
        'name' : 'value'
    }
)

sg = ec2.SecurityGroup('eks-kfp', 
    vpc_id=vpc.id,
    description="Allow all traffic and associate with our vpc",
    ingress=
    [
        {
            'from_port': 0,
            'to_port': 0,
            'protocol': '-1',
            'cidr_blocks': ["0.0.0.0/0"]
        }
    ],
    egress= 
    [
        {
            'from_port': 0,
            'to_port': 0,
            'protocol': '-1',
            'cidr_blocks': ["0.0.0.0/0"]
        }
    ]
)

kfp_cluster = eks.Cluster (
    'kfp',
    name='kfp',
    role_arn='arn:aws:iam::00000987654321:role/name',
    vpc_config={
        'subnet_ids' : ['subnet-XXXXXXXX','subnet-XXXXXXXX'],
        'security_group_ids': [sg.id]
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
    user: pulumi-eks-user
  name: {2}
current-context: {2}
kind: Config
preferences: {{}}
users:
- name: pulumi-eks-user
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
      env:
        - name: AWS_PROFILE
          value: "pulumi"
""".format(info[0]['data'], info[1], info[2], info[3], info[4], '{0}_{1}_{2}_{3}_{4}')
)

k8s_provider = Provider(
    'k8s', kubeconfig=k8s_config, cluster=kfp_cluster, __opts__=ResourceOptions(parent=kfp_cluster)
)

pulumi.export('kubeconfig', k8s_config)
pulumi.export('cluster_id', kfp_cluster.id)
pulumi.export('endpoint', kfp_cluster.endpoint)