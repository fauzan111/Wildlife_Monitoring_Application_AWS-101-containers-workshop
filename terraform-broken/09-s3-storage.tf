# S3 Storage Configuration for Wildlife Application
# NOTE: S3 bucket creation requires direct AWS API access and appropriate IAM permissions.
# In this VPC-isolated environment, S3 buckets should be created outside this Terraform
# configuration or using an IAM role with S3 permissions not restricted by VPC endpoints.

# Placeholder for future S3 configuration:
# - Wildlife data bucket for images and media with versioning and KMS encryption
# - Logs bucket for access logs with public access blocked
# - Server-side encryption and audit logging configured

# IAM Policy Attachments for Application

resource "aws_iam_role_policy_attachment" "application_data" {
	role       = data.aws_iam_role.ecs_task.name
	policy_arn = data.aws_iam_policy.application_data_policy.arn
}