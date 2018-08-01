import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

const region = aws.config.requireRegion();

const lambdaRole = new aws.iam.Role("lambdaRole", {
    assumeRolePolicy: JSON.stringify({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com",
                },
                "Effect": "Allow",
                "Sid": "",
            },
        ],
    })
});

const lambdaRolePolicy = new aws.iam.RolePolicy("lambdaRolePolicy", {
    role: lambdaRole.id,
    policy: JSON.stringify({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }]
    })
});

const sfnRole = new aws.iam.Role("sfnRole", {
    assumeRolePolicy: JSON.stringify({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": `states.${region}.amazonaws.com`
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
});

const sfnRolePolicy = new aws.iam.RolePolicy("sfnRolePolicy", {
    role: sfnRole.id,
    policy: JSON.stringify({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": "*"
            }
        ]
    })
});

const helloFunction = new aws.serverless.Function(
    "helloFunction",
    { role: lambdaRole },
    (event, context, callback) => {
        callback(null, "Hello");
    }
);

const worldFunction = new aws.serverless.Function(
  "worldFunction",
  {role: lambdaRole},
  (event, context, callback) => {
    callback(null, `${event} World!`);
  }
);

const stateMachine = new aws.sfn.StateMachine("stateMachine", {
    roleArn: sfnRole.arn,
    definition: pulumi.all([helloFunction.lambda.arn, worldFunction.lambda.arn])
      .apply(([helloArn, worldArn]) => {
      return JSON.stringify({
        "Comment": "A Hello World example of the Amazon States Language using two AWS Lambda Functions",
        "StartAt": "Hello",
        "States": {
          "Hello": {
            "Type": "Task",
            "Resource": helloArn,
            "Next": "World"
          },
          "World": {
            "Type": "Task",
            "Resource": worldArn,
            "End": true
          }
        }
      });
    })
});

exports.stateMachineArn = stateMachine.id;
