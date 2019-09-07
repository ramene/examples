[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new)

# AWS EKS Identity with Pulumi (WIP)

_This implemtation leverages Pulumi and Python to provision and configure infrastructure on AWS consisting of an EKS Kubernetes cluster with an EBS-backed StorageClass, and deploys Kubeflow via Helm, granting permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf via resources defined in Identity stack, referenced_

_Loosely derived from [`KtPW`](https://git.io/fjpBs)_


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

- [ ] Deploy Identity:

```sh
Previewing update (identity):

     Type                                       Name                                     Plan
 +   pulumi:pulumi:Stack                        identity-identity                        create
 +   ├─ awsinfra:x:iam:User                     bot.networkAdminCiUser                   create
 +   │  ├─ aws:iam:User                         bot.networkAdminCiUser                   create
 +   │  ├─ aws:iam:AccessKey                    networkAdminCiUser                       create
 +   │  └─ aws:iam:UserGroupMembership          bot.networkAdminCiUser                   create
 +   ├─ awsinfra:x:iam:User                     bot.eksAdminCiUser                       create
 +   │  ├─ aws:iam:User                         bot.eksAdminCiUser                       create
 +   │  ├─ aws:iam:AccessKey                    eksAdminCiUser                           create
 +   │  └─ aws:iam:UserGroupMembership          bot.eksAdminCiUser                       create
 +   ├─ awsProd:index:BaselineIam               baselineIam                              create
 +   │  ├─ awsProd:index:BaselineIamPolicies    baselineIam                              create
 +   │  │  └─ aws:iam:Policy                    iamPass                                  create
 +   │  └─ awsProd:index:BaselineIamGroups      baselineIam                              create
 +   │     ├─ aws:iam:Group                     useExistingIamRoles                      create
 +   │     │  └─ aws:iam:GroupPolicyAttachment  useExistingIamRoles-useExistingIamRoles  create
 +   │     ├─ aws:iam:Group                     networkAdmins                            create
 +   │     │  └─ aws:iam:GroupPolicyAttachment  networkAdmins-networkAdministrator       create
 +   │     ├─ aws:iam:Group                     eksAdmins                                create
 +   │     │  └─ aws:iam:GroupPolicyAttachment  eksAdmins-administratorAccess            create
 +   │     ├─ aws:iam:Group                     billing                                  create
 +   │     │  └─ aws:iam:GroupPolicyAttachment  billing-billing                          create
 +   │     ├─ aws:iam:Group                     securityAuditors                         create
 +   │     │  └─ aws:iam:GroupPolicyAttachment  securityAuditors-securityAudit           create
 +   │     └─ aws:iam:Group                     readOnly                                 create
 +   │        └─ aws:iam:GroupPolicyAttachment  readOnly-readOnly                        create
 +   └─ aws:iam:Role                            kubeAppRole                              create
 +      ├─ aws:iam:RolePolicyAttachment         kubeAppRole-ecrPowerUser                 create
 +      └─ aws:iam:RolePolicyAttachment         kubeAppRole-passRole                     create

Resources:
    + 28 to create
```

- [ ] Once you've finished experimenting, tear down your stack's resources by destroying and removing it:

    ```bash
    $ pulumi destroy --yes
    $ pulumi stack rm --yes
    ```