[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new)

# AWS EKS Cluster with [Kubeflow](https://kubeflow.org) (WIP)

_This implemtation leverages Pulumi and Python to provision and configure infrastructure on AWS consisting of an EKS Kubernetes cluster with an EBS-backed StorageClass, and deploys Kubeflow via Helm, granting permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf via custom extension of pulumi IAM modules_

_Derived from [`kubernetes-the-prod-way`](https://git.io/fjpBs)_