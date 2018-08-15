// Copyright 2016-2018, Pulumi Corporation.  All rights reserved.

import * as helm from "@pulumi/kubernetes/helm";
import * as k8s from "@pulumi/kubernetes";
import { k8sCluster, k8sProvider } from "./cluster";

const apache = new helm.v2.Chart("apache", {
    repo: "bitnami",
    chart: "apache",
    version: "1.0.0",
}, { providers: { kubernetes: k8sProvider } });

export let cluster = k8sCluster.name;
export let kubeConfig = k8sCluster.kubeConfigRaw;
export let serviceIP =
    (apache.resources["v1/Service::default/apache-apache"] as k8s.core.v1.Service).
        spec.apply(s => s.clusterIP);
