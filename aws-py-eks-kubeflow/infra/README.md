[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new)

# AWS EKS Cluster with [Kubeflow](https://kubeflow.org), Identity (WIP)

_This implemtation leverages Pulumi and Python to provision and configure infrastructure on AWS consisting of an EKS Kubernetes cluster with an EBS-backed StorageClass, and deploys Kubeflow via Helm, granting permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf via resources defined in Identity stack, referenced_

> [NOTE](https://www.pulumi.com/docs/reference/python/): As of Pulumi 0.16.4, we have removed support for Python 2.7, and only support Python 3.6 or greater. You must have installed Python 3.6 prior to running Pulumi programs, or you will likely see syntax errors - Pulumi makes use of new Python syntax that is not backwards-compatible with Python 2. Older Pulumi versions did support Python 2.7.

## Deploying the App

To deploy your infrastructure, follow the below steps.

### Prerequisites

1. [Install Pulumi](https://www.pulumi.com/docs/reference/install/)
2. [Install Python 3.6+](https://www.python.org/downloads/)
3. [Configure AWS Credentials](https://www.pulumi.com/docs/reference/clouds/aws/setup/)
4. [Install `aws-iam-authenticator`](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html#get-started-kubectl)

### Steps

After cloning this repo, from this working directory, run the following commands:

- [ ] Install the required Python packages packages:

    ```bash
    $ pip install -r requirements.txt
    ```

- [ ] Create a new stack, which is an isolated deployment target for this example:

    ```bash
    $ pulumi stack init
    ```

- [ ] Set the required AWS configuration variables:

    This sets configuration options and default values for our cluster.

    ```bash
    $ pulumi config set aws:region us-east-1
    ```

- [ ] Stand up the EKS cluster:

    To preview and deploy changes, run `pulumi update` and select "yes."

    The `update` sub-command shows a preview of the resources that will be created
    and prompts on whether to proceed with the deployment. Note that the stack
    itself is counted as a resource, though it does not correspond
    to a physical cloud resource.

    You can also run `pulumi up --diff` to see and inspect the diffs of the
    overall changes expected to take place.

    Running `pulumi up` will deploy the EKS cluster. Note, provisioning a
    new EKS cluster takes between 10-15 minutes.

    ```bash
    $ pulumi update
    Previewing update (eks-demo):

        Type                                          Name                              	Plan
    +   pulumi:pulumi:Stack                           eks-hello-world-eks-demo     			create
    +   ├─ eks:index:Cluster                          helloworld                          	create
    +   │  ├─ eks:index:ServiceRole                   helloworld-eksRole                  	create
    +   │  │  ├─ aws:iam:Role                         helloworld-eksRole-role             	create
    +   │  │  ├─ aws:iam:RolePolicyAttachment         helloworld-eksRole-90eb1c99         	create
    +   │  │  └─ aws:iam:RolePolicyAttachment         helloworld-eksRole-4b490823         	create
    +   │  ├─ eks:index:ServiceRole                   helloworld-instanceRole             	create
    +   │  │  ├─ aws:iam:Role                         helloworld-instanceRole-role        	create
    +   │  │  ├─ aws:iam:RolePolicyAttachment         helloworld-instanceRole-03516f97    	create
    +   │  │  ├─ aws:iam:RolePolicyAttachment         helloworld-instanceRole-e1b295bd    	create
    +   │  │  └─ aws:iam:RolePolicyAttachment         helloworld-instanceRole-3eb088f2    	create
    +   │  ├─ pulumi-nodejs:dynamic:Resource          helloworld-cfnStackName             	create
    +   │  ├─ aws:ec2:SecurityGroup                   helloworld-eksClusterSecurityGroup  	create
    +   │  ├─ aws:iam:InstanceProfile                 helloworld-instanceProfile          	create
    +   │  ├─ aws:eks:Cluster                         helloworld-eksCluster               	create
    +   │  ├─ pulumi-nodejs:dynamic:Resource          helloworld-vpc-cni                  	create
    +   │  ├─ pulumi:providers:kubernetes             helloworld-eks-k8s                  	create
    +   │  ├─ aws:ec2:SecurityGroup                   helloworld-nodeSecurityGroup        	create
    +   │  ├─ kubernetes:core:ConfigMap               helloworld-nodeAccess               	create
    +   │  ├─ kubernetes:storage.k8s.io:StorageClass  helloworld-gp2                      	create
    +   │  ├─ aws:ec2:SecurityGroupRule               helloworld-eksClusterIngressRule    	create
    +   │  ├─ aws:ec2:LaunchConfiguration             helloworld-nodeLaunchConfiguration  	create
    +   │  ├─ aws:cloudformation:Stack                helloworld-nodes                    	create
    +   │  └─ pulumi:providers:kubernetes             helloworld-provider                 	create
    +   └─ aws-infra:network:Network                  vpc                               	create
    +      ├─ aws:ec2:Vpc                             vpc                               	create
    +      ├─ aws:ec2:Eip                             vpc-nat-0                         	create
    +      ├─ aws:ec2:Eip                             vpc-nat-1                         	create
    +      ├─ aws:ec2:InternetGateway                 vpc                               	create
    +      ├─ aws:ec2:Subnet                          vpc-nat-1                         	create
    +      ├─ aws:ec2:Subnet                          vpc-0                             	create
    +      ├─ aws:ec2:Subnet                          vpc-nat-0                         	create
    +      ├─ aws:ec2:Subnet                          vpc-1                             	create
    +      ├─ aws:ec2:RouteTable                      vpc                               	create
    +      ├─ aws:ec2:NatGateway                      vpc-nat-1                         	create
    +      ├─ aws:ec2:RouteTableAssociation           vpc-nat-1                         	create
    +      ├─ aws:ec2:NatGateway                      vpc-nat-0                         	create
    +      ├─ aws:ec2:RouteTableAssociation           vpc-nat-0                         	create
    +      ├─ aws:ec2:RouteTable                      vpc-nat-1                         	create
    +      ├─ aws:ec2:RouteTable                      vpc-nat-0                         	create
    +      ├─ aws:ec2:RouteTableAssociation           vpc-1                             	create
    +      └─ aws:ec2:RouteTableAssociation           vpc-0                             	create

    Resources:
        + 42 to create

    clusterng (eks-demo):

        Type                                          Name                              	Status      Info
    +   pulumi:pulumi:Stack                           eks-hello-world-eks-demo     			created
    +   ├─ eks:index:Cluster                          helloworld                          	created
    +   │  ├─ eks:index:ServiceRole                   helloworld-eksRole                  	created
    +   │  │  ├─ aws:iam:Role                         helloworld-eksRole-role             	created
    +   │  │  ├─ aws:iam:RolePolicyAttachment         helloworld-eksRole-90eb1c99         	created
    +   │  │  └─ aws:iam:RolePolicyAttachment         helloworld-eksRole-4b490823         	created
    +   │  ├─ eks:index:ServiceRole                   helloworld-instanceRole             	created
    +   │  │  ├─ aws:iam:Role                         helloworld-instanceRole-role        	created
    +   │  │  ├─ aws:iam:RolePolicyAttachment         helloworld-instanceRole-3eb088f2    	created
    +   │  │  ├─ aws:iam:RolePolicyAttachment         helloworld-instanceRole-03516f97    	created
    +   │  │  └─ aws:iam:RolePolicyAttachment         helloworld-instanceRole-e1b295bd    	created
    +   │  ├─ pulumi-nodejs:dynamic:Resource          helloworld-cfnStackName             	created
    +   │  ├─ aws:iam:InstanceProfile                 helloworld-instanceProfile          	created
    +   │  ├─ aws:ec2:SecurityGroup                   helloworld-eksClusterSecurityGroup  	created
    +   │  ├─ aws:eks:Cluster                         helloworld-eksCluster               	created
    +   │  ├─ pulumi:providers:kubernetes             helloworld-eks-k8s                  	created
    +   │  ├─ pulumi-nodejs:dynamic:Resource          helloworld-vpc-cni                  	created
    +   │  ├─ aws:ec2:SecurityGroup                   helloworld-nodeSecurityGroup        	created
    +   │  ├─ kubernetes:core:ConfigMap               helloworld-nodeAccess               	created
    +   │  ├─ kubernetes:storage.k8s.io:StorageClass  helloworld-gp2                      	created
    +   │  ├─ aws:ec2:SecurityGroupRule               helloworld-eksClusterIngressRule    	created
    +   │  ├─ aws:ec2:LaunchConfiguration             helloworld-nodeLaunchConfiguration  	created
    +   │  ├─ aws:cloudformation:Stack                helloworld-nodes                    	created
    +   │  └─ pulumi:providers:kubernetes             helloworld-provider                 	created
    +   └─ aws-infra:network:Network                  vpc                               	created
    +      ├─ aws:ec2:Vpc                             vpc                               	created
    +      ├─ aws:ec2:Eip                             vpc-nat-0                         	created
    +      ├─ aws:ec2:Eip                             vpc-nat-1                         	created
    +      ├─ aws:ec2:InternetGateway                 vpc                               	created
    +      ├─ aws:ec2:Subnet                          vpc-nat-1                         	created
    +      ├─ aws:ec2:Subnet                          vpc-0                             	created
    +      ├─ aws:ec2:Subnet                          vpc-nat-0                         	created
    +      ├─ aws:ec2:Subnet                          vpc-1                             	created
    +      ├─ aws:ec2:RouteTable                      vpc                               	created
    +      ├─ aws:ec2:NatGateway                      vpc-nat-1                         	created
    +      ├─ aws:ec2:NatGateway                      vpc-nat-0                         	created
    +      ├─ aws:ec2:RouteTableAssociation           vpc-nat-0                         	created
    +      ├─ aws:ec2:RouteTableAssociation           vpc-nat-1                         	created
    +      ├─ aws:ec2:RouteTable                      vpc-nat-1                         	created
    +      ├─ aws:ec2:RouteTableAssociation           vpc-1                             	created
    +      ├─ aws:ec2:RouteTable                      vpc-nat-0                         	created
    +      └─ aws:ec2:RouteTableAssociation           vpc-0                             	created

    Diagnostics:
    pulumi:pulumi:Stack (eks-hello-world-eks-demo):

    Outputs:
        kubeconfig: {
            apiVersion     : "v1"
            clusters       : [
                [0]: {
                    cluster: {
                        certificate-authority-data: "<CERT_DATA>"
                        server                    : "https://<SERVER_ADDR>.us-west-2.eks.amazonaws.com"
                    }
                    name   : "kubernetes"
                }
            ]
            contexts       : [
                [0]: {
                    context: {
                        cluster: "kubernetes"
                        user   : "aws"
                    }
                    name   : "aws"
                }
            ]
            current-context: "aws"
            kind           : "Config"
            users          : [
                [0]: {
                    name: "aws"
                    user: {
                        exec: {
                            apiVersion: "client.authentication.k8s.io/v1alpha1"
                            args      : [
                                [0]: "token"
                                [1]: "-i"
                                [2]: "helloworld-eksCluster-e9e1711"
                            ]
                            command   : "aws-iam-authenticator"
                        }
                    }
                }
            ]
        }

    Resources:
        + 42 created

    Duration: 13m7s
    ```

- [ ] After 10-15 minutes, your cluster will be ready, and the kubeconfig JSON you'll use to connect to the cluster will
   be available as an output.

    As part of the update, you'll see some new objects in the output: a
    `Namespace` in Kubernetes to deploy into, a `Deployment` resource for
    the NGINX app, and a LoadBalancer `Service` to publicly access NGINX.

    Pulumi understands which changes to a given cloud resource can be made
    in-place, and which require replacement, and computes
    the minimally disruptive change to achieve the desired state.

	> **Note:** Pulumi auto-generates a suffix for all objects.
    > See the [Pulumi Programming Model](../../reference/programming-model.md#autonaming) for more info.
    >
    > ```
    > deploymentName : "pulumi-eks-kubeflow-58jkmc7c"
    > ...
    > namespaceName  : "pulumi-eks-kubeflow-xaldhgca"
    > serviceHostname: "a71f5ab3f2a6e11e3ac39200f4a9ad5d-1297981966.us-west-2.elb.amazonaws.com"
    > serviceName    : "pulumi-eks-kubeflow-3fc2uhh7"
    > ```

    If you visit the FQDN listed in `serviceHostname` you should land on the
    NGINX welcome page. Note, that it may take a minute or so for the
    LoadBalancer to become active on AWS.

- [ ] Access the Kubernetes Cluster using `kubectl`

    To access your new Kubernetes cluster using `kubectl`, we need to setup the
    `kubeconfig` file and download `kubectl`. We can leverage the Pulumi
    stack output in the CLI, as Pulumi faciliates exporting these objects for us.

    ```bash
    $ pulumi stack output kubeconfig > kubeconfig
    $ export KUBECONFIG=$PWD/kubeconfig
    $ export KUBERNETES_VERSION=1.13.5 && sudo curl -s -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/v${KUBERNETES_VERSION}/bin/linux/amd64/kubectl && sudo chmod +x /usr/local/bin/kubectl

    $ kubectl version
    $ kubectl cluster-info
    $ kubectl get nodes
    ```

    We can also use the stack output to query the cluster for our newly created Deployment:

    ```bash
    $ kubectl get deployment $(pulumi stack output deploymentName) --namespace=$(pulumi stack output namespaceName)
    $ kubectl get service $(pulumi stack output serviceName) --namespace=$(pulumi stack output namespaceName)
    ```

    We can also create another NGINX Deployment into the `default` namespace using
    `kubectl` natively:

    ```bash
    $ kubectl create deployment my-nginx --image=nginx
    $ kubectl get pods
    $ kubectl delete deployment my-nginx
    ```

    By deploying this nginx image in this way, it is outside of Pulumi's control. But this is simply to show that we can
    control our cluster via the CLI as well. 

- [ ] Once you've finished experimenting, tear down your stack's resources by destroying and removing it:

    ```bash
    $ pulumi destroy --yes
    $ pulumi stack rm --yes
    ```


- [ ] Using Custom Resources

    ```py
    import modules
    a = modules.A()
    b = modules.B()

    a.spam()
    b.foo()



    import modules

    a = modules.Oscar()
    b = modules.Alchemic()

    a.rasa_nlu()
    b.transmutate()
    ```